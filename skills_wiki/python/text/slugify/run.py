import json, os, re, sys, unicodedata
from pathlib import Path

p = json.loads(sys.argv[-1]) if len(sys.argv) > 1 else {}
text = p.get("text", "Hello World")
sep = p.get("separator", "-")
s = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
slug = re.sub(r"[^a-z0-9]+", sep, s).strip(sep)
Path(os.environ["SKILL_OUTPUT_DIR"], "slug.txt").write_text(slug)
print(slug)
