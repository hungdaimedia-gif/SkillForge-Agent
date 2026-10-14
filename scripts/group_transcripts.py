"""Group cached Cascadeur transcripts by catalogue category for manual distillation.

Usage (from repo root): .venv/Scripts/python.exe scripts/group_transcripts.py . work/cascadeur_manual/transcripts
Writes <out_dir>/<category>.txt and <out_dir>/sources.json (K-number -> video).
K-numbers follow manifests/cascadeur_tutor.urls then cascadeur_channel_extra.urls, so they
stay stable across runs. Videos not fetched yet show "(not fetched)".
"""
import json
import re
import sys
from pathlib import Path

repo, out = Path(sys.argv[1]), Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
rows = []
for manifest in ("cascadeur_tutor.urls", "cascadeur_channel_extra.urls"):
    for line in (repo / "manifests" / manifest).read_text(encoding="utf-8").splitlines():
        if not line.startswith("http"):
            continue
        url, _, meta = line.partition("#")
        vid = re.search(r"v=([\w-]{11})", url).group(1)
        parts = [p.strip() for p in meta.split("|")]
        if manifest == "cascadeur_tutor.urls":
            cat, lvl, dur, slug, title = parts[0], parts[1], parts[2], parts[3], " | ".join(parts[4:])
        else:
            cat, lvl, dur, slug, title = "Extra (channel)", "?", parts[0], vid, " | ".join(parts[1:])
        rows.append({"vid": vid, "cat": cat, "lvl": lvl, "dur": dur, "slug": slug, "title": title, "url": url.strip()})

sources = {}
groups: dict[str, list[str]] = {}
for i, r in enumerate(rows, start=1):
    key = f"K{i}"
    sources[key] = r
    doc_file = repo / "sources_cache" / "youtube" / r["vid"] / "doc.json"
    text = "(not fetched)"
    if doc_file.exists():
        doc = json.loads(doc_file.read_text(encoding="utf-8"))
        segs = [s for sec in doc["sections"] for s in sec["segments"]]
        r["transcript_source"] = doc.get("transcript_source")
        r["chars"] = sum(len(s["text"]) for s in segs)
        chapters = [c for c in json.loads((doc_file.parent / "info.json").read_text(encoding="utf-8")).get("chapters") or []]
        chap = " · ".join(f"{int(c['start_time'])//60}:{int(c['start_time'])%60:02d} {c.get('title','')}" for c in chapters)
        text = (f"chapters: {chap}\n" if chap else "") + "\n".join(f"[{s['anchor']}] {s['text']}" for s in segs)
    primary = r["cat"].split(",")[0].strip()
    groups.setdefault(primary, []).append(
        f"### {key} | {r['title']} | {r['dur']} | {r['lvl']} | cats: {r['cat']} | {r['url']}\n{text}\n")

for cat, blocks in groups.items():
    name = re.sub(r"[^a-z0-9]+", "_", cat.lower()).strip("_")
    (out / f"{name}.txt").write_text("\n".join(blocks), encoding="utf-8")
(out / "sources.json").write_text(json.dumps(sources, ensure_ascii=False, indent=1), encoding="utf-8")
for cat, blocks in groups.items():
    print(f"{cat:28s} {len(blocks):3d} videos  {sum(len(b) for b in blocks):7d} chars")
