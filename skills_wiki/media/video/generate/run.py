"""Generate a short MP4 video clip from a text prompt.


Skill contract:
- Params are read as JSON from the LAST sys.argv argument.
- All output files go into the directory given by env var SKILL_OUTPUT_DIR.
- Exit 0 on success, non-zero on error.


Providers (param "provider", default "auto"):
- "minimax": real AI video via a MiniMax-compatible API (the same protocol
  used by HungDai-Flow-Director's metaso provider). Configure with
  VIDEO_API_URL (default https://metaso.cn/api/minimax) and VIDEO_API_KEY
  (or MINIMAX_API_KEY). Submits an async task and polls until done.
- "local": procedural animation rendered locally and encoded with ffmpeg.
  Requires ffmpeg. Fully offline, no API key needed.
- "auto": use "minimax" when an API URL + key are configured, else "local".
"""
import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


DEFAULT_API_URL = "https://metaso.cn/api/minimax"
POLL_INTERVAL_S = 5
MAX_WAIT_S = 10 * 60




def parse_params():
    raw = sys.argv[-1] if len(sys.argv) > 1 else ""
    try:
        p = json.loads(raw) if raw.startswith("{") else {}
    except Exception:
        p = {}
    return p if isinstance(p, dict) else {}




def clamp_int(v, default, lo, hi):
    try:
        v = int(v)
    except (TypeError, ValueError):
        v = default
    return max(lo, min(hi, v))




def clamp_float(v, default, lo, hi):
    try:
        v = float(v)
    except (TypeError, ValueError):
        v = default
    return max(lo, min(hi, v))




def http_json(url, api_key, payload=None, timeout=60):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Authorization": f"Bearer {api_key}"}
    if data is not None:
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", "ignore"))




def minimax_generate(api_url, api_key, model, prompt, duration_s, resolution, ratio, out_path):
    """MiniMax-compatible async video generation (metaso.cn protocol)."""
    base = api_url.rstrip("/")
    submit = http_json(
        f"{base}/v2/video_generation", api_key,
        {"model": model, "duration": int(duration_s), "resolution": resolution,
         "ratio": ratio, "content": [{"type": "text", "text": prompt}]},
        timeout=60,
    )
    task_id = submit.get("task_id")
    if not task_id:
        raise RuntimeError(f"task submit returned no task_id: {submit}")


    deadline = time.time() + MAX_WAIT_S
    while True:
        data = http_json(f"{base}/v2/query/video_generation/{task_id}", api_key, timeout=30)
        task = (data.get("task") or {})
        status = task.get("status")
        if status == "succeeded":
            video_url = ((task.get("content") or {}).get("url"))
            if not video_url:
                raise RuntimeError(f"task succeeded but no content url: {data}")
            req = urllib.request.Request(video_url)
            with urllib.request.urlopen(req, timeout=600) as r, open(out_path, "wb") as f:
                f.write(r.read())
            return
        if status == "failed":
            raise RuntimeError(f"video task failed: {data}")
        if time.time() > deadline:
            raise RuntimeError(f"video task {task_id} timed out after {MAX_WAIT_S}s")
        time.sleep(POLL_INTERVAL_S)




def frame_bytes(width, height, c1, c2, c3, f1, f2, ph, t01):
    phase = t01 * 2 * math.pi
    buf = bytearray()
    for y in range(height):
        v = y / max(height - 1, 1)
        for x in range(width):
            u = x / max(width - 1, 1)
            wave = math.sin(u * f1 * 6.28318 + ph + phase) * math.cos(v * f2 * 3.14159 + phase * 0.7)
            t = min(1.0, max(0.0, v * 0.7 + wave * 0.3 + 0.15))
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            edge = abs(u - 0.5) + abs(v - 0.5)
            r = int(r * (1 - edge * 0.3) + c3[0] * edge * 0.3)
            g = int(g * (1 - edge * 0.3) + c3[1] * edge * 0.3)
            b = int(b * (1 - edge * 0.3) + c3[2] * edge * 0.3)
            buf += bytes((max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))
    return bytes(buf)




def encode_with_ffmpeg(ffmpeg, width, height, fps, duration_s, frames_iter, out_path):
    for codec in ("libx264", "mpeg4"):
        cmd = [ffmpeg, "-y",
               "-f", "rawvideo", "-pix_fmt", "rgb24",
               "-s", f"{width}x{height}", "-r", str(fps),
               "-i", "-",
               "-an", "-c:v", codec, "-pix_fmt", "yuv420p",
               "-t", str(duration_s), str(out_path)]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for frame in frames_iter():
                proc.stdin.write(frame)
            proc.stdin.close()
        except BrokenPipeError:
            pass
        if proc.wait() == 0 and Path(out_path).stat().st_size > 0:
            return True
    return False




def local_generate(prompt, seed, duration_s, fps, width, height, out_path):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found: install ffmpeg or configure a video API provider")
    h = hashlib.sha256(f"{prompt}::{seed}".encode("utf-8")).digest()
    c1, c2, c3 = (h[0], h[1], h[2]), (h[3], h[4], h[5]), (h[6], h[7], h[8])
    fh = hashlib.sha256(f"{prompt}::{seed}::freq".encode()).digest()
    f1, f2 = 1 + (fh[0] % 5), 1 + (fh[1] % 5)
    ph = (fh[2] / 255.0) * math.pi * 2
    n_frames = max(1, int(duration_s * fps))


    def frames():
        for i in range(n_frames):
            yield frame_bytes(width, height, c1, c2, c3, f1, f2, ph, i / n_frames)


    if not encode_with_ffmpeg(ffmpeg, width, height, fps, duration_s, frames, out_path):
        raise RuntimeError("ffmpeg encoding failed")




def main():
    p = parse_params()
    prompt = str(p.get("prompt", "ocean waves"))
    provider = str(p.get("provider", "auto")).lower()
    if provider not in ("auto", "minimax", "local"):
        provider = "auto"
    model = str(p.get("model", "MiniMax-H3"))
    resolution = str(p.get("resolution", "768P"))
    ratio = p.get("ratio")  # e.g. "16:9", optional
    duration_s = clamp_float(p.get("duration_s", 3), 3, 0.5, 15)
    fps = clamp_int(p.get("fps", 12), 12, 1, 30)
    width = clamp_int(p.get("width", 480), 480, 64, 1280)
    height = clamp_int(p.get("height", 480), 480, 64, 1280)
    width -= width % 2  # yuv420p needs even dimensions
    height -= height % 2
    seed = p.get("seed", 0)


    out_dir = Path(os.environ.get("SKILL_OUTPUT_DIR", "."))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "output.mp4"


    api_url = (os.environ.get("VIDEO_API_URL", "") or str(p.get("api_url", ""))).strip()
    api_key = (os.environ.get("VIDEO_API_KEY", "") or os.environ.get("MINIMAX_API_KEY", "")
               or str(p.get("api_key", ""))).strip()
    want_minimax = provider == "minimax" or (provider == "auto" and api_url and api_key)
    if provider == "minimax" and not api_url:
        api_url = DEFAULT_API_URL


    if want_minimax:
        if not api_key:
            msg = "provider=minimax needs VIDEO_API_KEY (or MINIMAX_API_KEY)"
            if provider == "minimax":
                print(f"ERROR: {msg}", file=sys.stderr)
                return 1
            print(f"warning: {msg}; falling back to local", file=sys.stderr)
        else:
            try:
                minimax_generate(api_url or DEFAULT_API_URL, api_key, model, prompt,
                                 duration_s, resolution, ratio, out_path)
                print(out_path)
                return 0
            except Exception as e:  # noqa: BLE001
                if provider == "minimax":
                    print(f"ERROR: minimax provider failed: {e}", file=sys.stderr)
                    return 1
                print(f"warning: minimax provider failed ({e}); falling back to local",
                      file=sys.stderr)


    try:
        local_generate(prompt, seed, duration_s, fps, width, height, out_path)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    print(out_path)
    return 0




if __name__ == "__main__":
    sys.exit(main())