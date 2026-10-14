"""Skills wiki storage on disk with SQLite run stats and hybrid search."""
from __future__ import annotations

import json
import logging
import math
import re
import shutil
import sqlite3
from pathlib import Path
from typing import Callable, Optional

from .models import KnowledgeSkill, SkillBundle, SkillMetadata, SkillSummary
from .text import tokenize as _tokenize

logger = logging.getLogger("skillforge.indexer")

_SAFE_REL = re.compile(r"^[A-Za-z0-9_.\-/]+$")


class SkillWiki:
    """Manages skill persistence on disk, SQLite run telemetry, and hybrid search."""

    def __init__(self, root: Path | str = "skills_wiki"):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self._db_path = self.root / ".stats.sqlite"
        self._meta_cache: tuple[tuple[int, int], list[SkillMetadata]] | None = None
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

        self._meta_cache = None
        logger.info("Saved skill '%s' to %s", bundle.metadata.id, d)
        return d

    def save_knowledge(self, skill: KnowledgeSkill, status: str = "draft",
                       eval_score: float | None = None, gate_issues: list[str] | None = None) -> Path:
        """Save a knowledge skill: SKILL.md + references/ + assets/ + SOURCES.md + skill.json."""
        taxonomy = f"{skill.domain}/{skill.plan.category}/{skill.plan.name.replace('-', '_')}"
        meta = SkillMetadata(
            name=skill.plan.title,
            taxonomy_path=taxonomy,
            description=skill.plan.description,
            tags=sorted({skill.domain, skill.plan.category, *skill.plan.name.split("-")}),
            runner="none",
            kind="knowledge",
            skill_name=skill.plan.name,
            status=status,  # type: ignore[arg-type]
            license=skill.license,
            sources=skill.sources,
            source=skill.sources[0] if skill.sources else "",
            eval_score=eval_score,
            gate_issues=gate_issues or [],
        )
        d = self._dir(meta.id)
        d.mkdir(parents=True, exist_ok=True)
        (d / "SKILL.md").write_text(skill.skill_md(), encoding="utf-8")
        if skill.sources_md:
            (d / "SOURCES.md").write_text(skill.sources_md, encoding="utf-8")
        for rel, content in skill.references.items():
            target = self._child(d, rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        for rel, src in skill.assets.items():
            target = self._child(d, rel)
            target.parent.mkdir(parents=True, exist_ok=True)
            if Path(src).exists():
                shutil.copy(src, target)
        if skill.quiz:
            (d / "quiz.json").write_text(
                json.dumps([q.model_dump() for q in skill.quiz], ensure_ascii=False, indent=2),
                encoding="utf-8")
        (d / "skill.json").write_text(meta.model_dump_json(indent=2), encoding="utf-8")
        self._meta_cache = None
        logger.info("Saved knowledge skill '%s' to %s", meta.id, d)
        return d

    @staticmethod
    def _child(base: Path, rel: str) -> Path:
        """Resolve a relative file inside a skill dir, rejecting traversal."""
        if not rel or not _SAFE_REL.match(rel) or ".." in rel.split("/"):
            raise ValueError(f"Unsafe relative path: {rel!r}")
        target = (base / rel).resolve()
        target.relative_to(base.resolve())
        return target

    def read_file(self, skill_id: str, rel: str = "SKILL.md") -> str:
        """Read a text file inside a skill (SKILL.md, references/x.md, SOURCES.md...)."""
        return self._child(self._dir(skill_id), rel).read_text(encoding="utf-8")

    def list_files(self, skill_id: str) -> list[str]:
        d = self._dir(skill_id)
        return sorted(p.relative_to(d).as_posix() for p in d.rglob("*")
                      if p.is_file() and not p.name.startswith("."))

    def load(self, skill_id: str) -> SkillBundle:
        """Load a skill bundle from the wiki. Knowledge skills carry SKILL.md as payload."""
        d = self._dir(skill_id)
        meta_path = d / "skill.json"
        code_path = d / "run.py"

        if not meta_path.exists():
            raise KeyError(f"Skill not found: {skill_id}")
        meta = SkillMetadata.model_validate_json(meta_path.read_text(encoding="utf-8"))
        if meta.kind == "knowledge":
            skill_md = d / "SKILL.md"
            code = skill_md.read_text(encoding="utf-8") if skill_md.exists() else ""
        elif code_path.exists():
            code = code_path.read_text(encoding="utf-8")
        else:
            raise KeyError(f"Skill not found: {skill_id}")

        # Discover visual asset if present
        asset = next(iter(sorted(d.glob("asset.*"))), None)
        return SkillBundle(metadata=meta, code_payload=code, visual_asset_path=asset)

    def all_metadata(self) -> list[SkillMetadata]:
        """Scan wiki directory and return metadata of all stored skills.

        Cached and invalidated by the newest skill.json mtime, so a search no
        longer re-parses every file on each query.
        """
        files = sorted(self.root.rglob("skill.json"))
        stamp = (len(files), max((f.stat().st_mtime_ns for f in files), default=0))
        if self._meta_cache is not None and self._meta_cache[0] == stamp:
            return list(self._meta_cache[1])
        out: list[SkillMetadata] = []
        for f in files:
            try:
                out.append(SkillMetadata.model_validate_json(f.read_text(encoding="utf-8")))
            except Exception as exc:
                logger.warning("Failed parsing %s: %s", f, exc)
                continue
        self._meta_cache = (stamp, out)
        return list(out)

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

    def _all_reliability(self) -> dict[str, float]:
        """One query for every skill instead of one connection per skill per search."""
        with self._get_db() as conn:
            rows = conn.execute("SELECT id, runs, ok FROM stats WHERE runs > 0").fetchall()
        return {r["id"]: (r["ok"] / r["runs"]) * math.log1p(r["runs"]) for r in rows}

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
        reliability_by_id = self._all_reliability()

        for m in self.all_metadata():
            if domain and m.domain != domain:
                continue
            if prefix and not m.taxonomy_path.startswith(prefix):
                continue

            base_score = scorer(q_tokens, m) if q_tokens else 0.1
            if base_score <= 0:
                continue

            # Reliability bonus from past successful runs + validation boost
            reliability = reliability_by_id.get(m.id, 0.0)
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
                    kind=m.kind,
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
