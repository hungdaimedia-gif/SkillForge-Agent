"""Distillation: raw resource text, tutorials, code or transcripts -> SkillBundle."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Optional

from .llm import LLMClient
from .models import SkillBundle, SkillMetadata

logger = logging.getLogger("skillforge.extractor")

SKILL_CONTRACT = """\
Skill code contract (STRICT):
- Single self-contained file, standard library (plus the target app's API, e.g. bpy) only.
- Read parameters as JSON from the LAST command-line argument:
    params = json.loads(sys.argv[-1]) if len(sys.argv) > 1 and sys.argv[-1].startswith("{") else {}
- Provide defaults for every parameter. Never hardcode values that a caller might want to change.
- Write ALL output files into the directory specified by env var SKILL_OUTPUT_DIR.
- Exit non-zero on failure (e.g. raise exception or sys.exit(1)).
- Print a one-line summary on success.
"""

EXTRACT_SYSTEM = f"""You convert tutorials, documentation, and transcripts into ONE atomic, executable, parameterized skill.
Inspired by Microsoft Resource2Skill distillation principles.

Reply with ONLY a valid JSON object (no surrounding explanations, no markdown fences) with keys:
  "metadata": {{
    "name": string (human-readable title),
    "taxonomy_path": string (domain/category/skill_name, lowercase [a-z0-9_-] only),
    "description": string (one-sentence purpose and applicability),
    "tags": list of strings,
    "params_schema": object (JSON-schema-like field names and types),
    "example_params": object (sensible default arguments that run headlessly),
    "runner": "python" or "blender",
    "expected_artifacts": list of globs (files created in SKILL_OUTPUT_DIR, e.g. ["out.txt", "*.blend"]),
    "expected_output": string (primary artifact filename),
    "source": string (optional source identifier or URL)
  }},
  "code": string (the complete, self-contained executable Python script)

IMPORTANT:
- taxonomy_path must use lowercase segments matching [a-z0-9_-]+.
- Make example_params and expected_artifacts such that executing the script headlessly produces verifiable files.
{SKILL_CONTRACT}"""


_STR = {"type": "string"}
BUNDLE_SCHEMA = {
    "type": "object",
    "properties": {
        "metadata": {
            "type": "object",
            "properties": {
                "name": _STR, "taxonomy_path": _STR, "description": _STR,
                "tags": {"type": "array", "items": _STR},
                # Free-form objects: JSON-encoded so the schema stays strict-compatible.
                "params_schema_json": _STR, "example_params_json": _STR,
                "runner": {"type": "string", "enum": ["python", "blender"]},
                "expected_artifacts": {"type": "array", "items": _STR},
                "expected_output": _STR, "source": _STR,
            },
            "required": ["name", "taxonomy_path", "description", "tags", "params_schema_json",
                         "example_params_json", "runner", "expected_artifacts",
                         "expected_output", "source"],
            "additionalProperties": False,
        },
        "code": _STR,
    },
    "required": ["metadata", "code"],
    "additionalProperties": False,
}


def _strip_fences(text: str) -> str:
    """Strip markdown code fences and extraneous text around JSON."""
    text = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if m:
        return m.group(1).strip()
    m2 = re.search(r"(\{.*\})", text, re.DOTALL)
    if m2:
        return m2.group(1).strip()
    return text


def parse_bundle(raw: str, source: str = "", visual_asset_path: Optional[Path | str] = None) -> SkillBundle:
    """Parse raw LLM JSON response into a validated SkillBundle."""
    cleaned = _strip_fences(raw)
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        logger.error("Failed to parse JSON bundle from LLM response: %s", exc)
        raise ValueError(f"Invalid JSON from extractor: {exc}\nRaw: {raw[:300]}") from exc

    if "metadata" not in data or "code" not in data:
        raise ValueError("Extractor JSON missing 'metadata' or 'code' key")

    meta_raw = dict(data["metadata"])
    for key in ("params_schema", "example_params"):
        encoded = meta_raw.pop(f"{key}_json", None)
        if encoded and key not in meta_raw:
            meta_raw[key] = json.loads(encoded) if isinstance(encoded, str) else encoded
    meta = SkillMetadata(**meta_raw)
    if source and not meta.source:
        meta.source = source

    return SkillBundle(
        metadata=meta,
        code_payload=data["code"],
        visual_asset_path=Path(visual_asset_path) if visual_asset_path else None,
    )


def extract_skill(
    llm: LLMClient,
    resource_text: str,
    source: str = "",
    domain_hint: str | None = None,
    visual_asset_path: Optional[Path | str] = None,
) -> SkillBundle:
    """Extract a SkillBundle from raw resource text."""
    hint = f"\nPreferred domain: {domain_hint}" if domain_hint else ""
    user_prompt = f"Resource Content:{hint}\n\n{resource_text}"
    logger.info("Extracting skill from resource (source=%s, domain=%s)", source or "inline", domain_hint)
    if hasattr(llm, "complete_json"):
        # Structured output: no regex-scraping JSON that embeds a whole script.
        data = llm.complete_json(EXTRACT_SYSTEM, user_prompt, BUNDLE_SCHEMA)
        raw = json.dumps(data)
    else:
        raw = llm.complete(EXTRACT_SYSTEM, user_prompt)
    bundle = parse_bundle(raw, source=source, visual_asset_path=visual_asset_path)
    logger.info("Successfully extracted skill: %s (%s)", bundle.metadata.name, bundle.metadata.id)
    return bundle


def extract_from_file(
    llm: LLMClient,
    path: Path,
    domain_hint: str | None = None,
    visual_asset_path: Optional[Path | str] = None,
) -> SkillBundle:
    """Read a local markdown, code, or transcript file and extract a skill."""
    logger.info("Extracting skill from file: %s", path)
    content = path.read_text(encoding="utf-8")
    return extract_skill(
        llm=llm,
        resource_text=content,
        source=str(path),
        domain_hint=domain_hint,
        visual_asset_path=visual_asset_path,
    )


def extract_from_video(
    llm: LLMClient,
    transcript: str,
    source_url: str = "",
    keyframe_paths: list[Path | str] | None = None,
    domain_hint: str | None = None,
) -> SkillBundle:
    """Multimodal Video / VLM distillation helper.

    Accepts an ingested video transcript, optional source URL, and sampled keyframe paths.
    Selects the primary representative keyframe as the visual asset.
    """
    logger.info("Extracting skill from video resource (source=%s, %d frames)",
                source_url, len(keyframe_paths or []))
    frame_context = ""
    chosen_asset: Path | None = None
    if keyframe_paths:
        frame_context = f"\nVideo Keyframe Frames Sampled: {[str(p) for p in keyframe_paths]}"
        chosen_asset = Path(keyframe_paths[0]) if keyframe_paths else None

    prompt = f"Video Source: {source_url}{frame_context}\n\nTranscript / Action Notes:\n{transcript}"
    raw = llm.complete(EXTRACT_SYSTEM, prompt)
    return parse_bundle(raw, source=source_url, visual_asset_path=chosen_asset)
