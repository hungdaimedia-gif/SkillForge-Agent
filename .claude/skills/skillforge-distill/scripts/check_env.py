"""Check everything `skillforge fetch/distill` needs. Read-only: installs and deletes nothing.

Usage (from the repo root, with the project's venv Python):
    .venv/Scripts/python.exe .claude/skills/skillforge-distill/scripts/check_env.py [--ping]

--ping makes one tiny real LLM call to prove the backend is logged in (costs a few tokens).
Exit code 0 = ready to distill, 1 = something blocking is missing.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

OK, WARN, BAD = "✅", "⚠️ ", "❌"


def find_repo(explicit: str | None) -> Path:
    """--repo > $SKILLFORGE_HOME > repo containing this skill > current directory.

    The skill also ships in a shared skills library, far from the repo, so the
    location cannot be derived from __file__ alone.
    """
    candidates = [explicit, os.environ.get("SKILLFORGE_HOME"),
                  str(Path(__file__).resolve().parents[4]), os.getcwd()]
    for c in candidates:
        if c and (Path(c) / "skillforge_cli.py").exists():
            return Path(c).resolve()
    return Path(explicit or os.environ.get("SKILLFORGE_HOME") or os.getcwd()).resolve()


def has_module(name: str) -> bool:
    return importlib.util.find_spec(name) is not None


def version_of(cmd: list[str]) -> str | None:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (out.stdout or out.stderr).strip().splitlines()
    return text[0][:80] if out.returncode == 0 and text else None


def ping_claude_cli(bin_path: str) -> tuple[bool, str]:
    try:
        out = subprocess.run([bin_path, "-p", "--output-format", "json", "--tools", "",
                              "--no-session-persistence"], input="Reply with: ok",
                             capture_output=True, text=True, encoding="utf-8", timeout=180)
        data = json.loads(out.stdout)
    except Exception as exc:  # noqa: BLE001 - report any failure as text
        return False, str(exc)[:160]
    if data.get("is_error"):
        return False, str(data.get("result"))[:160]
    return True, "logged in"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ping", action="store_true", help="make one tiny real LLM call")
    ap.add_argument("--repo", help="SkillForge-Agent checkout (default: $SKILLFORGE_HOME or cwd)")
    args = ap.parse_args()
    global REPO
    REPO = find_repo(args.repo)
    # Windows consoles default to cp1252 and crash on ✅/tiếng Việt.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    blocking = False
    rows: list[tuple[str, str, str]] = []

    def add(status: str, item: str, detail: str, block: bool = False) -> None:
        nonlocal blocking
        rows.append((status, item, detail))
        blocking |= block and status == BAD

    add(OK if sys.version_info >= (3, 10) else BAD, "Python >= 3.10",
        f"{sys.version.split()[0]} ({sys.executable})", block=True)
    in_venv = sys.prefix != sys.base_prefix
    add(OK if in_venv else WARN, "Đang dùng venv", sys.prefix if in_venv else "nên chạy bằng .venv của dự án")
    add(OK if (REPO / "skillforge_cli.py").exists() else BAD, "Repo SkillForge",
        str(REPO) if (REPO / "skillforge_cli.py").exists() else
        f"không thấy skillforge_cli.py ở {REPO} ⇒ clone repo, đặt SKILLFORGE_HOME hoặc --repo", block=True)

    for mod, why in (("pydantic", "lõi"), ("mcp", "MCP server")):
        add(OK if has_module(mod) else BAD, f"python: {mod}", why, block=True)
    add(OK if has_module("yt_dlp") else WARN, "python: yt_dlp",
        "YouTube" if has_module("yt_dlp") else "thiếu ⇒ `pip install -U yt-dlp` vào venv (bản trên PATH hay bị 403)")
    add(OK if has_module("fitz") or has_module("pypdf") else WARN, "python: pymupdf/pypdf",
        "đọc PDF" if has_module("fitz") or has_module("pypdf") else "chỉ cần khi chưng cất PDF")

    ytdlp = version_of([sys.executable, "-m", "yt_dlp", "--version"]) if has_module("yt_dlp") else \
        version_of([os.environ.get("SKILLFORGE_YTDLP") or shutil.which("yt-dlp") or "yt-dlp", "--version"])
    add(OK if ytdlp else BAD, "yt-dlp chạy được", ytdlp or "không chạy được (chỉ chặn khi dùng YouTube)")
    ffmpeg = os.environ.get("SKILLFORGE_FFMPEG") or shutil.which("ffmpeg")
    add(OK if ffmpeg else WARN, "ffmpeg", ffmpeg or "thiếu ⇒ không cắt được keyframe")
    whisper = os.environ.get("SKILLFORGE_WHISPER") or shutil.which("whisper")
    add(OK if whisper else WARN, "whisper (tuỳ chọn)", whisper or "chỉ cần cho video không có phụ đề")

    backend = os.environ.get("SKILLFORGE_LLM", "auto")
    api_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    claude_bin = os.environ.get("SKILLFORGE_CLAUDE_BIN") or shutil.which("claude")
    if api_key:
        add(OK if has_module("anthropic") else BAD, "LLM: API",
            "ANTHROPIC_API_KEY đã đặt" + ("" if has_module("anthropic") else " nhưng thiếu `pip install anthropic`"),
            block=backend in ("auto", "api"))
    elif backend == "api":
        add(BAD, "LLM: API", "SKILLFORGE_LLM=api nhưng chưa đặt ANTHROPIC_API_KEY", block=True)
    if not api_key or backend == "claude-cli":
        if not claude_bin:
            add(BAD, "LLM: claude CLI", "không có API key và không tìm thấy `claude`", block=True)
        elif args.ping:
            ok, detail = ping_claude_cli(claude_bin)
            add(OK if ok else BAD, "LLM: claude CLI", detail if ok else
                f"{detail} ⇒ mở `claude`, gõ /login", block=True)
        else:
            add(WARN, "LLM: claude CLI", f"{claude_bin} — chưa kiểm tra đăng nhập (thêm --ping)")

    free_gb = shutil.disk_usage(REPO).free / 1e9
    add(OK if free_gb > 5 else WARN, "Dung lượng trống", f"{free_gb:.1f} GB (video 720p ~5–15 MB/phút)")

    width = max(len(r[1]) for r in rows)
    for status, item, detail in rows:
        print(f"{status} {item:<{width}}  {detail}")
    print("\n" + ("❌ Chưa sẵn sàng — sửa các dòng ❌ ở trên." if blocking
                  else "✅ Sẵn sàng chưng cất." + ("" if args.ping or api_key else
                                                 " (Chưa chứng minh đăng nhập LLM — chạy lại với --ping.)")))
    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
