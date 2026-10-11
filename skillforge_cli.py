"""SkillForge-Agent CLI entry point: ingest, search, run, tree, serve."""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

from core.indexer import SkillWiki


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="skillforge",
        description="SkillForge-Agent: Distill tutorials into validated agent skills and serve over MCP.",
    )
    parser.add_argument(
        "--wiki",
        default=os.environ.get("SKILLFORGE_WIKI", "skills_wiki"),
        help="Path to skills wiki directory (default: env SKILLFORGE_WIKI or 'skills_wiki')",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose debug logging",
    )

    subparsers = parser.add_subparsers(dest="cmd", required=True)

    # Ingest command
    p_ingest = subparsers.add_parser("ingest", help="Distill a resource file into a validated skill")
    p_ingest.add_argument("file", type=Path, help="Path to markdown/tutorial/code/transcript file")
    p_ingest.add_argument("--domain", help="Domain hint (e.g. 'python', 'blender')")
    p_ingest.add_argument("--keep-draft", action="store_true", help="Save into wiki even if validation fails")
    p_ingest.add_argument("--max-retries", type=int, default=3, help="Max self-repair attempts (default 3)")

    # Search command
    p_search = subparsers.add_parser("search", help="Search the skills wiki")
    p_search.add_argument("query", help="Natural language query or keywords")
    p_search.add_argument("--domain", help="Filter by domain prefix (e.g. 'python')")
    p_search.add_argument("--limit", type=int, default=5, help="Max results (default 5)")

    # Run command
    p_run = subparsers.add_parser("run", help="Execute a skill with parameters")
    p_run.add_argument("skill_id", help="Canonical skill id (e.g. 'python.text.slugify')")
    p_run.add_argument("--params", default="{}", help="JSON string of parameter overrides")
    p_run.add_argument("--allow-draft", action="store_true", help="Allow executing unvalidated draft skills")
    p_run.add_argument("--docker", action="store_true", help="Force execution inside Docker container")

    # Tree command
    subparsers.add_parser("tree", help="Display the taxonomy tree of the wiki")

    # Serve command
    subparsers.add_parser("serve", help="Start the FastMCP server over stdio for Claude/MCP clients")

    args = parser.parse_args()
    setup_logging(args.verbose)

    wiki = SkillWiki(args.wiki)

    if args.cmd == "ingest":
        from core.extractor import extract_from_file
        from core.llm import AnthropicLLM
        from core.validator import validate

        llm = AnthropicLLM()
        bundle = extract_from_file(llm, args.file, domain_hint=args.domain)
        bundle, verification = asyncio.run(validate(bundle, llm=llm, max_retries=args.max_retries))

        status_str = "VALIDATED" if verification.passed else "DRAFT (FAILED)"
        print(f"\nResult: [{status_str}] attempts={verification.attempts} reason={verification.reason}")

        if verification.passed or args.keep_draft:
            saved_dir = wiki.save(bundle)
            print(f"Saved skill to: {saved_dir}")
        else:
            print("Skill was NOT saved. Pass --keep-draft to persist failing draft skills.")
            sys.exit(1)

    elif args.cmd == "search":
        hits = wiki.search(args.query, domain=args.domain, limit=args.limit)
        if not hits:
            print("No matching skills found.")
            return

        print(f"\nFound {len(hits)} skills matching '{args.query}':")
        for s in hits:
            status_tag = f"[{s.status.upper()}]"
            print(f"  {s.score:6.2f}  {s.id:<32} {status_tag:<12} {s.description}")

    elif args.cmd == "run":
        from runtime.executor import run_skill

        try:
            param_dict = json.loads(args.params)
        except json.JSONDecodeError as exc:
            print(f"Error parsing --params JSON: {exc}", file=sys.stderr)
            sys.exit(2)

        res = asyncio.run(
            run_skill(
                wiki=wiki,
                skill_id=args.skill_id,
                params=param_dict,
                allow_draft=args.allow_draft,
                use_docker=args.docker,
            )
        )
        print(res.model_dump_json(indent=2))
        if not res.success:
            sys.exit(res.return_code or 1)

    elif args.cmd == "tree":
        tree_data = wiki.tree()
        print(json.dumps(tree_data, indent=2))

    elif args.cmd == "serve":
        # Ensure wiki path is exported for runtime/mcp_server
        os.environ["SKILLFORGE_WIKI"] = str(Path(args.wiki).resolve())
        from runtime.mcp_server import main as serve_mcp
        serve_mcp()


if __name__ == "__main__":
    main()
