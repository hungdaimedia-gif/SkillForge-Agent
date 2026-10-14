"""Data contracts shared across all SkillForge-Agent layers."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, field_validator

_SEGMENT = re.compile(r"^[a-z0-9_-]+$")


class SkillMetadata(BaseModel):
    name: str
    taxonomy_path: str  # e.g. "blender/lighting/three_point" (domain/category/.../skill)
    description: str
    tags: list[str] = Field(default_factory=list)
    params_schema: dict[str, Any] = Field(default_factory=dict)  # JSON-schema-like
    example_params: dict[str, Any] = Field(default_factory=dict)  # used by the validator
    runner: Literal["python", "blender", "none"] = "python"
    expected_artifacts: list[str] = Field(default_factory=list)  # globs inside output dir
    expected_output: str = ""
    source: str = ""
    status: Literal["draft", "validated"] = "draft"
    timeout_s: int = 120
    # --- added for knowledge skills (optional, so old skill.json files still load) ---
    # "executable": run.py + sandbox validation. "knowledge": SKILL.md an agent reads offline.
    kind: Literal["executable", "knowledge"] = "executable"
    skill_name: str = ""  # SKILL.md frontmatter name (kebab-case)
    license: str = ""  # e.g. "youtube_review_pending", "book_paraphrase_only", "mit"
    sources: list[str] = Field(default_factory=list)  # URLs / file paths the skill was distilled from
    eval_score: Optional[float] = None  # offline quiz score in [0, 1]
    gate_issues: list[str] = Field(default_factory=list)

    @field_validator("taxonomy_path")
    @classmethod
    def _check_path(cls, v: str) -> str:
        parts = v.strip("/").split("/")
        if len(parts) < 2 or not all(_SEGMENT.match(p) for p in parts):
            raise ValueError(
                "taxonomy_path must be 'domain/category/.../skill' with lowercase [a-z0-9_-] segments only"
            )
        return "/".join(parts)

    @property
    def id(self) -> str:
        """Returns the canonical dot-separated identifier, e.g. python.text.slugify."""
        return self.taxonomy_path.replace("/", ".")

    @property
    def domain(self) -> str:
        """Returns top-level domain segment, e.g. 'python' or 'blender'."""
        return self.taxonomy_path.split("/")[0]

    @property
    def category(self) -> str:
        """Returns the category segment if present, e.g. 'lighting' or 'text'."""
        parts = self.taxonomy_path.split("/")
        return parts[1] if len(parts) > 1 else ""


class SkillBundle(BaseModel):
    metadata: SkillMetadata
    code_payload: str
    visual_asset_path: Optional[Path | str] = None


class SkillSummary(BaseModel):
    id: str
    name: str
    taxonomy_path: str
    description: str
    tags: list[str]
    status: str
    score: float = 0.0
    kind: str = "executable"


class ExecutionResult(BaseModel):
    success: bool
    return_code: int
    stdout: str = ""
    stderr: str = ""
    output_artifacts: list[str] = Field(default_factory=list)
    run_dir: str = ""


class VerificationResult(BaseModel):
    passed: bool
    attempts: int
    history: list[ExecutionResult] = Field(default_factory=list)
    reason: str = ""


# ---------------------------------------------------------------------------
# Source documents (video / book) with anchors back to the original
# ---------------------------------------------------------------------------

class Segment(BaseModel):
    """One span of source text. `anchor` is '1:23' for video, 'p.87' for books."""
    anchor: str
    text: str
    start_s: Optional[float] = None  # video only
    end_s: Optional[float] = None


class Frame(BaseModel):
    """A keyframe sampled from a video, stored on disk."""
    frame_id: str  # e.g. "f0007"
    path: str
    t_s: float
    reason: str = ""  # "chapter", "uniform", ...


class SourceSection(BaseModel):
    """A chapter of a book or a (chapter of a) video: the unit fed to one map call."""
    section_id: str
    title: str
    segments: list[Segment] = Field(default_factory=list)
    frames: list[Frame] = Field(default_factory=list)

    def char_len(self) -> int:
        return sum(len(s.text) for s in self.segments)


class SourceDoc(BaseModel):
    doc_id: str  # stable: youtube video id, or slug+hash of the book file
    kind: Literal["youtube", "book", "text"]
    title: str
    url: str = ""  # watch URL or absolute file path
    author: str = ""
    license: str = ""
    language: str = ""
    transcript_source: str = ""  # "manual_subs", "auto_subs", "whisper", "pdf", ...
    sections: list[SourceSection] = Field(default_factory=list)
    extras: dict[str, Any] = Field(default_factory=dict)

    def anchor_url(self, anchor: str) -> str:
        """Deep link for an anchor (YouTube &t=), else the plain url."""
        if self.kind == "youtube" and self.url:
            from .text import parse_ts

            secs = parse_ts(anchor)
            if secs is not None:
                return f"{self.url}&t={int(secs)}s"
        return self.url


# ---------------------------------------------------------------------------
# Knowledge distillation
# ---------------------------------------------------------------------------

UnitKind = Literal["procedure", "concept", "shortcut", "setting", "heuristic", "pitfall", "example"]


class KnowledgeUnit(BaseModel):
    """Atomic, cited piece of knowledge extracted from one source section."""
    unit_id: str
    source_key: str  # "S3" -> SourceDoc via the collection's source map
    kind: UnitKind
    title: str
    content: str
    steps: list[str] = Field(default_factory=list)
    ui_terms: list[str] = Field(default_factory=list)  # verbatim labels / hotkeys
    anchors: list[str] = Field(default_factory=list)
    frames: list[str] = Field(default_factory=list)  # frame paths backing this unit
    confidence: Literal["high", "medium", "low"] = "high"


class SkillPlanItem(BaseModel):
    name: str  # kebab-case SKILL.md name
    title: str
    category: str
    description: str  # trigger description ("Use when ...")
    unit_ids: list[str]
    is_hub: bool = False
    rationale: str = ""


class QuizItem(BaseModel):
    question: str
    answer: str
    anchors: list[str] = Field(default_factory=list)


class KnowledgeSkill(BaseModel):
    """A written knowledge skill, ready for gates and saving."""
    plan: SkillPlanItem
    domain: str
    body: str  # SKILL.md without frontmatter
    references: dict[str, str] = Field(default_factory=dict)  # "references/x.md" -> content
    assets: dict[str, str] = Field(default_factory=dict)  # "assets/f0007.jpg" -> source path
    sources_md: str = ""
    quiz: list[QuizItem] = Field(default_factory=list)
    license: str = ""
    sources: list[str] = Field(default_factory=list)

    def skill_md(self) -> str:
        desc = self.plan.description.replace("\n", " ").strip()
        return f"---\nname: {self.plan.name}\ndescription: {desc}\n---\n\n{self.body.strip()}\n"
