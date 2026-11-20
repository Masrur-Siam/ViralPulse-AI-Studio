"""FFmpeg utilities for OmniCut:
- Video probing (duration, resolution, fps, audio presence)
- Smart Split, Cut & Stitch (joining multiple segments seamlessly)
- Dual Video Comparison (Top/Bottom 9:16 and Side-by-Side 16:9 with customizable labels)
- Voiceover Overlay (with background audio ducking)
- Vertical 9:16 Shorts Generation (blurred-background or direct center-crop)
"""
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple

FONTS_DIR = Path(__file__).resolve().parent.parent / "fonts"
DEFAULT_FONT = FONTS_DIR / "Poppins-Bold.ttf"


def _clean_path(p: Path) -> str:
    """Format path for FFmpeg filter arguments (forward slashes, escaped colons)."""
    return str(p.resolve()).replace("\\", "/").replace(":", "\\:")


def probe_file(file_path: str) -> Dict:
    """Extract metadata using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration,size,bit_rate:stream=width,height,r_frame_rate,codec_name,codec_type",
        "-of", "json",
        str(file_path)
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(proc.stdout)
    except Exception as e:
        return {"error": str(e), "duration": 0, "width": 0, "height": 0, "has_audio": False}

    duration = float(data.get("format", {}).get("duration") or 0.0)
    size = int(data.get("format", {}).get("size") or 0)
    width, height, fps = 0, 0, 30.0
    has_audio, has_video = False, False

    for stream in data.get("streams", []):
        ctype = stream.get("codec_type")
        if ctype == "video" and not has_video:
            has_video = True
            width = int(stream.get("width") or 0)
            height = int(stream.get("height") or 0)
            fps_str = stream.get("r_frame_rate", "30/1")
            if "/" in fps_str:
                num, den = fps_str.split("/")
                fps = float(num) / float(den) if float(den) != 0 else 30.0
            else:
                fps = float(fps_str or 30.0)
        elif ctype == "audio":
            has_audio = True

    return {
        "duration": round(duration, 2),
        "size_mb": round(size / (1024 * 1024), 2),
        "width": width,
        "height": height,
        "fps": round(fps, 2),
        "has_audio": has_audio,
        "has_video": has_video
    }


def cut_and_stitch(
    input_path: str,
    segments: List[Tuple[float, float]],
    output_path: str,
    voiceover_path: Optional[str] = None,
    bg_music_volume: float = 0.3
) -> bool:
    """
    Cut multiple [start, end] segments from a video and stitch them together seamlessly.
    Optionally overlays a voiceover track.
    """
    if not segments:
        raise ValueError("At least one segment [start, end] is required.")

    info = probe_file(input_path)
    has_audio = info.get("has_audio", False)
    total_dur = info.get("duration", 0)

    # Validate and clamp segments
    valid_segments = []
    for s, e in segments:
        start = max(0.0, float(s))
        end = min(total_dur, float(e)) if total_dur > 0 else float(e)
        if end > start + 0.1:
            valid_segments.append((start, end))

    if not valid_segments:
        raise ValueError("No valid segment durations provided.")

    v_filters = []
    a_filters = []
    inputs_concat_v = []
    inputs_concat_a = []

    for i, (start, end) in enumerate(valid_segments):
        v_filters.append(f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[v{i}]")
        inputs_concat_v.append(f"[v{i}]")

        if has_audio:
            a_filters.append(f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a{i}]")
            inputs_concat_a.append(f"[a{i}]")
        else:
            dur = end - start
            a_filters.append(f"anullsrc=channel_layout=stereo:sample_rate=44100,atrim=duration={dur}[a{i}]")
            inputs_concat_a.append(f"[a{i}]")

    num = len(valid_segments)
    concat_filter = (
        "".join(inputs_concat_v) + "".join(inputs_concat_a) +
        f"concat=n={num}:v=1:a=1[vcat][acat]"
    )

    filter_complex = ";".join(v_filters + a_filters + [concat_filter])

    cmd = ["ffmpeg", "-y", "-i", str(input_path)]

    if voiceover_path and Path(voiceover_path).is_file():
        cmd.extend(["-i", str(voiceover_path)])
        # Mix concatenated audio with voiceover
        filter_complex += f";[acat]volume={bg_music_volume}[bg];[1:a]volume=1.0[voice];[bg][voice]amix=inputs=2:duration=first[aout]"
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[vcat]",
            "-map", "[aout]"
        ])
    else:
        cmd.extend([
            "-filter_complex", filter_complex,
            "-map", "[vcat]",
            "-map", "[acat]"
        ])

    cmd.extend([
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path)
    ])

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg stitching failed: {proc.stderr[-500:]}")

    return True


def make_comparison(
    video_a: str,
    video_b: str,
    output_path: str,
    layout: str = "top-bottom",  # "top-bottom" (9:16) or "side-by-side" (16:9)
    label_a: str = "Game A",
    label_b: str = "Game B",
    start_a: float = 0.0,
    start_b: float = 0.0,
    duration: float = 15.0,
    audio_mode: str = "both"  # "both", "a", "b", "mute"
) -> bool:
    """
    Creates a dual-video comparison video.
    - layout 'top-bottom': 1080x1920 (9:16 Vertical for Shorts/Reels/TikTok)
    - layout 'side-by-side': 1920x1080 (16:9 Horizontal for YouTube)
    """
    info_a = probe_file(video_a)
    info_b = probe_file(video_b)

    font_path_arg = _clean_path(DEFAULT_FONT) if DEFAULT_FONT.is_file() else ""
    font_arg = f":fontfile='{font_path_arg}'" if font_path_arg else ""

    # Clean labels for ffmpeg drawtext
    clean_la = re.sub(r"[':\\]", "", label_a).strip() or "Option A"
    clean_lb = re.sub(r"[':\\]", "", label_b).strip() or "Option B"

    filters = []

    if layout == "top-bottom":
        # Target: 1080x1920 (Vertical 9:16). Each video gets 1080x960
        filters.append(
            f"[0:v]trim=start={start_a}:duration={duration},setpts=PTS-STARTPTS,"
            f"scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960,"
            f"drawtext=text='{clean_la}'{font_arg}:x=(w-text_w)/2:y=40:fontsize=46:fontcolor=yellow:"
            f"box=1:boxcolor=black@0.65:boxborderw=12[va]"
        )
        filters.append(
            f"[1:v]trim=start={start_b}:duration={duration},setpts=PTS-STARTPTS,"
            f"scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960,"
            f"drawtext=text='{clean_lb}'{font_arg}:x=(w-text_w)/2:y=40:fontsize=46:fontcolor=cyan:"
            f"box=1:boxcolor=black@0.65:boxborderw=12[vb]"
        )
        # Stack vertically and add a thin dividing line in the middle (y=958-962)
        filters.append(
            f"[va][vb]vstack=inputs=2,"
            f"drawbox=y=957:color=white:width=iw:height=6:t=fill[vcomp]"
        )
    else:
        # Target: 1920x1080 (Horizontal 16:9). Each video gets 960x1080
        filters.append(
            f"[0:v]trim=start={start_a}:duration={duration},setpts=PTS-STARTPTS,"
            f"scale=960:1080:force_original_aspect_ratio=increase,crop=960:1080,"
            f"drawtext=text='{clean_la}'{font_arg}:x=(w-text_w)/2:y=50:fontsize=46:fontcolor=yellow:"
            f"box=1:boxcolor=black@0.65:boxborderw=12[va]"
        )
        filters.append(
            f"[1:v]trim=start={start_b}:duration={duration},setpts=PTS-STARTPTS,"
            f"scale=960:1080:force_original_aspect_ratio=increase,crop=960:1080,"
            f"drawtext=text='{clean_lb}'{font_arg}:x=(w-text_w)/2:y=50:fontsize=46:fontcolor=cyan:"
            f"box=1:boxcolor=black@0.65:boxborderw=12[vb]"
        )
        # Stack horizontally and add a thin vertical dividing line in the middle (x=957-963)
        filters.append(
            f"[va][vb]hstack=inputs=2,"
            f"drawbox=x=957:color=white:width=6:height=ih:t=fill[vcomp]"
        )

    # Audio Handling
    has_audio_a = info_a.get("has_audio", False)
    has_audio_b = info_b.get("has_audio", False)

    if audio_mode == "a" and has_audio_a:
        filters.append(f"[0:a]atrim=start={start_a}:duration={duration},asetpts=PTS-STARTPTS[acomp]")
    elif audio_mode == "b" and has_audio_b:
        filters.append(f"[1:a]atrim=start={start_b}:duration={duration},asetpts=PTS-STARTPTS[acomp]")
    elif audio_mode == "both" and (has_audio_a or has_audio_b):
        a_inputs = []
        if has_audio_a:
            filters.append(f"[0:a]atrim=start={start_a}:duration={duration},asetpts=PTS-STARTPTS[a1]")
            a_inputs.append("[a1]")
        if has_audio_b:
            filters.append(f"[1:a]atrim=start={start_b}:duration={duration},asetpts=PTS-STARTPTS[a2]")
            a_inputs.append("[a2]")
        if len(a_inputs) == 2:
            filters.append(f"{''.join(a_inputs)}amix=inputs=2:duration=longest[acomp]")
        else:
            filters.append(f"{a_inputs[0]}acopy[acomp]")
    else:
        filters.append(f"anullsrc=channel_layout=stereo:sample_rate=44100,atrim=duration={duration}[acomp]")

    filter_complex = ";".join(filters)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_a),
        "-i", str(video_b),
        "-filter_complex", filter_complex,
        "-map", "[vcomp]",
        "-map", "[acomp]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "21",
        "-c:a", "aac",
        "-b:a", "192k",
        "-t", str(duration),
        str(output_path)
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg comparison failed: {proc.stderr[-600:]}")

    return True


def make_vertical_short(
    video_path: str,
    output_path: str,
    start: float = 0.0,
    duration: Optional[float] = None,
    mode: str = "blur-background"  # "blur-background" or "center-crop"
) -> bool:
    """
    Transform horizontal/landscape video into high-retention 9:16 vertical video.
    - 'blur-background': Background is scaled & blurred 9:16, foreground is sharp centered video.
    - 'center-crop': Center of the video cropped to 1080x1920.
    """
    info = probe_file(video_path)
    dur_arg = f":duration={duration}" if duration and duration > 0 else ""

    if mode == "center-crop":
        v_filter = (
            f"[0:v]trim=start={start}{dur_arg},setpts=PTS-STARTPTS,"
            f"scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[vout]"
        )
    else:
        # Blur background
        v_filter = (
            f"[0:v]trim=start={start}{dur_arg},setpts=PTS-STARTPTS,split=2[bg_in][fg_in];"
            f"[bg_in]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=25:12[bg];"
            f"[fg_in]scale=1080:1920:force_original_aspect_ratio=decrease[fg];"
            f"[bg][fg]overlay=(W-w)/2:(H-h)/2[vout]"
        )

    filters = [v_filter]
    if info.get("has_audio"):
        filters.append(f"[0:a]atrim=start={start}{dur_arg},asetpts=PTS-STARTPTS[aout]")
    else:
        filters.append(f"anullsrc=channel_layout=stereo:sample_rate=44100[aout]")

    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-filter_complex", ";".join(filters),
        "-map", "[vout]",
        "-map", "[aout]",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "22",
        "-c:a", "aac",
        "-b:a", "192k"
    ]
    if duration and duration > 0:
        cmd.extend(["-t", str(duration)])

    cmd.append(str(output_path))

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg vertical short creation failed: {proc.stderr[-600:]}")

    return True


def overlay_voiceover(
    video_path: str,
    voice_path: str,
    output_path: str,
    bg_volume: float = 0.25,
    voice_volume: float = 1.0,
    replace_audio: bool = False
) -> bool:
    """Overlays an audio/voiceover track onto a video with background audio ducking."""
    info = probe_file(video_path)
    has_audio = info.get("has_audio", False)

    if replace_audio or not has_audio:
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(voice_path),
            "-map", "0:v",
            "-map", "1:a",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(output_path)
        ]
    else:
        filter_complex = (
            f"[0:a]volume={bg_volume}[bg];"
            f"[1:a]volume={voice_volume}[voice];"
            f"[bg][voice]amix=inputs=2:duration=first[aout]"
        )
        cmd = [
            "ffmpeg", "-y",
            "-i", str(video_path),
            "-i", str(voice_path),
            "-filter_complex", filter_complex,
            "-map", "0:v",
            "-map", "[aout]",
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "192k",
            str(output_path)
        ]

    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg voice overlay failed: {proc.stderr[-600:]}")

    return True
