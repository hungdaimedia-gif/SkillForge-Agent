"""Generate a PNG image from a text prompt.


Skill contract:
- Params are read as JSON from the LAST sys.argv argument.
- All output files go into the directory given by env var SKILL_OUTPUT_DIR.
- Exit 0 on success, non-zero on error.


Behaviour:
- Self-contained offline renderer using only the Python standard library.
  Artwork is deterministic: derived from SHA-256(prompt + seed).
- Optional provider override: set IMAGE_API_URL (and IMAGE_API_KEY) to call
  a real image-generation API; falls back to the local renderer on failure.
"""
import base64
import hashlib
import json
import math
import os
import struct
import sys
import urllib.request
import zlib
from pathlib import Path




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




def palette(prompt, seed):
    h = hashlib.sha256(f"{prompt}::{seed}".encode("utf-8")).digest()
    return [(h[0], h[1], h[2]), (h[3], h[4], h[5]), (h[6], h[7], h[8])]




def render_row(y, width, height, c1, c2, c3, f1, f2, ph, style, seed):
    v = y / max(height - 1, 1)
    row = bytearray()
    for x in range(width):
        u = x / max(width - 1, 1)
        if style == "noise":
            n = hashlib.sha256(f"{x},{y},{seed}".encode()).digest()[0] / 255.0
            r = int(c1[0] * n + c2[0] * (1 - n))
            g = int(c1[1] * n + c2[1] * (1 - n))
            b = int(c1[2] * n + c2[2] * (1 - n))
        elif style == "checker":
            s = max(8, width // 16)
            pick = c1 if ((x // s) + (y // s)) % 2 == 0 else c2
            k = v * 0.45
            r = int(pick[0] * (1 - k) + c3[0] * k)
            g = int(pick[1] * (1 - k) + c3[0] * k)
            b = int(pick[2] * (1 - k) + c3[2] * k)
        else:  # gradient (default)
            wave = math.sin(u * f1 * 6.28318 + ph) * math.cos(v * f2 * 3.14159 + ph * 0.5)
            t = min(1.0, max(0.0, v * 0.75 + wave * 0.25 + 0.125))
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            edge = abs(u - 0.5) + abs(v - 0.5)  # 0..1
            r = int(r * (1 - edge * 0.3) + c3[0] * edge * 0.3)
            g = int(g * (1 - edge * 0.3) + c3[1] * edge * 0.3)
            b = int(b * (1 - edge * 0.3) + c3[2] * edge * 0.3)
        row += bytes((max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))
    return bytes(row)




def write_png(path, width, height, rows):
    def chunk(ctype, data):
        c = struct.pack(">I", len(data)) + ctype + data
        return c + struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)


    raw = b"".join(b"\x00" + r for r in rows)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))
    Path(path).write_bytes(png)




def try_provider(api_url, api_key, prompt, width, height, out_path):
    """Best-effort provider call. Returns True if it produced the image."""
    payload = json.dumps({"prompt": prompt, "width": width, "height": height}).encode()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(api_url, data=payload, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read()
        ctype = resp.headers.get("Content-Type", "")
    if ctype.startswith("image/"):
        Path(out_path).write_bytes(body)
        return True
    try:
        data = json.loads(body.decode("utf-8", "ignore"))
    except Exception:
        return False
    if isinstance(data, dict):
        if data.get("image_b64"):
            Path(out_path).write_bytes(base64.b64decode(data["image_b64"]))
            return True
        url = data.get("image_url") or data.get("url")
        if url:
            with urllib.request.urlopen(url, timeout=120) as r2:
                Path(out_path).write_bytes(r2.read())
            return True
    return False




def main():
    p = parse_params()
    prompt = str(p.get("prompt", "a serene landscape"))
    width = clamp_int(p.get("width", 512), 512, 16, 2048)
    height = clamp_int(p.get("height", 512), 512, 16, 2048)
    style = str(p.get("style", "gradient")).lower()
    if style not in ("gradient", "noise", "checker"):
        style = "gradient"
    seed = p.get("seed", 0)


    out_dir = Path(os.environ.get("SKILL_OUTPUT_DIR", "."))
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "image.png"


    api_url = os.environ.get("IMAGE_API_URL", "") or str(p.get("api_url", ""))
    api_key = os.environ.get("IMAGE_API_KEY", "") or str(p.get("api_key", ""))
    if api_url:
        try:
            if try_provider(api_url, api_key, prompt, width, height, out_path):
                print(out_path)
                return 0
        except Exception as e:  # noqa: BLE001 - provider is best-effort
            print(f"provider failed ({e}), using local renderer", file=sys.stderr)


    c1, c2, c3 = palette(prompt, seed)
    fh = hashlib.sha256(f"{prompt}::{seed}::freq".encode()).digest()
    f1, f2 = 1 + (fh[0] % 5), 1 + (fh[1] % 5)
    ph = (fh[2] / 255.0) * math.pi * 2
    rows = [render_row(y, width, height, c1, c2, c3, f1, f2, ph, style, seed)
            for y in range(height)]
    write_png(out_path, width, height, rows)
    print(out_path)
    return 0




if __name__ == "__main__":
    sys.exit(main())