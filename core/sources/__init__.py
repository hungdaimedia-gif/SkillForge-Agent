"""Source connectors: turn a URL or file into cached, anchored SourceDocs."""
from __future__ import annotations

from pathlib import Path

from ..models import SourceDoc
from .book import BOOK_SUFFIXES, load_book
from .youtube import fetch_video, is_youtube_url, list_videos


def acquire(target: str, cache_dir: Path | str = "sources_cache", lang: str = "en",
            max_frames: int = 24, frames: bool = True, limit: int | None = None) -> list[SourceDoc]:
    """URL (video / playlist / channel) or local file -> SourceDocs, in source order."""
    if is_youtube_url(target):
        videos = list_videos(target)[:limit] if limit else list_videos(target)
        docs = []
        for v in videos:
            doc = fetch_video(v["url"], cache_dir=cache_dir, lang=lang,
                              max_frames=max_frames, frames=frames)
            doc.extras.setdefault("playlist_index", v.get("index"))
            if v.get("playlist_title"):
                doc.extras["playlist_title"] = v["playlist_title"]
            docs.append(doc)
        return docs
    path = Path(target)
    if path.suffix.lower() in BOOK_SUFFIXES and path.exists():
        return [load_book(path)]
    raise ValueError(f"Don't know how to acquire: {target}")


__all__ = ["acquire", "fetch_video", "list_videos", "load_book"]
