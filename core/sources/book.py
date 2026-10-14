"""Book / document acquisition: PDF, EPUB, Markdown, plain text -> SourceDoc.

Anchors point back into the original: 'p.87' for PDF pages, '§<n>' for EPUB
chapters / Markdown headings + paragraph index. No LLM is used here.

PDF needs PyMuPDF (`pip install pymupdf`) or pypdf; EPUB is parsed with the
standard library (it is a zip of XHTML files).
"""
from __future__ import annotations

import hashlib
import html
import logging
import re
import zipfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET

from ..models import Segment, SourceDoc, SourceSection
from ..text import slugify

logger = logging.getLogger("skillforge.sources.book")

BOOK_SUFFIXES = {".pdf", ".epub", ".md", ".markdown", ".txt"}
# A map call should see a whole chapter but not a whole book.
MAX_SECTION_CHARS = 60_000


def doc_id_for(path: Path) -> str:
    digest = hashlib.sha1(path.read_bytes()).hexdigest()[:8]
    return f"{slugify(path.stem, sep='_', max_len=40)}_{digest}"


def load_book(path: Path | str, title: str | None = None) -> SourceDoc:
    path = Path(path).resolve()
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        sections, meta = _pdf(path)
        source = "pdf"
    elif suffix == ".epub":
        sections, meta = _epub(path)
        source = "epub"
    elif suffix in (".md", ".markdown", ".txt"):
        sections, meta = _markdown(path.read_text(encoding="utf-8", errors="replace")), {}
        source = "text"
    else:
        raise ValueError(f"Unsupported book format: {suffix}")
    doc_id = doc_id_for(path)
    for i, s in enumerate(sections):
        s.section_id = f"{doc_id}#{i}"
    return SourceDoc(
        doc_id=doc_id, kind="book" if suffix in (".pdf", ".epub") else "text",
        title=title or meta.get("title") or path.stem, url=str(path),
        author=meta.get("author", ""),
        # Books are almost always copyrighted: skills may paraphrase, never reproduce.
        license="book_paraphrase_only",
        transcript_source=source, sections=_split_long(sections),
    )


# ---------------------------------------------------------------------------

def _split_long(sections: list[SourceSection]) -> list[SourceSection]:
    out: list[SourceSection] = []
    for s in sections:
        if s.char_len() <= MAX_SECTION_CHARS:
            out.append(s)
            continue
        part, size, n = [], 0, 1
        for seg in s.segments:
            if part and size + len(seg.text) > MAX_SECTION_CHARS:
                out.append(SourceSection(section_id=f"{s.section_id}.{n}",
                                         title=f"{s.title} (part {n})", segments=part))
                part, size, n = [], 0, n + 1
            part.append(seg)
            size += len(seg.text)
        if part:
            out.append(SourceSection(section_id=f"{s.section_id}.{n}",
                                     title=f"{s.title} (part {n})" if n > 1 else s.title,
                                     segments=part))
    return out


def _markdown(text: str) -> list[SourceSection]:
    """Split on #/## headings; each paragraph becomes a segment anchored §heading¶n."""
    sections: list[SourceSection] = []
    title, paras, buf = "Introduction", [], []

    def flush_para():
        if buf:
            paras.append(" ".join(buf).strip())
            buf.clear()

    def flush_section():
        flush_para()
        if any(paras):
            idx = len(sections) + 1
            sections.append(SourceSection(section_id="", title=title, segments=[
                Segment(anchor=f"§{idx}¶{j + 1}", text=p) for j, p in enumerate(paras) if p]))
        paras.clear()

    for line in text.splitlines():
        m = re.match(r"^(#{1,2})\s+(.*)", line)
        if m:
            flush_section()
            title = m.group(2).strip()
        elif not line.strip():
            flush_para()
        else:
            buf.append(line.strip())
    flush_section()
    return sections


def _pdf(path: Path) -> tuple[list[SourceSection], dict]:
    pages: list[str]
    toc: list[tuple[int, str, int]] = []
    meta: dict = {}
    try:
        import fitz  # PyMuPDF

        with fitz.open(path) as pdf:
            pages = [p.get_text("text") for p in pdf]
            toc = [(lvl, t, pg) for lvl, t, pg in pdf.get_toc() if lvl <= 2]
            meta = {k: v for k, v in (pdf.metadata or {}).items() if v}
    except ImportError:
        try:
            from pypdf import PdfReader
        except ImportError as exc:
            raise RuntimeError("Reading PDF needs `pip install pymupdf` (or pypdf)") from exc
        reader = PdfReader(str(path))
        pages = [p.extract_text() or "" for p in reader.pages]
        info = reader.metadata or {}
        meta = {"title": info.get("/Title", ""), "author": info.get("/Author", "")}

    if sum(len(p.strip()) for p in pages) < 200:
        raise RuntimeError(f"{path.name}: no text layer (scanned PDF?) — OCR it first")

    segs = [Segment(anchor=f"p.{i + 1}", text=re.sub(r"\s+", " ", t).strip())
            for i, t in enumerate(pages) if t.strip()]
    if toc:
        starts = sorted({(pg, t) for _, t, pg in toc if pg >= 1})
        sections = []
        for k, (pg, t) in enumerate(starts):
            end = starts[k + 1][0] if k + 1 < len(starts) else len(pages) + 1
            body = [s for s in segs if pg <= int(s.anchor[2:]) < end]
            if body:
                sections.append(SourceSection(section_id="", title=t, segments=body))
        front = [s for s in segs if int(s.anchor[2:]) < starts[0][0]]
        if front:
            sections.insert(0, SourceSection(section_id="", title="Front matter", segments=front))
        return sections, meta
    # No outline: fixed 10-page sections.
    return [SourceSection(section_id="", title=f"pp. {segs[i].anchor[2:]}–{segs[min(i + 9, len(segs) - 1)].anchor[2:]}",
                          segments=segs[i:i + 10]) for i in range(0, len(segs), 10)], meta


_TAG = re.compile(r"<[^>]+>")


def _xhtml_paragraphs(raw: str) -> list[str]:
    raw = re.sub(r"(?is)<(script|style|head)[^>]*>.*?</\1>", " ", raw)
    raw = re.sub(r"(?i)</(p|div|h[1-6]|li|tr|blockquote)>|<br\s*/?>", "\n\n", raw)
    text = html.unescape(_TAG.sub(" ", raw))
    return [re.sub(r"\s+", " ", p).strip() for p in text.split("\n\n") if p.strip()]


def _epub(path: Path) -> tuple[list[SourceSection], dict]:
    with zipfile.ZipFile(path) as z:
        container = ET.fromstring(z.read("META-INF/container.xml"))
        rootfile = next(e.get("full-path") for e in container.iter() if e.tag.endswith("rootfile"))
        opf = ET.fromstring(z.read(rootfile))
        base = PurePosixPath(rootfile).parent
        manifest = {e.get("id"): e.get("href") for e in opf.iter() if e.tag.endswith("item")}
        spine = [e.get("idref") for e in opf.iter() if e.tag.endswith("itemref")]
        meta = {}
        for e in opf.iter():
            if e.tag.endswith("}title") and e.text:
                meta.setdefault("title", e.text.strip())
            if e.tag.endswith("}creator") and e.text:
                meta.setdefault("author", e.text.strip())
        sections = []
        for n, idref in enumerate(spine, start=1):
            href = manifest.get(idref)
            if not href:
                continue
            raw = z.read(str(base / href)).decode("utf-8", errors="replace")
            paras = _xhtml_paragraphs(raw)
            if sum(len(p) for p in paras) < 200:  # cover, toc, blank pages
                continue
            m = re.search(r"(?is)<h[1-3][^>]*>(.*?)</h[1-3]>", raw)
            title = html.unescape(_TAG.sub("", m.group(1))).strip() if m else f"Chapter {n}"
            sections.append(SourceSection(section_id="", title=title or f"Chapter {n}", segments=[
                Segment(anchor=f"§{len(sections) + 1}¶{j + 1}", text=p) for j, p in enumerate(paras)]))
    return sections, meta
