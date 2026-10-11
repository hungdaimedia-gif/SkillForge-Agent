"""FastMCP server exposing SkillForge skills wiki and runtime execution tools."""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from core.indexer import SkillWiki
from runtime.executor import run_skill as _run_skill

logger = logging.getLogger("skillforge.mcp")

mcp = FastMCP("skillforge")


def get_wiki() -> SkillWiki:
    """Retrieve or construct the SkillWiki instance."""
    wiki_path = Path(os.environ.get("SKILLFORGE_WIKI", "skills_wiki"))
    return SkillWiki(wiki_path)


@mcp.tool()
def search_skills(query: str, domain: str | None = None, limit: int = 5) -> list[dict[str, Any]]:
    """Search for skills by natural-language query and domain filter.

    Returns ranked list of skill summaries scored by relevance and historical reliability.
    """
    wiki = get_wiki()
    results = wiki.search(query=query, domain=domain, limit=limit)
    return [s.model_dump() for s in results]


@mcp.tool()
def browse_taxonomy() -> dict[str, Any]:
    """Browse the domain/category taxonomy tree of all available skills in the wiki."""
    wiki = get_wiki()
    return wiki.tree()


@mcp.tool()
def get_skill_details(skill_id: str) -> dict[str, Any]:
    """Retrieve complete metadata, parameter schema, and source code of a skill."""
    wiki = get_wiki()
    try:
        bundle = wiki.load(skill_id)
        return {
            "success": True,
            "metadata": bundle.metadata.model_dump(),
            "code": bundle.code_payload,
            "visual_asset": str(bundle.visual_asset_path) if bundle.visual_asset_path else None,
        }
    except Exception as exc:
        logger.error("Error retrieving skill '%s': %s", skill_id, exc)
        return {"success": False, "error": str(exc), "skill_id": skill_id}


@mcp.tool()
async def run_skill(
    skill_id: str,
    parameters: dict[str, Any] | None = None,
    allow_draft: bool = False,
) -> dict[str, Any]:
    """Execute a skill with parameters.

    Draft skills are rejected unless allow_draft=True. Defaults are merged from example_params.
    """
    wiki = get_wiki()
    try:
        result = await _run_skill(
            wiki=wiki,
            skill_id=skill_id,
            params=parameters,
            allow_draft=allow_draft,
        )
        return result.model_dump()
    except Exception as exc:
        logger.error("Failed running skill '%s': %s", skill_id, exc)
        return {
            "success": False,
            "return_code": 1,
            "stdout": "",
            "stderr": str(exc),
            "output_artifacts": [],
            "run_dir": "",
        }


@mcp.tool()
async def run_chain(
    steps: list[dict[str, Any]],
    allow_draft: bool = False,
) -> list[dict[str, Any]]:
    """Execute a sequence of skills [{skill_id, parameters}, ...], stopping at the first failure."""
    wiki = get_wiki()
    history: list[dict[str, Any]] = []

    for i, step in enumerate(steps):
        skill_id = step.get("skill_id", "")
        params = step.get("parameters")
        logger.info("Executing chain step %d/%d: %s", i + 1, len(steps), skill_id)

        try:
            res = await _run_skill(
                wiki=wiki,
                skill_id=skill_id,
                params=params,
                allow_draft=allow_draft,
            )
            step_record = {"step": i + 1, "skill_id": skill_id, **res.model_dump()}
        except Exception as exc:
            step_record = {
                "step": i + 1,
                "skill_id": skill_id,
                "success": False,
                "return_code": 1,
                "stderr": str(exc),
                "output_artifacts": [],
            }

        history.append(step_record)
        if not step_record.get("success"):
            logger.warning("Chain stopped at step %d (%s) due to failure", i + 1, skill_id)
            break

    return history


def main() -> None:
    """Run FastMCP server over stdio."""
    logging.basicConfig(level=logging.INFO)
    mcp.run()


if __name__ == "__main__":
    main()
