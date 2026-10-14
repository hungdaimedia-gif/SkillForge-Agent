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


def export_skills(wiki: SkillWiki, selector: str, dest: Path, include_drafts: bool = False) -> list[Path]:
    """Copy knowledge skills to dest/<skill_name>/ (SKILL.md, references/, assets/, SOURCES.md).

    Never overwrites: an existing destination folder is skipped and reported,
    so a hand-edited skill in the target library cannot be clobbered.
    """
    import shutil

    metas = [m for m in wiki.all_metadata() if m.kind == "knowledge"
             and (m.id == selector or m.domain == selector or m.id.startswith(selector + "."))]
    out: list[Path] = []
    for m in metas:
        if m.status != "validated" and not include_drafts:
            print(f"skip  {m.id} (status {m.status}; use --include-drafts)")
            continue
        src = wiki._dir(m.id)
        target = dest / (m.skill_name or m.id.split(".")[-1])
        if target.exists():
            print(f"exists {target} — not overwritten (remove or rename it yourself to re-export)")
            continue
        target.mkdir(parents=True)
        for rel in wiki.list_files(m.id):
            if rel in ("skill.json", "quiz.json", "eval.json"):
                continue
            (target / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(src / rel, target / rel)
        print(f"ok    {m.id} -> {target}")
        out.append(target)
    return out


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

    # Fetch command (no LLM): cache transcripts/frames/book text
    p_fetch = subparsers.add_parser("fetch", help="Download & cache sources (YouTube video/playlist, PDF/EPUB/MD) without any LLM call")
    p_fetch.add_argument("target", help="YouTube URL (video/playlist/channel) or book file")
    p_fetch.add_argument("--cache", default=os.environ.get("SKILLFORGE_CACHE", "sources_cache"))
    p_fetch.add_argument("--lang", default="en", help="Transcript language (default en)")
    p_fetch.add_argument("--max-frames", type=int, default=24, help="Max keyframes per video")
    p_fetch.add_argument("--no-frames", action="store_true", help="Transcript only")
    p_fetch.add_argument("--limit", type=int, help="Only the first N videos")

    # Distill command: sources -> knowledge skills (SKILL.md)
    p_distill = subparsers.add_parser("distill", help="Distill videos/books into offline knowledge skills (SKILL.md)")
    p_distill.add_argument("targets", nargs="+", help="YouTube URLs and/or book files (one collection)")
    p_distill.add_argument("--domain", required=True, help="Skill domain / name prefix, e.g. 'cascadeur'")
    p_distill.add_argument("--lang", default="vi", help="Language of the written skills (default vi)")
    p_distill.add_argument("--source-lang", default="en", help="Transcript language to fetch (default en)")
    p_distill.add_argument("--cache", default=os.environ.get("SKILLFORGE_CACHE", "sources_cache"))
    p_distill.add_argument("--work", default=os.environ.get("SKILLFORGE_WORK", "work"),
                           help="Resumable intermediate results (units, plan, drafts)")
    p_distill.add_argument("--max-frames", type=int, default=24)
    p_distill.add_argument("--limit", type=int, help="Only the first N videos of a playlist")
    p_distill.add_argument("--workers", type=int, default=4, help="Parallel LLM calls")
    p_distill.add_argument("--no-eval", action="store_true", help="Skip the closed-book quiz")
    p_distill.add_argument("--min-eval", type=float, default=0.7, help="Quiz score needed for 'validated'")
    p_distill.add_argument("--force", action="store_true", help="Ignore cached units/plan/skills")
    p_distill.add_argument("--redo", action="append", default=[], metavar="NAME",
                           help="Rewrite only this skill (repeatable); 'plan' re-plans the skill list")
    p_distill.add_argument("--llm", choices=["auto", "api", "claude-cli"], default=None,
                           help="LLM backend (default env SKILLFORGE_LLM or auto)")
    p_distill.add_argument("--model", help="Model id/alias for the chosen backend")

    # Export command: copy knowledge skills into an agent's skills folder
    p_export = subparsers.add_parser("export", help="Copy knowledge skills into a skills folder (e.g. .claude/skills)")
    p_export.add_argument("selector", help="Skill id (cascadeur.timeline.x) or a domain (cascadeur)")
    p_export.add_argument("--to", required=True, type=Path, help="Destination skills directory")
    p_export.add_argument("--include-drafts", action="store_true")

    # Tree command
    subparsers.add_parser("tree", help="Display the taxonomy tree of the wiki")

    # Serve command
    subparsers.add_parser("serve", help="Start the FastMCP server over stdio for Claude/MCP clients")

    args = parser.parse_args()
    setup_logging(args.verbose)

    wiki = SkillWiki(args.wiki)

    if args.cmd == "ingest":
        from core.extractor import extract_from_file
        from core.llm import get_llm
        from core.validator import validate

        llm = get_llm()
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

    elif args.cmd == "fetch":
        from core.sources import acquire

        docs = acquire(args.target, cache_dir=args.cache, lang=args.lang,
                       max_frames=args.max_frames, frames=not args.no_frames, limit=args.limit)
        for i, d in enumerate(docs, start=1):
            chars = sum(len(s.text) for sec in d.sections for s in sec.segments)
            frames = sum(len(sec.frames) for sec in d.sections)
            print(f"S{i:<3} {d.doc_id:<14} {d.transcript_source:<16} chars={chars:<6} "
                  f"frames={frames:<3} {d.title}")
        print(f"\nCached under: {Path(args.cache).resolve()}")

    elif args.cmd == "distill":
        from core.distill import distill
        from core.llm import get_llm
        from core.sources import acquire

        docs = []
        for target in args.targets:
            docs += acquire(target, cache_dir=args.cache, lang=args.source_lang,
                            max_frames=args.max_frames, limit=args.limit)
        print(f"Đã có {len(docs)} nguồn trong cache. Bắt đầu chưng cất ...")
        llm = get_llm(args.llm, args.model)
        report = distill(docs, llm, wiki, domain=args.domain, work_dir=args.work, lang=args.lang,
                         workers=args.workers, run_eval=not args.no_eval,
                         min_eval=args.min_eval, force=args.force, redo=args.redo)
        print("\n" + report.to_markdown())
        if not any(s.status == "validated" for s in report.skills):
            sys.exit(1)

    elif args.cmd == "export":
        exported = export_skills(wiki, args.selector, args.to, args.include_drafts)
        if not exported:
            print("Nothing exported.")
            sys.exit(1)

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
