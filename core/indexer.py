"""Skills wiki storage on disk with SQLite run stats and hybrid search."""
from __future__ import annotations

import logging
import math
import re
import shutil
import sqlite3
from pathlib import Path
from typing import Callable, Optional

from .models import SkillBundle, SkillMetadata, SkillSummary

logger = logging.getLogger("skillforge.indexer")

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    """Extract lowercase alphanumeric tokens."""
    return _TOKEN_RE.findall(text.lower())


class SkillWiki:
    """Manages skill persistence on disk, SQLite run telemetry, and hybrid search."""

    def __init__(self, root: Path | str = "skills_wiki"):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self._db_path = self.root / ".stats.sqlite"
        self._init_db()

    def _get_db(self) -> sqlite3.Connection:
        """Thread-safe SQLite connection."""
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._get_db() as conn:
            conn.execute(
                """CREATE TABLE IF NOT EXISTS stats (
                    id TEXT PRIMARY KEY,
                    runs INTEGER DEFAULT 0,
                    ok INTEGER DEFAULT 0
                )"""
            )

    # ---- storage & path security ---------------------------------------
    def _dir(self, skill_id: str) -> Path:
        """Resolve skill storage directory with strict path-traversal rejection."""
        if not skill_id or ".." in skill_id or skill_id.startswith("/") or skill_id.startswith("\\"):
            raise ValueError(f"Invalid or unsafe skill_id: {skill_id!r}")

        rel_path = skill_id.replace(".", "/")
        target = (self.root / rel_path).resolve()

        # Reject path escaping wiki root
        try:
            target.relative_to(self.root)
        except ValueError as exc:
            raise ValueError(f"Path traversal detected for skill_id: {skill_id!r}") from exc

        return target

    def save(self, bundle: SkillBundle) -> Path:
        """Save a skill bundle into the wiki."""
        d = self._dir(bundle.metadata.id)
        d.mkdir(parents=True, exist_ok=True)

        meta_path = d / "skill.json"
        meta_path.write_text(bundle.metadata.model_dump_json(indent=2), encoding="utf-8")

        code_path = d / "run.py"
        code_path.write_text(bundle.code_payload, encoding="utf-8")

        if bundle.visual_asset_path:
            src = Path(bundle.visual_asset_path)
            if src.exists():
                ext = src.suffix or ".png"
                shutil.copy(src, d / f"asset{ext}")

        logger.info("Saved skill '%s' to %s", bundle.metadata.id, d)
        return d

    def load(self, skill_id: str) -> SkillBundle:
        """Load a skill bundle from the wiki."""
        d = self._dir(skill_id)
        meta_path = d / "skill.json"
        code_path = d / "run.py"

        if not meta_path.exists() or not code_path.exists():
            raise KeyError(f"Skill not found: {skill_id}")

        meta = SkillMetadata.model_validate_json(meta_path.read_text(encoding="utf-8"))
        code = code_path.read_text(encoding="utf-8")

        # Discover visual asset if present
        asset = next(iter(sorted(d.glob("asset.*"))), None)
        return SkillBundle(metadata=meta, code_payload=code, visual_asset_path=asset)

    def all_metadata(self) -> list[SkillMetadata]:
        """Scan wiki directory and return metadata of all stored skills."""
        out: list[SkillMetadata] = []
        for f in sorted(self.root.rglob("skill.json")):
            try:
                out.append(SkillMetadata.model_validate_json(f.read_text(encoding="utf-8")))
            except Exception as exc:
                logger.warning("Failed parsing %s: %s", f, exc)
                continue
        return out

    # ---- execution telemetry -------------------------------------------
    def record_run(self, skill_id: str, ok: bool) -> None:
        """Record run outcome in SQLite."""
        with self._get_db() as conn:
            conn.execute("INSERT OR IGNORE INTO stats (id, runs, ok) VALUES (?, 0, 0)", (skill_id,))
            conn.execute(
                "UPDATE stats SET runs = runs + 1, ok = ok + ? WHERE id = ?",
                (1 if ok else 0, skill_id),
            )

    def _reliability(self, skill_id: str) -> float:
        """Calculate historical reliability boost: (ok / runs) * log1p(runs)."""
        with self._get_db() as conn:
            row = conn.execute("SELECT runs, ok FROM stats WHERE id = ?", (skill_id,)).fetchone()
            if not row or row["runs"] == 0:
                return 0.0
            runs, ok = row["runs"], row["ok"]
            return (ok / runs) * math.log1p(runs)

    # ---- hybrid search -------------------------------------------------
    @staticmethod
    def default_lexical_scorer(query_tokens: list[str], m: SkillMetadata) -> float:
        """Weighted lexical score based on field relevance."""
        fields = [
            (m.name, 3.0),
            (" ".join(m.tags), 2.0),
            (m.description, 1.0),
            (m.taxonomy_path.replace("/", " "), 1.5),
        ]
        score = 0.0
        for text, weight in fields:
            toks = set(_tokenize(text))
            score += weight * sum(1 for t in query_tokens if t in toks)
        return score

    def search(
        self,
        query: str,
        domain: str | None = None,
        prefix: str | None = None,
        limit: int = 5,
        custom_scorer: Optional[Callable[[list[str], SkillMetadata], float]] = None,
    ) -> list[SkillSummary]:
        """Hybrid search: taxonomy filter + scoring + reliability boost.

        `custom_scorer` is swappable for embedding similarity.
        """
        q_tokens = _tokenize(query)
        scorer = custom_scorer or self.default_lexical_scorer
        results: list[SkillSummary] = []

        for m in self.all_metadata():
            if domain and m.domain != domain:
                continue
            if prefix and not m.taxonomy_path.startswith(prefix):
                continue

            base_score = scorer(q_tokens, m) if q_tokens else 0.1
            if base_score <= 0:
                continue

            # Reliability bonus from past successful runs + validation boost
            reliability = self._reliability(m.id)
            status_boost = 0.5 if m.status == "validated" else 0.0
            total_score = base_score + reliability + status_boost

            results.append(
                SkillSummary(
                    id=m.id,
                    name=m.name,
                    taxonomy_path=m.taxonomy_path,
                    description=m.description,
                    tags=m.tags,
                    status=m.status,
                    score=round(total_score, 3),
                )
            )

        return sorted(results, key=lambda s: s.score, reverse=True)[:limit]

    def tree(self) -> dict:
        """Browseable nested dictionary taxonomy tree."""
        tree_dict: dict = {}
        for m in self.all_metadata():
            curr = tree_dict
            parts = m.taxonomy_path.split("/")
            for p in parts:
                curr = curr.setdefault(p, {})
        return tree_dict
