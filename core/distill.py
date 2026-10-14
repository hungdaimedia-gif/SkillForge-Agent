"""Knowledge distillation: SourceDocs (videos, books) -> offline agent skills (SKILL.md).

Pipeline (each stage cached in work_dir so a crash or re-run costs nothing extra):

  map     one call per source section  -> cited KnowledgeUnits   (sees frames)
  plan    one call per collection       -> skills = clusters of unit ids + hub skill
  write   one call per skill            -> SKILL.md body + references/ + quiz
  gate    deterministic                 -> name/description/length/citations/links
  eval    two calls per skill (opt.)    -> closed-book quiz: can an agent with ONLY
                                           this skill answer questions from the source?

Ideas adapted from Microsoft Resource2Skill (MIT): modality decomposition,
quality gates before a skill becomes active, license tagging per source.
"""
from __future__ import annotations

import json
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from .llm import complete_json
from .models import (KnowledgeSkill, KnowledgeUnit, QuizItem, SkillPlanItem, SourceDoc,
                     SourceSection)
from .text import fmt_ts, parse_ts, slugify

logger = logging.getLogger("skillforge.distill")

LANG_NAMES = {"vi": "Vietnamese", "en": "English"}
_STR = {"type": "string"}
_STRS = {"type": "array", "items": _STR}
UNIT_KINDS = ["procedure", "concept", "shortcut", "setting", "heuristic", "pitfall", "example"]
# [S3 1:23] / [S3 1:23, 2:05] / [S5 p.87] / [S2 §3¶4]
CITATION_RE = re.compile(r"\[(S\d+)\s+([^\]\[]+?)\]")
ASSET_RE = re.compile(r"\]\((assets/[A-Za-z0-9_.\-]+)\)")
REF_RE = re.compile(r"(references/[A-Za-z0-9_.\-]+\.md)")


def _obj(props: dict, required: list[str] | None = None) -> dict:
    return {"type": "object", "properties": props,
            "required": required or list(props), "additionalProperties": False}


# ---------------------------------------------------------------------------
# Stage 1 — map: section -> knowledge units
# ---------------------------------------------------------------------------

MAP_SCHEMA = _obj({
    "section_summary": _STR,
    "units": {"type": "array", "items": _obj({
        "kind": {"type": "string", "enum": UNIT_KINDS},
        "title": _STR,
        "content": _STR,
        "steps": _STRS,
        "ui_terms": _STRS,
        "anchors": _STRS,
        "frames": _STRS,
        "confidence": {"type": "string", "enum": ["high", "medium", "low"]},
    })},
})

MAP_SYSTEM = """\
You distill tutorial material (video transcripts + keyframes, or book chapters) into
knowledge units that an AI agent will later rely on WITHOUT internet access. Whatever
you miss now is lost forever, so be exhaustive and concrete.

Unit kinds:
- procedure: an ordered way to accomplish something. Put each action in `steps`, naming
  the exact menu path, button, panel, mouse button and hotkey.
- shortcut: one hotkey / mouse binding and what it does.
- setting: a parameter, mode or option, its values and their effect.
- concept: what a feature/idea is and why it matters (mental model).
- heuristic: rule of thumb, when to choose A over B, best practice.
- pitfall: a mistake, its symptom, and the fix.
- example: a worked example worth reproducing (values, sequence).

Rules:
- Use only what the source says or shows. Domain knowledge may ONLY be used to fix obvious
  speech-recognition errors in auto-generated transcripts (e.g. a misheard tool name); then
  set confidence "medium".
- Keyframes carry information the narration skips: on-screen hotkey overlays, panel and
  button labels, menu items, numeric values. Read them carefully and cite their frame ids.
- `ui_terms`: exact UI labels and key combos verbatim as shown (keep original language).
- `anchors`: the [m:ss] times (video) or [p.N] / [§..] markers (book) where the unit is
  supported, copied exactly from the source markers. At least one per unit.
- `content`: 1-4 concise sentences in English, paraphrased (never long quotes).
- Prefer several precise units over one vague unit. Skip greetings, sponsor talk, outros.
- `section_summary`: 2-3 sentences on what this section teaches.
"""


def _section_prompt(doc: SourceDoc, section: SourceSection, key: str) -> str:
    kind = {"youtube": "YouTube video", "book": "book", "text": "document"}[doc.kind]
    lines = [
        f"Source {key}: {kind} \"{doc.title}\"" + (f" by {doc.author}" if doc.author else ""),
        f"Section: {section.title}",
        f"Transcript origin: {doc.transcript_source}"
        + (" (automatic captions: expect recognition errors)" if "auto" in doc.transcript_source else ""),
    ]
    desc = doc.extras.get("description")
    if desc:
        lines.append(f"Description (context only): {desc[:600]}")
    if section.frames:
        lines.append("Keyframes attached (by frame id): " + ", ".join(
            f"{f.frame_id}@{fmt_ts(f.t_s)}" for f in section.frames))
    lines.append("\nSOURCE TEXT:")
    for s in section.segments:
        lines.append(f"[{s.anchor}] {s.text}")
    if not section.segments:
        lines.append("(no transcript — rely on the keyframes)")
    return "\n".join(lines)


def _valid_anchor(doc: SourceDoc, anchor: str) -> bool:
    anchor = anchor.strip().strip("[]")
    if doc.kind == "youtube":
        secs = parse_ts(anchor)
        dur = float(doc.extras.get("duration_s") or 0)
        return secs is not None and 0 <= secs <= (dur + 5 if dur else 1e9)
    known = {s.anchor for sec in doc.sections for s in sec.segments}
    if anchor in known:
        return True
    m = re.fullmatch(r"p\.(\d+)(?:\s*[-–]\s*(\d+))?", anchor)
    if m:
        pages = {s.anchor for s in (seg for sec in doc.sections for seg in sec.segments)}
        return f"p.{m.group(1)}" in pages
    return False


def map_section(llm: Any, doc: SourceDoc, section: SourceSection, key: str) -> list[KnowledgeUnit]:
    images = [(f"Frame {f.frame_id} at {fmt_ts(f.t_s)}:", f.path) for f in section.frames]
    data = complete_json(llm, MAP_SYSTEM, _section_prompt(doc, section, key), MAP_SCHEMA,
                         images=images)
    frames = {f.frame_id: f.path for f in section.frames}
    fallback_anchor = section.segments[0].anchor if section.segments else (
        fmt_ts(section.frames[0].t_s) if section.frames else "0:00")
    units: list[KnowledgeUnit] = []
    for raw in data.get("units", []):
        anchors = [a.strip().strip("[]") for a in raw.get("anchors", [])]
        anchors = [a for a in anchors if _valid_anchor(doc, a)]
        confidence = raw.get("confidence", "high")
        if not anchors:  # model cited nothing checkable: keep, but flag it
            anchors, confidence = [fallback_anchor], "low"
        units.append(KnowledgeUnit(
            unit_id="",  # assigned by the caller (stable order)
            source_key=key,
            kind=raw.get("kind", "concept"),
            title=raw.get("title", "").strip(),
            content=raw.get("content", "").strip(),
            steps=[s for s in raw.get("steps", []) if s.strip()],
            ui_terms=[t for t in raw.get("ui_terms", []) if t.strip()],
            anchors=anchors,
            frames=[frames[f] for f in raw.get("frames", []) if f in frames],
            confidence=confidence,
        ))
    return units


# ---------------------------------------------------------------------------
# Stage 2 — plan: units -> skills
# ---------------------------------------------------------------------------

PLAN_SCHEMA = _obj({
    "hub": _obj({"title": _STR, "description": _STR}),
    "skills": {"type": "array", "items": _obj({
        "name": _STR, "title": _STR, "category": _STR, "description": _STR,
        "unit_ids": _STRS, "rationale": _STR,
    })},
})

PLAN_SYSTEM = """\
You design a library of agent skills from extracted knowledge units. A skill is ONE
coherent capability an agent would be asked to perform or explain (e.g. "animate a jump
with correct ballistics"), not one per source video or chapter.

Rules:
- Group units by task/capability. Typically 4-12 skills per collection; merge thin topics,
  split a topic only when it would exceed ~40 units.
- Every unit id must appear in at least one skill. A unit may appear in two skills when
  both genuinely need it.
- `name`: kebab-case, lowercase ascii, starts with the domain prefix given, max 64 chars.
- `category`: one lowercase word or snake_case slug grouping related skills (e.g. "timeline").
- `description` (max 600 chars, English): third person, starts with "Use when", lists the
  concrete situations, user phrasings and keywords that should trigger the skill (UI terms,
  feature names). It decides whether the agent loads the skill, so be specific.
- `hub`: an overview skill for the whole domain (glossary, shortcut cheat sheet, routing to
  the other skills). Give its title and trigger description.
- If an existing skill name is listed and covers the same capability, reuse that exact name.
"""


def plan_skills(llm: Any, units: list[KnowledgeUnit], domain: str,
                source_titles: dict[str, str], existing: list[tuple[str, str]] | None = None
                ) -> list[SkillPlanItem]:
    lines = [f"Domain prefix: {domain}", "Sources:"]
    lines += [f"- {k}: {t}" for k, t in source_titles.items()]
    if existing:
        lines.append("Existing skills (reuse names when same capability):")
        lines += [f"- {n}: {d[:160]}" for n, d in existing]
    lines.append("\nUnits (id [kind] title — content):")
    for u in units:
        lines.append(f"{u.unit_id} [{u.kind}] {u.title} — {u.content[:180]}")
    data = complete_json(llm, PLAN_SYSTEM, "\n".join(lines), PLAN_SCHEMA)

    known = {u.unit_id for u in units}
    prefix = slugify(domain)
    plan: list[SkillPlanItem] = []
    used: set[str] = set()
    for raw in data.get("skills", []):
        name = slugify(raw.get("name", ""))
        if not name.startswith(prefix):
            name = f"{prefix}-{name}"
        name = name[:64].strip("-")
        if name == prefix or any(p.name == name for p in plan):
            name = f"{name}-{len(plan) + 1}"
        ids = [i for i in raw.get("unit_ids", []) if i in known]
        if not ids:
            continue
        used.update(ids)
        plan.append(SkillPlanItem(
            name=name, title=raw.get("title", name), category=slugify(raw.get("category", "general"), sep="_"),
            description=raw.get("description", "")[:1000], unit_ids=ids,
            rationale=raw.get("rationale", "")))

    # Hub: glossary + cheat sheet material + anything the planner forgot.
    hub_ids = [u.unit_id for u in units
               if u.kind in ("shortcut", "concept") or u.unit_id not in used]
    hub = data.get("hub") or {}
    plan.insert(0, SkillPlanItem(
        name=prefix, title=hub.get("title") or f"{domain} overview",
        category="overview", is_hub=True, unit_ids=hub_ids,
        description=(hub.get("description") or f"Use when working with {domain}.")[:1000]))
    return plan


# ---------------------------------------------------------------------------
# Stage 3 — write: plan item + units -> SKILL.md
# ---------------------------------------------------------------------------

WRITE_SCHEMA = _obj({
    "body": _STR,
    "references": {"type": "array", "items": _obj({"filename": _STR, "content": _STR})},
    "quiz": {"type": "array", "items": _obj({"question": _STR, "answer": _STR, "anchors": _STRS})},
})

WRITE_SYSTEM = """\
You write an Agent Skill (SKILL.md body, no frontmatter) from cited knowledge units.
The reader is an AI agent with NO internet access: after reading, it must be able to
do the work or guide a human step by step. Write in {lang}; keep UI labels, menu items,
hotkeys and parameter names verbatim in the software's language (usually English),
formatted as `code`.

Body structure (omit a section only if there is nothing for it):
  # <Title>
  One-paragraph overview: what this capability is and the outcome.
  ## Khi nào dùng / When to use        (concrete triggers)
  ## Khái niệm cốt lõi / Core concepts   (mental model the agent needs)
  ## Quy trình / Procedures              (numbered steps, exact UI path + hotkeys)
  ## Quy tắc chọn / Decision rules        (if X then Y; trade-offs)
  ## Lỗi hay gặp / Pitfalls               (symptom -> cause -> fix)
  ## Tra nhanh / Quick reference          (table: action | hotkey/UI | note)
  ## Tự kiểm / Self-check                  (how to verify the result is right)
Use the language-appropriate heading of each pair.

Rules:
- Only state what the units support. Cite after each factual sentence or step with the
  unit's source key and anchor, exactly like [S3 1:23] or [S5 p.87] (several anchors:
  [S3 1:23, 2:05]). Never invent anchors. If a gap matters, say the source does not cover it.
- Low-confidence units: include only with a short "(chưa chắc chắn)" / "(unverified)" note.
- Keep the body under ~350 lines. Move long tables, exhaustive per-feature detail or
  long examples to reference files and link them from the body as
  [title](references/<file>.md). Reference files follow the same citation rules.
- Images: you may embed listed keyframes as ![what it shows](assets/<frame>.jpg) where a
  picture of the UI genuinely helps (max ~6). Use only the listed asset names.
- Link to sibling skills by name when a step belongs to another skill.
- quiz: 6-10 practical questions an agent should answer after reading (hotkeys, which
  setting to use when, exact procedure steps, pitfalls), each with the correct answer and
  the anchors supporting it.
"""

HUB_EXTRA = """\
THIS IS THE HUB SKILL for the whole domain. Its body must contain:
- what the software/topic is and the overall workflow, in order;
- a routing table: | Task | Skill to load | (all sibling skills listed below);
- a complete shortcut / hotkey cheat sheet from the units;
- a glossary of the domain's terms;
- if any source description says it is outdated or points to an updated guide/version,
  a short version warning near the top (the agent may face a newer UI).
"""


def _unit_block(u: KnowledgeUnit, frame_names: dict[str, str]) -> str:
    out = [f"### {u.unit_id} [{u.kind}] {u.title}  (anchors: "
           + ", ".join(f"{u.source_key} {a}" for a in u.anchors) + f"; confidence: {u.confidence})",
           u.content]
    if u.steps:
        out += [f"  {i}. {s}" for i, s in enumerate(u.steps, 1)]
    if u.ui_terms:
        out.append("  UI terms: " + " | ".join(u.ui_terms))
    if u.frames:
        out.append("  Frames: " + ", ".join(frame_names[p] for p in u.frames if p in frame_names))
    return "\n".join(out)


def write_skill(llm: Any, item: SkillPlanItem, units: list[KnowledgeUnit], plan: list[SkillPlanItem],
                domain: str, docs_by_key: dict[str, SourceDoc], lang: str = "vi",
                max_assets: int = 12) -> KnowledgeSkill:
    by_id = {u.unit_id: u for u in units}
    mine = [by_id[i] for i in item.unit_ids if i in by_id]
    # Asset names: frame stem + source key keeps them unique across videos.
    frame_names: dict[str, str] = {}
    for u in mine:
        for p in u.frames:
            if p not in frame_names and len(frame_names) < max_assets:
                frame_names[p] = f"{u.source_key.lower()}_{Path(p).stem}.jpg"

    system = WRITE_SYSTEM.format(lang=LANG_NAMES.get(lang, lang)) + (HUB_EXTRA if item.is_hub else "")
    lines = [f"Skill name: {item.name}", f"Title: {item.title}", f"Trigger description: {item.description}",
             "", "Sibling skills:"]
    lines += [f"- {p.name}: {p.description[:200]}" for p in plan if p.name != item.name]
    lines += ["", "Sources:"]
    keys = sorted({u.source_key for u in mine}, key=lambda k: int(k[1:]))
    for k in keys:
        if k not in docs_by_key:
            continue
        d = docs_by_key[k]
        note = ""
        if item.is_hub and d.extras.get("description"):
            note = " — description: " + " ".join(str(d.extras["description"]).split())[:300]
        lines.append(f"- {k}: {d.title}{note}")
    lines += ["", "Available assets: " + (", ".join(f"assets/{n}" for n in frame_names.values()) or "none"),
              "", "KNOWLEDGE UNITS:"]
    lines += [_unit_block(u, frame_names) for u in mine]

    data = complete_json(llm, system, "\n".join(lines), WRITE_SCHEMA)
    references = {}
    for ref in data.get("references", []):
        fname = slugify(Path(ref.get("filename", "")).stem, sep="_") + ".md"
        references[f"references/{fname}"] = ref.get("content", "")
    body = data.get("body", "")
    # Normalise reference links to the slugged filenames.
    for ref in data.get("references", []):
        orig = Path(ref.get("filename", "")).name
        fixed = slugify(Path(orig).stem, sep="_") + ".md"
        if orig and orig != fixed:
            body = body.replace(f"references/{orig}", f"references/{fixed}")

    assets = {f"assets/{name}": path for path, name in frame_names.items()}
    used_assets = set(ASSET_RE.findall(body + "\n".join(references.values())))
    assets = {k: v for k, v in assets.items() if k in used_assets}

    skill = KnowledgeSkill(
        plan=item, domain=slugify(domain, sep="_"), body=body, references=references, assets=assets,
        quiz=[QuizItem(**q) for q in data.get("quiz", [])],
        license=_combined_license([docs_by_key[k] for k in keys if k in docs_by_key]),
        sources=[docs_by_key[k].url for k in keys if k in docs_by_key],
    )
    skill.sources_md = sources_md(skill, docs_by_key)
    return skill


def _combined_license(docs: list[SourceDoc]) -> str:
    lic = sorted({d.license for d in docs if d.license})
    return ",".join(lic)


def sources_md(skill: KnowledgeSkill, docs_by_key: dict[str, SourceDoc]) -> str:
    """Deterministic provenance file: every citation resolved to a deep link."""
    text = skill.body + "\n" + "\n".join(skill.references.values())
    cited: dict[str, set[str]] = {}
    for key, anchors in CITATION_RE.findall(text):
        for a in anchors.split(","):
            cited.setdefault(key, set()).add(a.strip())
    lines = ["# Nguồn / Sources", "",
             "Skill được chưng cất bằng SkillForge-Agent; nội dung đã diễn giải lại, không chép nguyên văn.",
             "", "| Key | Nguồn | Loại | Giấy phép |", "|---|---|---|---|"]
    for key in sorted(cited, key=lambda k: int(k[1:])):
        d = docs_by_key.get(key)
        if d:
            lines.append(f"| {key} | [{d.title}]({d.url}) | {d.transcript_source} | {d.license} |")
    lines += ["", "## Mốc trích dẫn / Cited anchors", ""]
    for key in sorted(cited, key=lambda k: int(k[1:])):
        d = docs_by_key.get(key)
        if not d:
            continue
        def order(a: str) -> float:
            v = parse_ts(a)
            return v if v is not None else 0.0
        links = [f"[{a}]({d.anchor_url(a)})" if d.kind == "youtube" else a
                 for a in sorted(cited[key], key=order)]
        lines.append(f"- **{key}** — " + ", ".join(links))
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Stage 4 — gates (deterministic)
# ---------------------------------------------------------------------------

_NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def lint_skill(skill: KnowledgeSkill, docs_by_key: dict[str, SourceDoc]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings). Errors keep the skill in 'draft'."""
    errors: list[str] = []
    warnings: list[str] = []
    name, desc = skill.plan.name, skill.plan.description
    if not _NAME_RE.match(name) or len(name) > 64:
        errors.append(f"name '{name}' must be kebab-case <= 64 chars")
    if not desc.strip():
        errors.append("description is empty")
    elif len(desc) > 1024:
        errors.append(f"description too long ({len(desc)} > 1024)")
    elif "use when" not in desc.lower():
        warnings.append("description should say 'Use when ...' so the agent knows when to load it")

    n_lines = skill.body.count("\n") + 1
    if n_lines > 800:
        errors.append(f"SKILL.md body has {n_lines} lines (> 800); move detail to references/")
    elif n_lines > 500:
        warnings.append(f"SKILL.md body has {n_lines} lines (> 500 recommended)")

    all_text = {"SKILL.md": skill.body, **skill.references}
    n_cites = 0
    for fname, text in all_text.items():
        for key, anchors in CITATION_RE.findall(text):
            n_cites += 1
            doc = docs_by_key.get(key)
            if doc is None:
                errors.append(f"{fname}: citation to unknown source {key}")
                continue
            for a in anchors.split(","):
                if not _valid_anchor(doc, a):
                    errors.append(f"{fname}: invalid anchor [{key} {a.strip()}]")
        for asset in ASSET_RE.findall(text):
            if asset not in skill.assets:
                errors.append(f"{fname}: image {asset} is not an available asset")
        for ref in REF_RE.findall(text):
            if ref not in skill.references:
                errors.append(f"{fname}: link to missing {ref}")
    if n_cites == 0:
        errors.append("no citations: nothing in the skill is traceable to the source")
    elif n_cites < max(3, len(skill.plan.unit_ids) // 4):
        warnings.append(f"only {n_cites} citations for {len(skill.plan.unit_ids)} units")
    for ref in skill.references:
        if ref not in skill.body:
            warnings.append(f"{ref} is not linked from SKILL.md (agent may never open it)")
    if len(skill.quiz) < 3:
        warnings.append("fewer than 3 quiz questions: offline eval will be weak")
    return errors, warnings


# ---------------------------------------------------------------------------
# Stage 5 — closed-book eval
# ---------------------------------------------------------------------------

ANSWER_SCHEMA = _obj({"answers": {"type": "array", "items": _obj({"index": {"type": "integer"},
                                                                    "answer": _STR})}})
JUDGE_SCHEMA = _obj({"verdicts": {"type": "array", "items": _obj({
    "index": {"type": "integer"},
    "verdict": {"type": "string", "enum": ["correct", "partial", "wrong"]},
    "reason": _STR})}})

STUDENT_SYSTEM = """\
You are an agent working offline. You have NO internet and must not use outside
knowledge: answer ONLY from the skill files provided. If the files do not contain the
answer, say "not in skill". Be specific (exact hotkeys, menu paths, values)."""

JUDGE_SYSTEM = """\
Grade each student answer against the reference answer. "correct": same essential facts
(hotkeys, steps, values) even if worded differently; "partial": incomplete or partly wrong;
"wrong": incorrect or "not in skill". Be strict about concrete facts."""


def skill_text(skill: KnowledgeSkill) -> str:
    parts = [f"=== SKILL.md ===\n{skill.skill_md()}"]
    parts += [f"=== {k} ===\n{v}" for k, v in skill.references.items()]
    return "\n\n".join(parts)


def evaluate_skill(llm: Any, skill: KnowledgeSkill) -> tuple[float, list[dict]]:
    if not skill.quiz:
        return 0.0, []
    qs = "\n".join(f"{i}. {q.question}" for i, q in enumerate(skill.quiz))
    ans = complete_json(llm, STUDENT_SYSTEM, f"{skill_text(skill)}\n\nQUESTIONS:\n{qs}", ANSWER_SCHEMA)
    student = {a["index"]: a["answer"] for a in ans.get("answers", [])}
    grading = "\n\n".join(f"#{i}\nQ: {q.question}\nReference: {q.answer}\nStudent: {student.get(i, '(none)')}"
                          for i, q in enumerate(skill.quiz))
    judged = complete_json(llm, JUDGE_SYSTEM, grading, JUDGE_SCHEMA)
    points = {"correct": 1.0, "partial": 0.5, "wrong": 0.0}
    rows = []
    total = 0.0
    verdicts = {v["index"]: v for v in judged.get("verdicts", [])}
    for i, q in enumerate(skill.quiz):
        v = verdicts.get(i, {"verdict": "wrong", "reason": "not graded"})
        total += points.get(v["verdict"], 0.0)
        rows.append({"question": q.question, "reference": q.answer, "student": student.get(i, ""),
                     "verdict": v["verdict"], "reason": v.get("reason", "")})
    return round(total / len(skill.quiz), 3), rows


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------

@dataclass
class SkillResult:
    name: str
    status: str
    path: str
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    eval_score: float | None = None
    n_units: int = 0


@dataclass
class DistillReport:
    domain: str
    n_sources: int
    n_units: int
    skills: list[SkillResult]
    work_dir: str

    def to_markdown(self) -> str:
        lines = [f"# Báo cáo chưng cất — {self.domain}", "",
                 f"- Nguồn: {self.n_sources} · Đơn vị kiến thức: {self.n_units} · Skill: {len(self.skills)}",
                 "", "| Skill | Trạng thái | Units | Quiz offline | Lỗi | Cảnh báo |", "|---|---|---|---|---|---|"]
        for s in self.skills:
            score = "—" if s.eval_score is None else f"{s.eval_score:.0%}"
            lines.append(f"| `{s.name}` | {s.status} | {s.n_units} | {score} | {len(s.errors)} | {len(s.warnings)} |")
        for s in self.skills:
            if s.errors or s.warnings:
                lines += ["", f"## {s.name}", *[f"- ❌ {e}" for e in s.errors], *[f"- ⚠️ {w}" for w in s.warnings]]
        return "\n".join(lines) + "\n"


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def distill(docs: list[SourceDoc], llm: Any, wiki: Any, domain: str,
            work_dir: Path | str = "work", lang: str = "vi", workers: int = 4,
            run_eval: bool = True, min_eval: float = 0.7, force: bool = False,
            redo: list[str] | None = None,
            log: Callable[[str], None] = print) -> DistillReport:
    """Full pipeline over a collection of SourceDocs; resumable via work_dir.

    `redo`: skill names to rewrite (and re-quiz) ignoring their cache; "plan" re-plans.
    Lets one bad skill be regenerated without deleting cache files or paying for --force.
    """
    redo_set = set(redo or [])
    domain_slug = slugify(domain, sep="_")
    work = Path(work_dir) / domain_slug
    work.mkdir(parents=True, exist_ok=True)
    docs_by_key = {f"S{i}": d for i, d in enumerate(docs, start=1)}
    _write_json(work / "sources.json", {k: {"doc_id": d.doc_id, "title": d.title, "url": d.url}
                                        for k, d in docs_by_key.items()})

    # ---- map (parallel, cached per section) ----
    jobs = [(key, doc, sec) for key, doc in docs_by_key.items() for sec in doc.sections]

    def run_map(job):
        key, doc, sec = job
        cache = work / "units" / f"{slugify(sec.section_id, sep='_')}.json"
        cached = None if force else _read_json(cache)
        if cached is not None:
            # The same video can be S3 in one collection and S41 in another: re-key
            # cached units, or citations would point at the wrong source.
            return key, sec.section_id, [KnowledgeUnit(**{**u, "source_key": key}) for u in cached]
        units = map_section(llm, doc, sec, key)
        _write_json(cache, [u.model_dump() for u in units])
        log(f"  map {key} {doc.title[:50]} / {sec.title[:30]}: {len(units)} units")
        return key, sec.section_id, units

    log(f"[1/4] Bóc tách {len(jobs)} phần từ {len(docs)} nguồn ...")
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        mapped = list(pool.map(run_map, jobs))
    units: list[KnowledgeUnit] = []
    counters: dict[str, int] = {}
    for key, _, us in mapped:  # stable ids in source order
        for u in us:
            counters[key] = counters.get(key, 0) + 1
            u.unit_id = f"{key}.u{counters[key]}"
            units.append(u)
    _write_json(work / "units.json", [u.model_dump() for u in units])
    if not units:
        raise RuntimeError("No knowledge units extracted — check transcripts/frames in the cache")

    # ---- plan ----
    plan_file = work / "plan.json"
    plan_raw = None if (force or "plan" in redo_set) else _read_json(plan_file)
    if plan_raw and set(plan_raw.get("unit_ids", [])) == {u.unit_id for u in units}:
        plan = [SkillPlanItem(**p) for p in plan_raw["skills"]]
    else:
        log(f"[2/4] Lập kế hoạch skill từ {len(units)} đơn vị kiến thức ...")
        existing = [(m.skill_name, m.description) for m in wiki.all_metadata()
                    if m.kind == "knowledge" and m.domain == domain_slug]
        plan = plan_skills(llm, units, domain_slug,
                           {k: d.title for k, d in docs_by_key.items()}, existing)
        _write_json(plan_file, {"unit_ids": [u.unit_id for u in units],
                                "skills": [p.model_dump() for p in plan]})
    log("      " + ", ".join(f"{p.name}({len(p.unit_ids)})" for p in plan))

    # ---- write + gate + eval (parallel per skill) ----
    def run_skill(item: SkillPlanItem) -> SkillResult:
        cache = work / "skills" / f"{item.name}.json"
        cached = None if (force or item.name in redo_set) else _read_json(cache)
        if cached is not None and cached["skill"]["plan"] == item.model_dump():
            skill = KnowledgeSkill(**cached["skill"])
            score, rows = cached.get("eval_score"), cached.get("eval_rows", [])
        else:
            skill = write_skill(llm, item, units, plan, domain_slug, docs_by_key, lang=lang)
            score, rows = None, []
        errors, warnings = lint_skill(skill, docs_by_key)
        if run_eval and not errors and score is None:
            score, rows = evaluate_skill(llm, skill)
        _write_json(cache, {"skill": skill.model_dump(), "eval_score": score, "eval_rows": rows})
        if score is not None and score < min_eval:
            warnings.append(f"offline quiz score {score:.0%} < {min_eval:.0%}")
        status = "validated" if not errors and (score is None or score >= min_eval) else "draft"
        path = wiki.save_knowledge(skill, status=status, eval_score=score,
                                   gate_issues=errors + warnings)
        if rows:
            _write_json(Path(path) / "eval.json", rows)
        log(f"  {status:9s} {item.name}  units={len(item.unit_ids)} "
            f"quiz={'—' if score is None else f'{score:.0%}'} errors={len(errors)}")
        return SkillResult(item.name, status, str(path), errors, warnings, score, len(item.unit_ids))

    log(f"[3/4] Viết + kiểm định {len(plan)} skill ...")
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        results = list(pool.map(run_skill, plan))

    report = DistillReport(domain_slug, len(docs), len(units), results, str(work))
    (work / "report.md").write_text(report.to_markdown(), encoding="utf-8")
    log(f"[4/4] Xong. Báo cáo: {work / 'report.md'}")
    return report
