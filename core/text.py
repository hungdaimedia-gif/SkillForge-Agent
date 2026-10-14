"""Text helpers shared by indexer and distillation (Unicode/Vietnamese aware)."""
from __future__ import annotations

import re
import unicodedata

_WORD_RE = re.compile(r"[a-z0-9]+")


def fold(text: str) -> str:
    """Lowercase and strip diacritics so 'Chào Thế Giới' matches 'chao the gioi'.

    The old ASCII-only tokenizer split 'chào' into 'ch' + 'o', which made
    Vietnamese queries useless. 'đ' has no decomposition, so map it by hand.
    """
    text = text.lower().replace("đ", "d")
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def tokenize(text: str) -> list[str]:
    """Diacritic-folded alphanumeric tokens."""
    return _WORD_RE.findall(fold(text))


def slugify(text: str, sep: str = "-", max_len: int = 64) -> str:
    """ASCII slug usable as a skill name or taxonomy segment."""
    slug = sep.join(tokenize(text))
    return slug[:max_len].strip(sep) or "skill"


def fmt_ts(seconds: float) -> str:
    """Seconds -> 'm:ss' (or 'h:mm:ss')."""
    s = int(max(0, seconds))
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}:{m:02d}:{sec:02d}" if h else f"{m}:{sec:02d}"


def parse_ts(value: str) -> float | None:
    """'1:23' / '01:02:03' / '83' -> seconds; None when unparseable."""
    parts = value.strip().split(":")
    try:
        nums = [float(p) for p in parts]
    except ValueError:
        return None
    total = 0.0
    for n in nums:
        total = total * 60 + n
    return total
