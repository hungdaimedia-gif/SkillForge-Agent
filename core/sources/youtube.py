"""YouTube acquisition: playlist listing, transcript (subs or whisper), keyframes.

Adapted in spirit from Microsoft Resource2Skill (MIT) `core/collector.py` +
`core/analyzer.py` (yt-dlp search, ffmpeg keyframes). Resource2Skill hands the
URL straight to Gemini; Claude cannot watch a URL, so here we pull the
transcript and frames ourselves and cache them on disk. Re-running is free:
every step skips work whose output already exists.

No LLM is used in this module.
"""
from __future__ import annotations

import json
import logging
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from ..models import Frame, Segment, SourceDoc, SourceSection
from ..text import fmt_ts

logger = logging.getLogger("skillforge.sources.youtube")

CACHE_VERSION = 3  # bump when doc.json layout/logic changes; old caches are rebuilt
SUB_CLIENTS = ([], ["--extractor-args", "youtube:player_client=android"],
               ["--extractor-args", "youtube:player_client=web_safari,tv"])
VIDEO_HEIGHT = int(os.environ.get("SKILLFORGE_VIDEO_HEIGHT", "720"))
_VIDEO_ID = re.compile(r"(?:v=|youtu\.be/|shorts/|embed/)([A-Za-z0-9_-]{11})")


def _tool(env_var: str, name: str) -> list[str]:
    explicit = os.environ.get(env_var)
    if explicit:
        return [explicit]
    if name == "yt-dlp":
        # Prefer the project's own (pinned, updatable) yt-dlp: a stale copy elsewhere
        # on PATH gets HTTP 403 from YouTube when downloading video data.
        try:
            import yt_dlp  # noqa: F401
            return [sys.executable, "-m", "yt_dlp"]
        except ImportError:
            pass
    found = shutil.which(name)
    if found:
        return [found]
    raise RuntimeError(f"{name} not found (install it or set {env_var})")


def _run(cmd: list[str], timeout: int = 900) -> subprocess.CompletedProcess:
    logger.debug("exec: %s", " ".join(cmd[:6]))
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)


def ytdlp(*args: str, timeout: int = 900) -> subprocess.CompletedProcess:
    return _run([*_tool("SKILLFORGE_YTDLP", "yt-dlp"), "--no-update", "--no-warnings", *args],
                timeout=timeout)


def is_youtube_url(value: str) -> bool:
    return "youtube.com" in value or "youtu.be" in value


def video_id(url_or_id: str) -> str:
    m = _VIDEO_ID.search(url_or_id)
    if m:
        return m.group(1)
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", url_or_id):
        return url_or_id
    raise ValueError(f"Not a YouTube video URL/id: {url_or_id}")


def list_videos(url: str) -> list[dict[str, Any]]:
    """Playlist/channel/single video -> [{id, title, url, duration}] in playlist order."""
    if "list=" not in url and "/@" not in url and "/channel/" not in url:
        vid = video_id(url)
        return [{"id": vid, "title": "", "url": f"https://www.youtube.com/watch?v={vid}",
                 "duration": None, "index": 1}]
    proc = ytdlp("--flat-playlist", "-J", url, timeout=300)
    if proc.returncode != 0:
        raise RuntimeError(f"yt-dlp failed listing {url}: {proc.stderr[:400]}")
    data = json.loads(proc.stdout)
    out = []
    for i, e in enumerate(data.get("entries") or [], start=1):
        if not e or not e.get("id"):
            continue
        out.append({"id": e["id"], "title": e.get("title") or "",
                    "url": f"https://www.youtube.com/watch?v={e['id']}",
                    "duration": e.get("duration"), "index": i,
                    "playlist_title": data.get("title") or ""})
    return out


# ---------------------------------------------------------------------------
# Transcript
# ---------------------------------------------------------------------------

def parse_json3(path: Path) -> list[Segment]:
    """YouTube json3 captions -> timed segments (one per caption event)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    segs: list[Segment] = []
    for ev in data.get("events") or []:
        pieces = ev.get("segs")
        if not pieces:
            continue
        text = "".join(p.get("utf8", "") for p in pieces).replace("\n", " ").strip()
        if not text:
            continue
        start = ev.get("tStartMs", 0) / 1000.0
        end = start + ev.get("dDurationMs", 0) / 1000.0
        segs.append(Segment(anchor=fmt_ts(start), text=text, start_s=start, end_s=end))
    return _dedupe_rolling(segs)


def _dedupe_rolling(segs: list[Segment]) -> list[Segment]:
    """Auto-captions repeat the previous line while scrolling; drop exact repeats."""
    out: list[Segment] = []
    for s in segs:
        if out and s.text == out[-1].text:
            out[-1].end_s = s.end_s
            continue
        out.append(s)
    return out


def merge_segments(segs: list[Segment], window_s: float = 12.0) -> list[Segment]:
    """Group caption events into ~window_s blocks so prompts stay compact but timed."""
    merged: list[Segment] = []
    cur: list[Segment] = []
    for s in segs:
        if cur and (s.start_s or 0) - (cur[0].start_s or 0) >= window_s:
            merged.append(_join(cur))
            cur = []
        cur.append(s)
    if cur:
        merged.append(_join(cur))
    return merged


def _join(group: list[Segment]) -> Segment:
    return Segment(anchor=group[0].anchor, text=" ".join(g.text for g in group),
                   start_s=group[0].start_s, end_s=group[-1].end_s)


def _pick_sub_file(vdir: Path, lang: str, stem: str = "subs") -> tuple[Path | None, str]:
    """Pick the caption file closest to the requested language."""
    files = sorted(vdir.glob(f"{stem}.*.json3"))
    if not files:
        return None, ""
    def rank(p: Path) -> tuple[int, int]:
        code = p.name.split(".")[1]
        return (0 if code == lang else 1 if code.startswith(lang) else 2, len(code))
    best = min(files, key=rank)
    return best, best.name.split(".")[1]


def fetch_transcript(url: str, vdir: Path, info: dict, lang: str = "en",
                     whisper: bool = True) -> tuple[list[Segment], str]:
    manual = info.get("subtitles") or {}
    auto = info.get("automatic_captions") or {}
    has_manual = any(k == lang or k.startswith(lang + "-") for k in manual)
    has_auto = any(k == lang or k.startswith(lang + "-") for k in auto)
    best: tuple[list[Segment], str] = ([], "none")
    for flag, label, available in (("--write-subs", "manual_subs", has_manual),
                                   ("--write-auto-subs", "auto_subs", has_auto)):
        if not available:
            continue
        stem = "msubs" if label == "manual_subs" else "asubs"
        sub_file, code = _pick_sub_file(vdir, lang, stem)
        if sub_file is None:
            # YouTube answers HTTP 429 for caption requests after many videos in a row
            # (2026-10-14, playlist of 93); the android client still serves captions in
            # seconds, so retry with other clients before paying minutes of whisper CPU.
            for i, client_args in enumerate(SUB_CLIENTS):
                if i:
                    time.sleep(2)
                ytdlp(*client_args, flag, "--sub-langs", f"{lang},{lang}-orig,{lang}.*",
                      "--sub-format", "json3", "--skip-download",
                      "-o", str(vdir / f"{stem}.%(ext)s"), url, timeout=300)
                sub_file, code = _pick_sub_file(vdir, lang, stem)
                if sub_file is not None:
                    break
        if sub_file is None:
            continue
        segs = parse_json3(sub_file)
        # Some "manual" tracks are just a caption of on-screen text (one line for a
        # 2-minute video): keep looking at auto captions when the track is that thin.
        if sum(len(s.text) for s in segs) > sum(len(s.text) for s in best[0]):
            best = (segs, f"{label}:{code}")
        if sum(len(s.text) for s in segs) >= 300:
            break
    if best[0]:
        return best
    if whisper:
        segs = _whisper(url, vdir, lang)
        if segs:
            return segs, "whisper"
    return [], "none"


def _whisper(url: str, vdir: Path, lang: str) -> list[Segment]:
    out_json = vdir / "audio.json"
    if not out_json.exists():
        try:
            whisper_bin = _tool("SKILLFORGE_WHISPER", "whisper")
        except RuntimeError:
            logger.warning("No subtitles and whisper is not installed: %s", url)
            return []
        audio = vdir / "audio.m4a"
        if not audio.exists():
            ytdlp("-f", "bestaudio[ext=m4a]/bestaudio", "-o", str(audio), url)
        model = os.environ.get("SKILLFORGE_WHISPER_MODEL", "small")
        _run([*whisper_bin, str(audio), "--model", model, "--language", lang,
              "--output_format", "json", "--output_dir", str(vdir)], timeout=3600)
    if not out_json.exists():
        return []
    data = json.loads(out_json.read_text(encoding="utf-8"))
    return [Segment(anchor=fmt_ts(s["start"]), text=s["text"].strip(),
                    start_s=s["start"], end_s=s["end"])
            for s in data.get("segments", []) if s.get("text", "").strip()]


# ---------------------------------------------------------------------------
# Keyframes
# ---------------------------------------------------------------------------

def frame_times(duration: float, chapters: list[dict], max_frames: int,
                min_gap: float = 4.0) -> list[tuple[float, str]]:
    """Chapter starts first (they show the new topic), then uniform fill."""
    if duration <= 0 or max_frames <= 0:
        return []
    picks: list[tuple[float, str]] = []
    for ch in chapters:
        t = float(ch.get("start_time") or 0) + 2.0
        if t < duration - 1:
            picks.append((t, "chapter"))
    n_uniform = max(0, max_frames - len(picks))
    if n_uniform:
        step = duration / (n_uniform + 1)
        picks += [(step * (i + 1), "uniform") for i in range(n_uniform)]
    # Chapter frames win over a nearby uniform frame (they show the new topic).
    kept: list[tuple[float, str]] = []
    for t, why in picks:  # chapters come first in `picks`
        if len(kept) >= max_frames or any(abs(t - k) < min_gap for k, _ in kept):
            continue
        kept.append((round(t, 1), why))
    return sorted(kept)


def extract_frames(url: str, vdir: Path, duration: float, chapters: list[dict],
                   max_frames: int) -> list[Frame]:
    times = frame_times(duration, chapters, max_frames)
    if not times:
        return []
    h = VIDEO_HEIGHT
    fdir = vdir / f"frames_{h}p"
    fdir.mkdir(exist_ok=True)
    wanted = [(t, why, fdir / f"f{int(t * 10):06d}.jpg") for t, why in times]
    if any(not p.exists() for _, _, p in wanted):
        video = next(iter(sorted(vdir.glob(f"video_{h}p.*"))), None)
        if video is None:
            # Video-only stream: frames need no audio. 360p is too small to read UI
            # labels/hotkey overlays (and YouTube often offers no 480p at all).
            # YouTube intermittently answers 403 for one player client; retry with others.
            for client_args in ([], ["--extractor-args", "youtube:player_client=web_safari,tv"],
                                ["--extractor-args", "youtube:player_client=ios,mweb"]):
                ytdlp(*client_args, "-f", f"bv*[height<={h}][ext=mp4]/bv*[height<={h}]/b[height<={h}]/b",
                      "-o", str(vdir / f"video_{h}p.%(ext)s"), url, timeout=1800)
                video = next(iter(sorted(vdir.glob(f"video_{h}p.*"))), None)
                if video is not None:
                    break
        if video is None:
            logger.warning("Could not download video for frames: %s", url)
            return []
        ffmpeg = _tool("SKILLFORGE_FFMPEG", "ffmpeg")
        for t, _, path in wanted:
            if not path.exists():
                _run([*ffmpeg, "-y", "-loglevel", "error", "-ss", f"{t}", "-i", str(video),
                      "-frames:v", "1", "-vf", "scale='min(1280,iw)':-2", "-q:v", "3", str(path)],
                     timeout=120)
    return [Frame(frame_id=p.stem, path=str(p.resolve()), t_s=t, reason=why)
            for t, why, p in wanted if p.exists()]


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def fetch_video(url_or_id: str, cache_dir: Path | str = "sources_cache", lang: str = "en",
                max_frames: int = 10, frames: bool = True, whisper: bool = True,
                merge_window_s: float = 12.0) -> SourceDoc:
    """Fetch one video into a SourceDoc (cached under cache_dir/youtube/<id>/)."""
    vid = video_id(url_or_id)
    url = f"https://www.youtube.com/watch?v={vid}"
    vdir = Path(cache_dir) / "youtube" / vid
    vdir.mkdir(parents=True, exist_ok=True)

    doc_file = vdir / "doc.json"
    if doc_file.exists():
        doc = SourceDoc.model_validate_json(doc_file.read_text(encoding="utf-8"))
        has_frames = any(s.frames for s in doc.sections)
        if doc.extras.get("cache_version") == CACHE_VERSION and (
                not frames or (doc.extras.get("max_frames") == max_frames and has_frames)):
            return doc

    info_file = vdir / "info.json"
    if not info_file.exists():
        proc = ytdlp("-J", "--skip-download", url, timeout=300)
        if proc.returncode != 0:
            raise RuntimeError(f"yt-dlp failed for {url}: {proc.stderr[:400]}")
        info_file.write_text(proc.stdout, encoding="utf-8")
    info = json.loads(info_file.read_text(encoding="utf-8"))

    raw_segs, transcript_source = fetch_transcript(url, vdir, info, lang=lang, whisper=whisper)
    segs = merge_segments(raw_segs, merge_window_s)
    duration = float(info.get("duration") or (segs[-1].end_s if segs else 0) or 0)
    chapters = [c for c in (info.get("chapters") or []) if c.get("start_time") is not None]
    # UI tutorials change screen every few seconds: ~1 frame / 15 s, at least 6, capped.
    # Little or no narration (music + on-screen text) -> the frames ARE the content.
    spoken = sum(len(s.text) for s in raw_segs)
    per = 6 if spoken < 400 else 15
    n_frames = min(max_frames, max(6, int(duration / per)))
    frame_list = extract_frames(url, vdir, duration, chapters, n_frames) if frames else []

    sections = _split_sections(vid, segs, frame_list, chapters, duration)
    doc = SourceDoc(
        doc_id=vid, kind="youtube", title=info.get("title") or vid, url=url,
        author=info.get("channel") or info.get("uploader") or "",
        # YouTube rarely states reuse rights; keep the Resource2Skill convention.
        license="creative_commons" if "creative commons" in str(info.get("license", "")).lower()
        else "youtube_review_pending",
        language=lang, transcript_source=transcript_source, sections=sections,
        extras={"duration_s": duration, "upload_date": info.get("upload_date"),
                "description": (info.get("description") or "")[:2000],
                "max_frames": max_frames, "cache_version": CACHE_VERSION},
    )
    doc_file.write_text(doc.model_dump_json(indent=2), encoding="utf-8")
    return doc


def _split_sections(vid: str, segs: list[Segment], frames: list[Frame],
                    chapters: list[dict], duration: float) -> list[SourceSection]:
    """Short tutorials -> one section; long ones split by chapter (or ~10 min)."""
    bounds: list[tuple[float, float, str]]
    if duration > 900 and chapters:
        bounds = [(float(c["start_time"]), float(c.get("end_time") or duration),
                   c.get("title") or f"Part {i + 1}") for i, c in enumerate(chapters)]
    elif duration > 900:
        step = 600.0
        bounds = [(s, min(s + step, duration), f"{fmt_ts(s)}–{fmt_ts(min(s + step, duration))}")
                  for s in [i * step for i in range(int(duration // step) + 1)] if s < duration]
    else:
        bounds = [(0.0, max(duration, 1e9), "full video")]
    sections = []
    for i, (a, b, title) in enumerate(bounds):
        sections.append(SourceSection(
            section_id=f"{vid}#{i}", title=title,
            segments=[s for s in segs if a <= (s.start_s or 0) < b],
            frames=[f for f in frames if a <= f.t_s < b],
        ))
    return [s for s in sections if s.segments or s.frames]
