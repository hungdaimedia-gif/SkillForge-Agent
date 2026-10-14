"""Source connectors: turn a URL or file into cached, anchored SourceDocs."""
from __future__ import annotations

from pathlib import Path

from ..models import SourceDoc
from .book import BOOK_SUFFIXES, load_book
from .youtube import fetch_video, is_youtube_url, list_videos


def acquire(target: str, cache_dir: Path | str = "sources_cache", lang: str = "en",
            max_frames: int = 24, frames: bool = True, limit: int | None = None) -> list[SourceDoc]:
    """URL (video / playlist / channel) or local file -> SourceDocs, in source order.

    A `.urls` file is a curated list: one URL per line, `#` starts a comment
    (e.g. manifests/cascadeur_tutor.urls built from a course catalogue).
    """
    path = Path(target)
    if path.suffix.lower() == ".urls" and path.exists():
        urls = [line.split("#", 1)[0].strip()
                for line in path.read_text(encoding="utf-8").splitlines()]
        urls = [u for u in urls if u][:limit] if limit else [u for u in urls if u]
        docs = []
        for i, url in enumerate(urls, start=1):
            for doc in acquire(url, cache_dir=cache_dir, lang=lang, max_frames=max_frames,
                               frames=frames):
                doc.extras["playlist_index"] = i  # position in the manifest, not "1 of 1"
                docs.append(doc)
        return docs
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
    if path.suffix.lower() in BOOK_SUFFIXES and path.exists():
        return [load_book(path)]
    raise ValueError(f"Don't know how to acquire: {target}")


__all__ = ["acquire", "fetch_video", "list_videos", "load_book"]
