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
    runner: Literal["python", "blender"] = "python"
    expected_artifacts: list[str] = Field(default_factory=list)  # globs inside output dir
    expected_output: str = ""
    source: str = ""
    status: Literal["draft", "validated"] = "draft"
    timeout_s: int = 120

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
