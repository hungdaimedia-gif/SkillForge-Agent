"""Offline tests for knowledge distillation (videos/books -> SKILL.md). No network, no API key."""
from __future__ import annotations

import asyncio
import json
import zipfile
from pathlib import Path

import pytest

from core import distill as D
from core.indexer import SkillWiki
from core.models import Frame, Segment, SkillBundle, SkillMetadata, SourceDoc, SourceSection
from core.sources.book import load_book
from core.sources.youtube import frame_times, merge_segments, parse_json3
from core.text import fold, tokenize


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def make_doc(tmp_path: Path, vid: str = "abcdefghijk", title: str = "Tutorial 7: Timeline") -> SourceDoc:
    (tmp_path / vid).mkdir(exist_ok=True)
    frame = tmp_path / vid / "f000150.jpg"
    frame.write_bytes(b"\xff\xd8fakejpeg")
    return SourceDoc(
        doc_id=vid, kind="youtube", title=title, url=f"https://www.youtube.com/watch?v={vid}",
        transcript_source="auto_subs:en", license="youtube_review_pending",
        extras={"duration_s": 120.0},
        sections=[SourceSection(
            section_id=f"{vid}#0", title="full video",
            segments=[Segment(anchor="0:05", text="press K to set a key", start_s=5, end_s=10),
                      Segment(anchor="1:10", text="use the interpolation menu", start_s=70, end_s=80)],
            frames=[Frame(frame_id="f000150", path=str(frame), t_s=15.0, reason="uniform")],
        )],
    )


class FakeKnowledgeLLM:
    """Routes on the system prompt; records every call."""

    def __init__(self, bad_anchor: bool = False, wrong_answers: bool = False):
        self.calls: list[str] = []
        self.images_seen: list[str] = []
        self.bad_anchor = bad_anchor
        self.wrong_answers = wrong_answers

    def complete(self, system: str, user: str) -> str:  # pragma: no cover - not used here
        raise AssertionError("knowledge pipeline must use complete_json")

    def complete_json(self, system, user, schema, images=None):
        self.images_seen += [p for _, p in images or []]
        if system == D.MAP_SYSTEM:
            self.calls.append("map")
            return {"section_summary": "keys and interpolation", "units": [
                {"kind": "shortcut", "title": "Set key", "content": "K sets a key on the current frame.",
                 "steps": [], "ui_terms": ["K"], "anchors": ["0:05"], "frames": ["f000150"],
                 "confidence": "high"},
                {"kind": "procedure", "title": "Change interpolation", "content": "Open the menu.",
                 "steps": ["Select keys", "Interpolation > Bezier"], "ui_terms": ["Interpolation"],
                 "anchors": ["[1:10]", "9:99"], "frames": ["nope"], "confidence": "medium"},
            ]}
        if system == D.PLAN_SYSTEM:
            self.calls.append("plan")
            ids = [line.split(" ")[0] for line in user.splitlines() if line.startswith("S1.u")]
            return {"hub": {"title": "Cascadeur overview", "description": "Use when using Cascadeur."},
                    "skills": [{"name": "timeline keys", "title": "Timeline keys", "category": "Timeline",
                                "description": "Use when setting keys or changing interpolation.",
                                "unit_ids": ids, "rationale": "same task"}]}
        if system.startswith(D.WRITE_SYSTEM[:40]):
            self.calls.append("write")
            anchor = "9:59" if self.bad_anchor else "0:05"
            asset = "assets/s1_f000150.jpg"
            return {"body": f"# Timeline keys\n\nNhấn `K` để đặt key [S1 {anchor}].\n\n"
                            f"![khung]({asset})\n\n"
                            "Chi tiết: [nội suy](references/Interp Detail.md) [S1 1:10]\n",
                    "references": [{"filename": "Interp Detail.md",
                                    "content": "Chọn `Interpolation > Bezier` [S1 1:10]."}],
                    "quiz": [{"question": "Phím đặt key?", "answer": "K", "anchors": ["0:05"]},
                             {"question": "Menu nội suy?", "answer": "Interpolation", "anchors": ["1:10"]},
                             {"question": "Kiểu nội suy?", "answer": "Bezier", "anchors": ["1:10"]}]}
        if system == D.STUDENT_SYSTEM:
            self.calls.append("student")
            assert "SKILL.md" in user and "Nhấn `K`" in user  # closed book: only skill text
            return {"answers": [{"index": i, "answer": "x"} for i in range(3)]}
        if system == D.JUDGE_SYSTEM:
            self.calls.append("judge")
            verdict = "wrong" if self.wrong_answers else "correct"
            return {"verdicts": [{"index": i, "verdict": verdict, "reason": ""} for i in range(3)]}
        raise AssertionError(f"unexpected system prompt: {system[:60]}")


# ---------------------------------------------------------------------------
# P0
# ---------------------------------------------------------------------------

def test_vietnamese_tokenizer_and_search(tmp_path: Path) -> None:
    assert fold("Đặt Khung Hình") == "dat khung hinh"
    assert tokenize("Xin chào Thế Giới") == ["xin", "chao", "the", "gioi"]
    wiki = SkillWiki(tmp_path / "wiki")
    meta = SkillMetadata(name="Tạo đường dẫn thân thiện", taxonomy_path="python/text/slug",
                         description="Chuyển tiêu đề tiếng Việt thành slug", status="validated")
    wiki.save(SkillBundle(metadata=meta, code_payload="print('x')\n"))
    hits = wiki.search("duong dan than thien")
    assert hits and hits[0].id == "python.text.slug"


def test_generated_code_cannot_read_api_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from runtime.executor import execute_code

    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-secret")
    monkeypatch.setenv("GH_TOKEN", "ghp-secret")
    code = ("import os, sys\n"
            "sys.exit(1 if os.environ.get('ANTHROPIC_API_KEY') or os.environ.get('GH_TOKEN') else 0)\n")
    res = asyncio.run(execute_code(code=code, runner="python", params={}, runs_dir=tmp_path / "runs",
                                   use_docker=False))
    assert res.success, res.stderr


def test_extractor_uses_structured_output(tmp_path: Path) -> None:
    from core.extractor import extract_skill

    class JsonLLM:
        def complete_json(self, system, user, schema, images=None):
            assert schema["required"] == ["metadata", "code"]
            return {"metadata": {"name": "Echo", "taxonomy_path": "python/text/echo", "description": "d",
                                 "tags": [], "params_schema_json": '{"text": "string"}',
                                 "example_params_json": '{"text": "hi"}', "runner": "python",
                                 "expected_artifacts": ["out.txt"], "expected_output": "out.txt",
                                 "source": ""},
                    "code": "print('ok')\n"}

    bundle = extract_skill(JsonLLM(), "tutorial")
    assert bundle.metadata.example_params == {"text": "hi"}
    assert bundle.metadata.params_schema == {"text": "string"}


# ---------------------------------------------------------------------------
# Sources
# ---------------------------------------------------------------------------

def test_json3_parsing_dedupe_and_merge(tmp_path: Path) -> None:
    f = tmp_path / "subs.en.json3"
    f.write_text(json.dumps({"events": [
        {"tStartMs": 0, "dDurationMs": 2000, "segs": [{"utf8": "hello"}]},
        {"tStartMs": 2000, "dDurationMs": 1000, "segs": [{"utf8": "hello"}]},  # rolling repeat
        {"tStartMs": 3000, "dDurationMs": 1000, "segs": [{"utf8": "\n"}]},
        {"tStartMs": 5000, "dDurationMs": 1000, "segs": [{"utf8": "press "}, {"utf8": "K"}]},
        {"tStartMs": 65000, "dDurationMs": 1000, "segs": [{"utf8": "later"}]},
    ]}), encoding="utf-8")
    segs = parse_json3(f)
    assert [s.text for s in segs] == ["hello", "press K", "later"]
    merged = merge_segments(segs, window_s=12)
    assert [m.anchor for m in merged] == ["0:00", "1:05"]
    assert merged[0].text == "hello press K"


def test_urls_manifest(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import core.sources as S

    seen = []
    monkeypatch.setattr(S, "fetch_video", lambda url, **kw: seen.append(url) or SourceDoc(
        doc_id=url[-11:], kind="youtube", title=url, url=url))
    f = tmp_path / "course.urls"
    f.write_text("# catalogue\nhttps://www.youtube.com/watch?v=aaaaaaaaaaa  # Physics | 5:00\n\n"
                 "https://www.youtube.com/watch?v=bbbbbbbbbbb\n", encoding="utf-8")
    docs = S.acquire(str(f), cache_dir=tmp_path)
    assert seen == ["https://www.youtube.com/watch?v=aaaaaaaaaaa",
                    "https://www.youtube.com/watch?v=bbbbbbbbbbb"]
    assert [d.extras["playlist_index"] for d in docs] == [1, 2]
    assert len(S.acquire(str(f), cache_dir=tmp_path, limit=1)) == 1


def test_frame_times_prefers_chapters_and_spacing() -> None:
    times = frame_times(100.0, [{"start_time": 0}, {"start_time": 50}], max_frames=5)
    assert (2.0, "chapter") in times and (52.0, "chapter") in times
    assert len(times) <= 5
    assert all(b[0] - a[0] >= 4 for a, b in zip(times, times[1:]))


def test_markdown_and_epub_books(tmp_path: Path) -> None:
    md = tmp_path / "guide.md"
    md.write_text("# Intro\n\nFirst para.\n\n## Keys\n\nPress K.\nIt sets a key.\n\nSecond.\n", encoding="utf-8")
    doc = load_book(md)
    assert [s.title for s in doc.sections] == ["Intro", "Keys"]
    assert doc.sections[1].segments[0].anchor == "§2¶1"
    assert doc.sections[1].segments[0].text == "Press K. It sets a key."
    assert doc.license == "book_paraphrase_only"

    epub = tmp_path / "book.epub"
    chapter = "<html><body><h1>Chapter One</h1>" + "<p>Animation principle text.</p>" * 20 + "</body></html>"
    with zipfile.ZipFile(epub, "w") as z:
        z.writestr("META-INF/container.xml",
                   '<container><rootfiles><rootfile full-path="OEBPS/content.opf"/></rootfiles></container>')
        z.writestr("OEBPS/content.opf",
                   '<package xmlns:dc="http://purl.org/dc/elements/1.1/"><metadata><dc:title>My Book</dc:title>'
                   '<dc:creator>An Author</dc:creator></metadata><manifest><item id="c1" href="c1.xhtml"/>'
                   '</manifest><spine><itemref idref="c1"/></spine></package>')
        z.writestr("OEBPS/c1.xhtml", chapter)
    edoc = load_book(epub)
    assert edoc.title == "My Book" and edoc.author == "An Author"
    assert edoc.sections[0].title == "Chapter One"
    assert len(edoc.sections[0].segments) == 21  # heading + 20 paragraphs


# ---------------------------------------------------------------------------
# Distillation pipeline
# ---------------------------------------------------------------------------

def test_distill_end_to_end_resumable(tmp_path: Path) -> None:
    doc = make_doc(tmp_path)
    wiki = SkillWiki(tmp_path / "wiki")
    llm = FakeKnowledgeLLM()
    report = D.distill([doc], llm, wiki, domain="cascadeur", work_dir=tmp_path / "work",
                       workers=1, log=lambda _: None)

    assert llm.calls.count("map") == 1 and llm.calls.count("plan") == 1
    assert llm.images_seen == [doc.sections[0].frames[0].path]  # frames really sent to the model
    names = sorted(s.name for s in report.skills)
    assert names == ["cascadeur", "cascadeur-timeline-keys"]
    res = next(s for s in report.skills if s.name == "cascadeur-timeline-keys")
    assert res.status == "validated", res.errors
    assert res.eval_score == 1.0

    skill_dir = Path(res.path)
    skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    assert skill_md.startswith("---\nname: cascadeur-timeline-keys\ndescription: Use when")
    assert "references/interp_detail.md" in skill_md  # link normalised to slugged file
    assert (skill_dir / "references" / "interp_detail.md").exists()
    assert (skill_dir / "assets" / "s1_f000150.jpg").exists()
    sources = (skill_dir / "SOURCES.md").read_text(encoding="utf-8")
    assert "https://www.youtube.com/watch?v=abcdefghijk&t=70s" in sources
    meta = json.loads((skill_dir / "skill.json").read_text(encoding="utf-8"))
    assert meta["kind"] == "knowledge" and meta["license"] == "youtube_review_pending"

    units = json.loads((tmp_path / "work" / "cascadeur" / "units.json").read_text(encoding="utf-8"))
    interp = next(u for u in units if u["title"] == "Change interpolation")
    assert interp["anchors"] == ["1:10"]  # "[1:10]" cleaned, out-of-range "9:99" dropped
    assert interp["frames"] == []  # unknown frame id dropped

    # Re-run: everything cached -> zero LLM calls.
    before = len(llm.calls)
    D.distill([doc], llm, wiki, domain="cascadeur", work_dir=tmp_path / "work", workers=1,
              log=lambda _: None)
    assert len(llm.calls) == before

    # --redo one skill: only that skill is rewritten + re-quizzed.
    D.distill([doc], llm, wiki, domain="cascadeur", work_dir=tmp_path / "work", workers=1,
              redo=["cascadeur-timeline-keys"], log=lambda _: None)
    assert llm.calls[before:] == ["write", "student", "judge"]

    # Search finds it, MCP can read it, runtime refuses to "execute" it.
    assert wiki.search("timeline keys", domain="cascadeur")[0].kind == "knowledge"
    from runtime import mcp_server
    from runtime.executor import run_skill

    skill_id = meta["taxonomy_path"].replace("/", ".")
    import os
    os.environ["SKILLFORGE_WIKI"] = str(tmp_path / "wiki")
    details = mcp_server.get_skill_details(skill_id)
    assert details["success"] and "SKILL.md" in details["files"]
    ref = mcp_server.read_skill_file(skill_id, "references/interp_detail.md")
    assert "Bezier" in ref["content"]
    assert not mcp_server.read_skill_file(skill_id, "../../skill.json")["success"]
    res_run = asyncio.run(run_skill(wiki, skill_id))
    assert not res_run.success and "knowledge skill" in res_run.stderr


def test_cached_units_are_rekeyed_when_source_order_changes(tmp_path: Path) -> None:
    doc = make_doc(tmp_path)
    other = make_doc(tmp_path, vid="zzzzzzzzzzz", title="Other video")
    wiki = SkillWiki(tmp_path / "wiki")
    llm = FakeKnowledgeLLM()
    D.distill([doc], llm, wiki, domain="cascadeur", work_dir=tmp_path / "work", workers=1,
              run_eval=False, log=lambda _: None)
    # Now the same video is the 2nd source: its cached units must become S2.*
    D.distill([other, doc], llm, wiki, domain="cascadeur", work_dir=tmp_path / "work", workers=1,
              run_eval=False, log=lambda _: None)
    units = json.loads((tmp_path / "work" / "cascadeur" / "units.json").read_text(encoding="utf-8"))
    assert {u["source_key"] for u in units if u["unit_id"].startswith("S2.")} == {"S2"}
    assert all(u["unit_id"].split(".")[0] == u["source_key"] for u in units)


def test_gate_rejects_invented_anchor(tmp_path: Path) -> None:
    doc = make_doc(tmp_path)
    wiki = SkillWiki(tmp_path / "wiki")
    llm = FakeKnowledgeLLM(bad_anchor=True)
    report = D.distill([doc], llm, wiki, domain="cascadeur", work_dir=tmp_path / "work",
                       workers=1, log=lambda _: None)
    res = next(s for s in report.skills if s.name == "cascadeur-timeline-keys")
    assert res.status == "draft"
    assert any("invalid anchor [S1 9:59]" in e for e in res.errors)
    assert "student" not in llm.calls  # no eval spend on a skill that already failed the gate


def test_low_quiz_score_keeps_draft(tmp_path: Path) -> None:
    doc = make_doc(tmp_path)
    wiki = SkillWiki(tmp_path / "wiki")
    report = D.distill([doc], FakeKnowledgeLLM(wrong_answers=True), wiki, domain="cascadeur",
                       work_dir=tmp_path / "work", workers=1, log=lambda _: None)
    res = next(s for s in report.skills if s.name == "cascadeur-timeline-keys")
    assert res.status == "draft" and res.eval_score == 0.0


def test_export_never_overwrites(tmp_path: Path, capsys: pytest.CaptureFixture) -> None:
    from skillforge_cli import export_skills

    doc = make_doc(tmp_path)
    wiki = SkillWiki(tmp_path / "wiki")
    D.distill([doc], FakeKnowledgeLLM(), wiki, domain="cascadeur", work_dir=tmp_path / "work",
              workers=1, log=lambda _: None)
    dest = tmp_path / "skills"
    out = export_skills(wiki, "cascadeur", dest)
    exported = {p.name for p in out}
    assert "cascadeur-timeline-keys" in exported
    target = dest / "cascadeur-timeline-keys"
    assert (target / "SKILL.md").exists() and not (target / "skill.json").exists()
    (target / "SKILL.md").write_text("hand edited", encoding="utf-8")
    assert export_skills(wiki, "cascadeur", dest) == []
    assert (target / "SKILL.md").read_text(encoding="utf-8") == "hand edited"
    assert "not overwritten" in capsys.readouterr().out
