"""Gate for manually distilled knowledge files: every citation must point at a real video and time.

Usage (from repo root):
  .venv/Scripts/python.exe scripts/check_knowledge.py <skill_dir> <transcripts_dir>/sources.json

Checks every *.md under <skill_dir>:
  - citations look like [K12 3:45] or [K12 3:45, 7:10]; K must exist in sources.json
  - each time must be inside the video's duration (+5 s)
  - links to references/*.md resolve; SKILL.md has name + description frontmatter
  - prints, per file, how many citations it has (0 citations = error)
Also prints which K-sources are never cited (coverage). Exit 1 on any error.
"""
import json
import re
import sys
from pathlib import Path

CIT = re.compile(r"\[(K\d+)\s+([^\]\[]+?)\]")
LINK = re.compile(r"\]\(((?:references/)?[A-Za-z0-9_.\-]+\.md)\)")


def secs(t: str) -> float | None:
    try:
        n = 0.0
        for p in t.strip().split(":"):
            n = n * 60 + float(p)
        return n
    except ValueError:
        return None


def main() -> int:
    skill_dir, sources_file = Path(sys.argv[1]), Path(sys.argv[2])
    sources = json.loads(sources_file.read_text(encoding="utf-8"))
    dur = {k: secs(v["dur"]) or 0 for k, v in sources.items()}
    errors, cited = [], set()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        errors.append("missing SKILL.md")
    else:
        head = skill_md.read_text(encoding="utf-8").replace("\r\n", "\n")
        m = re.match(r"^---\nname: ([a-z0-9-]+)\ndescription: (.+?)\n---\n", head, re.S)
        if not m:
            errors.append("SKILL.md: frontmatter must be ---/name/description/---")
        elif m.group(1) != skill_dir.name:
            errors.append(f"SKILL.md: name '{m.group(1)}' != folder '{skill_dir.name}'")
    for md in sorted(skill_dir.rglob("*.md")):
        text = md.read_text(encoding="utf-8")
        n = 0
        for key, times in CIT.findall(text):
            times = times.split('"')[0].strip()  # [K12 3:45 "quote"] → 3:45
            n += 1
            if key not in sources:
                errors.append(f"{md.name}: unknown source [{key} {times}]")
                continue
            cited.add(key)
            for t in times.split(","):
                s = secs(t)
                if s is None or s < 0 or (dur[key] and s > dur[key] + 5):
                    errors.append(f"{md.name}: bad time [{key} {t.strip()}] (video is {sources[key]['dur']})")
        for link in LINK.findall(text):
            target = (md.parent / link) if not link.startswith("references/") else (skill_dir / link)
            if not target.exists():
                errors.append(f"{md.name}: broken link {link}")
        rel = md.relative_to(skill_dir)
        print(f"{n:4d} citations  {rel}")
        if n == 0 and md.name != "SOURCES.md":
            errors.append(f"{rel}: no citations")
    missing = [k for k in sources if k not in cited]
    print(f"\ncoverage: {len(cited)}/{len(sources)} videos cited")
    if missing:
        print("never cited:", ", ".join(f"{k}({sources[k]['slug']})" for k in missing))
    if errors:
        print(f"\n❌ {len(errors)} error(s):")
        for e in errors:
            print("  -", e)
        return 1
    print("\n✅ OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
