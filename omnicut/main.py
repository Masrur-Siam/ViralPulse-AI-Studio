"""OmniCut Studio - AI Video Clipping, Multi-Segment Stitching, Dual Comparison & Voiceover Suite.
Seamless YouTube & URL support: Just paste any YouTube link and it works directly!
"""
import asyncio
import os
import shutil
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

import uvicorn
from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .engine import analyzer, download_helper, ffmpeg_utils, tts_engine

ROOT = Path(__file__).resolve().parent
UPLOADS_DIR = ROOT / "uploads"
OUTPUTS_DIR = ROOT / "outputs"
STATIC_DIR = ROOT / "static"

UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="OmniCut Studio")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
app.mount("/media/uploads", StaticFiles(directory=str(UPLOADS_DIR)), name="uploads")
app.mount("/media/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")


# -------------------------------------------------------------
# File Uploads & Fast URL Metadata
# -------------------------------------------------------------
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a local video or audio file."""
    ext = Path(file.filename).suffix.lower() or ".mp4"
    safe_name = f"{int(time.time())}_{uuid.uuid4().hex[:6]}{ext}"
    dest = UPLOADS_DIR / safe_name

    with dest.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    info = ffmpeg_utils.probe_file(str(dest))
    return {
        "ok": True,
        "filename": safe_name,
        "original_name": file.filename,
        "url": f"/media/uploads/{safe_name}",
        "path": str(dest),
        "info": info
    }


class UrlInfoRequest(BaseModel):
    url: str


@app.post("/api/url-info")
def fetch_url_info(req: UrlInfoRequest):
    """Fast video info without downloading (returns title, thumbnail, duration)."""
    data = download_helper.get_url_info(req.url)
    if not data.get("ok"):
        raise HTTPException(400, data.get("error", "Could not fetch video info from URL."))
    return data


# -------------------------------------------------------------
# Auto-Split (Active Scene & Silence Detection)
# -------------------------------------------------------------
class AutoSplitRequest(BaseModel):
    source: str  # Can be filename OR YouTube URL
    noise_db: float = -30.0
    min_silence: float = 0.5
    min_clip_len: float = 2.0


@app.post("/api/auto-split")
async def auto_split_video(req: AutoSplitRequest):
    try:
        video_path = await asyncio.to_thread(download_helper.resolve_video_source, req.source)
    except Exception as e:
        raise HTTPException(400, f"Source resolution error: {str(e)}")

    segments = await asyncio.to_thread(
        analyzer.detect_action_segments,
        str(video_path),
        noise_db=req.noise_db,
        min_silence=req.min_silence,
        min_clip_len=req.min_clip_len
    )
    return {
        "ok": True,
        "filename": video_path.name,
        "url": f"/media/uploads/{video_path.name}",
        "segments": segments
    }


# -------------------------------------------------------------
# Split, Cut & Stitch Multiple Segments
# -------------------------------------------------------------
class Segment(BaseModel):
    start: float
    end: float


class SplitStitchRequest(BaseModel):
    source: str  # Can be local filename OR YouTube URL
    segments: List[Segment]
    voiceover_filename: Optional[str] = None
    bg_music_volume: float = 0.25


@app.post("/api/split-and-stitch")
async def split_and_stitch_video(req: SplitStitchRequest):
    try:
        inp = await asyncio.to_thread(download_helper.resolve_video_source, req.source)
    except Exception as e:
        raise HTTPException(400, f"Failed to get video source: {str(e)}")

    out_name = f"stitched_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp4"
    out_path = OUTPUTS_DIR / out_name

    voice_path = None
    if req.voiceover_filename:
        vp = OUTPUTS_DIR / req.voiceover_filename
        if not vp.is_file():
            vp = UPLOADS_DIR / req.voiceover_filename
        if vp.is_file():
            voice_path = str(vp)

    seg_tuples = [(s.start, s.end) for s in req.segments]

    try:
        await asyncio.to_thread(
            ffmpeg_utils.cut_and_stitch,
            str(inp),
            seg_tuples,
            str(out_path),
            voice_path,
            req.bg_music_volume
        )
    except Exception as e:
        raise HTTPException(500, f"Stitching error: {str(e)}")

    info = ffmpeg_utils.probe_file(str(out_path))
    return {
        "ok": True,
        "filename": out_name,
        "url": f"/media/outputs/{out_name}",
        "info": info
    }


# -------------------------------------------------------------
# Dual Video Comparison (Game comparison, Side-by-side, Top-bottom)
# -------------------------------------------------------------
class CompareRequest(BaseModel):
    video_a: str  # Can be local filename OR YouTube URL
    video_b: str  # Can be local filename OR YouTube URL
    layout: str = "top-bottom"  # "top-bottom" (9:16) or "side-by-side" (16:9)
    label_a: str = "Game A"
    label_b: str = "Game B"
    start_a: float = 0.0
    start_b: float = 0.0
    duration: float = 15.0
    audio_mode: str = "both"  # "both", "a", "b", "mute"


@app.post("/api/compare-videos")
async def compare_videos(req: CompareRequest):
    try:
        path_a = await asyncio.to_thread(download_helper.resolve_video_source, req.video_a)
        path_b = await asyncio.to_thread(download_helper.resolve_video_source, req.video_b)
    except Exception as e:
        raise HTTPException(400, f"Failed to resolve comparison videos: {str(e)}")

    out_name = f"compare_{req.layout}_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp4"
    out_path = OUTPUTS_DIR / out_name

    try:
        await asyncio.to_thread(
            ffmpeg_utils.make_comparison,
            str(path_a),
            str(path_b),
            str(out_path),
            layout=req.layout,
            label_a=req.label_a,
            label_b=req.label_b,
            start_a=req.start_a,
            start_b=req.start_b,
            duration=req.duration,
            audio_mode=req.audio_mode
        )
    except Exception as e:
        raise HTTPException(500, f"Comparison render error: {str(e)}")

    info = ffmpeg_utils.probe_file(str(out_path))
    return {
        "ok": True,
        "filename": out_name,
        "url": f"/media/outputs/{out_name}",
        "info": info
    }


# -------------------------------------------------------------
# Vertical 9:16 Short Creator (Directly from YouTube or File)
# -------------------------------------------------------------
class ShortRequest(BaseModel):
    source: str  # Can be local filename OR YouTube URL
    start: float = 0.0
    duration: Optional[float] = None
    mode: str = "blur-background"  # "blur-background" or "center-crop"


@app.post("/api/make-short")
async def make_short(req: ShortRequest):
    try:
        inp = await asyncio.to_thread(download_helper.resolve_video_source, req.source)
    except Exception as e:
        raise HTTPException(400, f"Failed to get video source: {str(e)}")

    out_name = f"short_916_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp4"
    out_path = OUTPUTS_DIR / out_name

    try:
        await asyncio.to_thread(
            ffmpeg_utils.make_vertical_short,
            str(inp),
            str(out_path),
            start=req.start,
            duration=req.duration,
            mode=req.mode
        )
    except Exception as e:
        raise HTTPException(500, f"Short creation error: {str(e)}")

    info = ffmpeg_utils.probe_file(str(out_path))
    return {
        "ok": True,
        "filename": out_name,
        "url": f"/media/outputs/{out_name}",
        "info": info
    }


# -------------------------------------------------------------
# TTS Voiceover Generation & Overlay
# -------------------------------------------------------------
@app.get("/api/tts/voices")
def list_voices():
    return tts_engine.get_voices()


class TTSGenerateRequest(BaseModel):
    text: str
    voice: str = "en-US-GuyNeural"
    rate: str = "+0%"
    pitch: str = "+0Hz"


@app.post("/api/tts/generate")
async def generate_tts(req: TTSGenerateRequest):
    out_name = f"voice_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp3"
    out_path = OUTPUTS_DIR / out_name

    try:
        await tts_engine.generate_speech(
            text=req.text,
            output_path=str(out_path),
            voice=req.voice,
            rate=req.rate,
            pitch=req.pitch
        )
    except Exception as e:
        raise HTTPException(500, f"TTS generation error: {str(e)}")

    return {
        "ok": True,
        "filename": out_name,
        "url": f"/media/outputs/{out_name}"
    }


class TTSOverlayRequest(BaseModel):
    video_source: str  # Can be filename OR YouTube URL
    voice_filename: str
    bg_volume: float = 0.25
    voice_volume: float = 1.0
    replace_audio: bool = False


@app.post("/api/tts/overlay")
async def overlay_tts(req: TTSOverlayRequest):
    try:
        vp = await asyncio.to_thread(download_helper.resolve_video_source, req.video_source)
    except Exception as e:
        raise HTTPException(400, f"Video source error: {str(e)}")

    ap = OUTPUTS_DIR / req.voice_filename
    if not ap.is_file():
        ap = UPLOADS_DIR / req.voice_filename

    if not ap.is_file():
        raise HTTPException(404, "Voice file not found.")

    out_name = f"voiced_{int(time.time())}_{uuid.uuid4().hex[:6]}.mp4"
    out_path = OUTPUTS_DIR / out_name

    try:
        await asyncio.to_thread(
            ffmpeg_utils.overlay_voiceover,
            str(vp),
            str(ap),
            str(out_path),
            bg_volume=req.bg_volume,
            voice_volume=req.voice_volume,
            replace_audio=req.replace_audio
        )
    except Exception as e:
        raise HTTPException(500, f"Overlay error: {str(e)}")

    info = ffmpeg_utils.probe_file(str(out_path))
    return {
        "ok": True,
        "filename": out_name,
        "url": f"/media/outputs/{out_name}",
        "info": info
    }


# -------------------------------------------------------------
# Library & Management
# -------------------------------------------------------------
@app.get("/api/library")
def get_library():
    def scan_dir(d: Path, folder_type: str):
        items = []
        for f in sorted(d.glob("*"), key=os.path.getmtime, reverse=True):
            if f.is_file() and f.suffix.lower() in [".mp4", ".mov", ".mkv", ".mp3", ".wav", ".webm"]:
                stat = f.stat()
                items.append({
                    "name": f.name,
                    "folder": folder_type,
                    "url": f"/media/{folder_type}/{f.name}",
                    "size_mb": round(stat.st_size / (1024 * 1024), 2),
                    "created_at": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
                    "is_video": f.suffix.lower() in [".mp4", ".mov", ".mkv", ".webm"]
                })
        return items

    return {
        "outputs": scan_dir(OUTPUTS_DIR, "outputs"),
        "uploads": scan_dir(UPLOADS_DIR, "uploads")
    }


@app.delete("/api/library/{folder}/{filename}")
def delete_item(folder: str, filename: str):
    d = OUTPUTS_DIR if folder == "outputs" else UPLOADS_DIR
    target = d / filename
    if target.is_file():
        target.unlink()
        return {"ok": True, "message": "File deleted."}
    raise HTTPException(404, "File not found.")


def main():
    print("\n" + "=" * 60)
    print("  🚀 OmniCut Studio is running at: http://127.0.0.1:8899")
    print("=" * 60 + "\n")
    uvicorn.run("omnicut.main:app", host="127.0.0.1", port=8899, log_level="info")


if __name__ == "__main__":
    main()
