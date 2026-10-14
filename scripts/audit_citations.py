"""Print every cited sentence next to the real transcript around its timestamp, for human/agent review.

check_knowledge.py only proves a citation's time EXISTS; it cannot tell whether the transcript
there says what the sentence claims. In the first Cascadeur run 5 of 10 sampled citations did
not (invented hotkeys, menus, advice) — this script makes that review systematic.

Usage (from repo root):
  .venv/Scripts/python.exe scripts/audit_citations.py <skill_dir> <transcripts_dir>/sources.json <out.md> [--window 25]

Writes <out.md>: one block per cited line with the transcript text from (t - window) to
(t + window/2) for each cited time. Lines citing a video WITHOUT transcript are flagged
"NO TRANSCRIPT" — such citations are unverifiable and must be removed.
"""
import argparse
import json
import re
from pathlib import Path

CIT = re.compile(r"\[(K\d+)\s+([^\]\[]+?)\]")


def secs(t: str):
    try:
        n = 0.0
        for p in t.strip().split(":"):
            n = n * 60 + float(p)
        return n
    except ValueError:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("skill_dir", type=Path)
    ap.add_argument("sources", type=Path)
    ap.add_argument("out", type=Path)
    ap.add_argument("--window", type=float, default=25)
    ap.add_argument("--strict", action="store_true",
                    help="fail when a `code` or **bold** term of a cited line is absent from every cited window")
    a = ap.parse_args()
    if hasattr(__import__("sys").stdout, "reconfigure"):
        __import__("sys").stdout.reconfigure(encoding="utf-8", errors="replace")
    sources =json.loads(a.sources.read_text(encoding="utf-8"))
    cache = a.sources.resolve().parents[3] / "sources_cache" / "youtube"
    segs_by_key = {}
    for k, v in sources.items():
        f = cache / v["vid"] / "doc.json"
        segs_by_key[k] = ([s for sec in json.loads(f.read_text(encoding="utf-8"))["sections"]
                           for s in sec["segments"]] if f.exists() else [])
    out, n_lines, n_empty = ["# Soát trích dẫn", "",
                             "Mỗi khối: câu trong skill → lời thoại thật quanh mốc. Ghi kết luận vào cột cuối:",
                             "✅ khớp · ✏️ sửa câu cho đúng nguồn · 🔁 đổi mốc (ghi mốc đúng) · ❌ xoá câu/trích dẫn.", ""], 0, 0
    strict_fail: list[str] = []
    for md in sorted(a.skill_dir.rglob("*.md")):
        if md.name == "SOURCES.md":
            continue
        for no, line in enumerate(md.read_text(encoding="utf-8").splitlines(), start=1):
            cits = CIT.findall(line)
            if not cits:
                continue
            n_lines += 1
            out.append(f"## {md.relative_to(a.skill_dir)}:{no}")
            out.append(f"> {line.strip()}")
            if a.strict:
                missing = unsupported_terms(line, cits, segs_by_key, sources, a.window)
                if missing:
                    where = f"{md.relative_to(a.skill_dir)}:{no}"
                    strict_fail.append(f"{where}  thiếu trong nguồn: {', '.join(missing)}")
                    out.append(f"- ⛔ STRICT: không thấy trong lời thoại quanh mốc: {', '.join(missing)}")
            for key, times in cits:
                segs = segs_by_key.get(key, [])
                if not segs:
                    n_empty += 1
                    out.append(f"- **[{key}] NO TRANSCRIPT** — không kiểm chứng được ⇒ xoá trích dẫn này")
                    continue
                for t in times.split(","):
                    s = secs(t)
                    if s is None:
                        continue
                    near = [x["text"] for x in segs
                            if x.get("start_s") is not None and s - a.window <= x["start_s"] <= s + a.window / 2]
                    out.append(f"- [{key} {t.strip()}] {sources[key]['title'][:70]}: "
                               f"“{' '.join(near)[:600] or '(không có lời thoại quanh mốc)'}”")
            out.append("- Kết luận: ")
            out.append("")
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"{n_lines} dòng có trích dẫn · {n_empty} trích dẫn tới video không có transcript → {a.out}")
    if a.strict:
        print(f"STRICT: {len(strict_fail)}/{n_lines} dòng có thuật ngữ (code/in đậm) không xuất hiện ở nguồn")
        for s in strict_fail[:400]:
            print("  -", s)
        if strict_fail or n_empty:
            raise SystemExit(1)


_TERM = re.compile(r"`([^`]+)`|\*\*([^*]+)\*\*")
_WORD = re.compile(r"[a-z0-9]+")
# Generic words that may legitimately be bolded in Vietnamese prose without being UI terms.
_STOP = {"the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "mode", "tool", "tools"}


def _norm_words(text: str) -> list[str]:
    # Whole tokens only: "Điểm tựa" must not shred into "i", "m", "t"... — keep pure-ASCII words.
    return [w for w in re.findall(r"\w+", text.lower())
            if w.isascii() and _WORD.fullmatch(w) and w not in _STOP]


def unsupported_terms(line, cits, segs_by_key, sources, window) -> list[str]:
    """Terms the line formats as `code`/**bold** whose words never appear near the cited times.

    Only ASCII/English words are checked (UI labels, hotkeys, API names); a term passes when
    every one of its words occurs in the cited windows, the video title or chapter titles.
    Vietnamese-only bold text has no ASCII words and is skipped.
    """
    terms = [t for pair in _TERM.findall(line) for t in pair if t]
    if not terms:
        return []
    haystack = []
    for key, times in cits:
        segs = segs_by_key.get(key, [])
        haystack.append(sources.get(key, {}).get("title", ""))
        for t in times.split(","):
            s = secs(t)
            if s is None:
                continue
            haystack += [x["text"] for x in segs
                         if x.get("start_s") is not None and s - window * 2 <= x["start_s"] <= s + window]
    hay = set(_norm_words(" ".join(haystack)))
    missing = []
    for term in terms:
        words = _norm_words(term)
        if words and not all(w in hay or (w.endswith("s") and w[:-1] in hay) for w in words):
            missing.append(term)
    return missing


if __name__ == "__main__":
    main()
