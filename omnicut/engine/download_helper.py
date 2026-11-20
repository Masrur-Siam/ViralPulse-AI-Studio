"""URL Downloader and Cache Manager for OmniCut.
Allows direct processing from YouTube, Twitch, TikTok links without manual downloads.
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Optional

UPLOADS_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)


def get_url_info(url: str) -> Dict:
    """Fast metadata extraction using yt-dlp without downloading video."""
    cmd = [
        sys.executable, "-m", "yt_dlp",
        "--no-playlist",
        "--dump-json",
        url.strip()
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(proc.stdout)
        return {
            "ok": True,
            "title": data.get("title", "Online Video"),
            "duration": float(data.get("duration") or 0.0),
            "thumbnail": data.get("thumbnail") or "",
            "uploader": data.get("uploader") or "",
            "url": url.strip()
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "title": "Unknown Video", "duration": 0.0}


def resolve_video_source(source: str) -> Path:
    """
    Given a local filename or an online URL (YouTube, etc.):
    Returns the Path to the local file, automatically downloading and caching if it's a URL.
    """
    cleaned = source.strip()

    # Check if it's already a local file
    local_p = UPLOADS_DIR / cleaned
    if local_p.is_file():
        return local_p

    # Check outputs dir
    outputs_dir = Path(__file__).resolve().parent.parent / "outputs"
    local_out = outputs_dir / cleaned
    if local_out.is_file():
        return local_out

    # If it's a URL (http/https)
    if cleaned.startswith("http://") or cleaned.startswith("https://"):
        url_hash = hashlib.md5(cleaned.encode("utf-8")).hexdigest()[:12]
        cached_file = UPLOADS_DIR / f"yt_{url_hash}.mp4"

        # Check if already cached
        if cached_file.is_file() and cached_file.stat().st_size > 1024:
            return cached_file

        # Download using yt-dlp
        cmd = [
            sys.executable, "-m", "yt_dlp",
            "--no-playlist",
            "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "--merge-output-format", "mp4",
            "-o", str(cached_file),
            cleaned
        ]

        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"Failed to fetch YouTube/online video: {proc.stderr[-400:]}")

        if not cached_file.is_file() or cached_file.stat().st_size == 0:
            raise RuntimeError("Downloaded file is empty or missing.")

        return cached_file

    raise FileNotFoundError(f"Video source not found: {source}")
