"""Tiny client for Cascadeur's built-in MCP script server (Scripts > MCP > Start script server).

Works for any agent that can run Python — no MCP client needed. Standard library only.

  python casc.py health
  python casc.py run "print(scene.get_current_frame())"
  python casc.py run --file my_script.py
  python casc.py shot out.png [--frame 30] [--width 960]   # screenshot of the viewport area

Exit code: 0 ok, 1 script error, 2 server not running / unreachable.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.request

BASE = "http://127.0.0.1:8765"

# Grabbing the window needs the screen grab path: QWindow has no grabWindow() in
# Cascadeur's PySide6 build (AttributeError seen 2026-10-14).
SHOT_CODE = r'''
from PySide6.QtGui import QGuiApplication
_w = max((w for w in QGuiApplication.instance().topLevelWindows() if w.isVisible()),
         key=lambda w: w.width() * w.height())
_img = _w.screen().grabWindow(_w.winId()).toImage()
# Viewport area of the default layout: below toolbar/tabs, left of Outliner, above timeline.
_vp = _img.copy(0, int(_img.height() * 0.07), int(_img.width() * 0.725), int(_img.height() * 0.80))
print(_vp.scaledToWidth({width}).save(r"{path}"))
'''


def post(path: str, payload: dict, timeout: float = 60) -> dict:
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def run(code: str, timeout: float = 60) -> dict:
    """Run code inside Cascadeur (next scene_idle). Namespace: csc, scene, app."""
    return post("/run", {"code": code}, timeout)


def health() -> dict:
    with urllib.request.urlopen(BASE + "/health", timeout=5) as r:
        return json.loads(r.read().decode("utf-8"))


def screenshot(path: str, frame: int | None = None, width: int = 960) -> dict:
    if frame is not None:
        res = run(f"scene.set_current_frame({int(frame)})")
        if not res.get("ok"):
            return res
        time.sleep(0.8)  # let Cascadeur redraw before grabbing
    return run(SHOT_CODE.format(path=path.replace("\\", "/"), width=int(width)))


def _print(res: dict) -> int:
    for m in res.get("messages", []):
        print(f"[{m.get('level')}] {m.get('text')}")
    if res.get("value"):
        print(res["value"])
    if not res.get("ok"):
        print(res.get("error", "unknown error"), file=sys.stderr)
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("health")
    p_run = sub.add_parser("run")
    p_run.add_argument("code", nargs="?")
    p_run.add_argument("--file")
    p_run.add_argument("--timeout", type=float, default=60)
    p_shot = sub.add_parser("shot")
    p_shot.add_argument("path")
    p_shot.add_argument("--frame", type=int)
    p_shot.add_argument("--width", type=int, default=960)
    args = ap.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    try:
        if args.cmd == "health":
            print(json.dumps(health()))
            return 0
        if args.cmd == "run":
            code = open(args.file, encoding="utf-8").read() if args.file else (args.code or sys.stdin.read())
            return _print(run(code, args.timeout))
        return _print(screenshot(args.path, args.frame, args.width))
    except (urllib.error.URLError, ConnectionError, TimeoutError) as exc:
        print(f"Cascadeur MCP server unreachable at {BASE}: {exc}\n"
              "Open Cascadeur, then Scripts > MCP > Start script server.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
