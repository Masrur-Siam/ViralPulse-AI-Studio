"""Audio & Scene analyzer for OmniCut.
Detects silence and action chunks to assist in auto-splitting.
"""
import re
import subprocess
from typing import Dict, List, Tuple
from .ffmpeg_utils import probe_file


def detect_silence(video_path: str, noise_db: float = -30.0, min_duration: float = 0.5) -> List[Tuple[float, float]]:
    """Detect silent intervals [start, end] in a video."""
    cmd = [
        "ffmpeg", "-i", str(video_path),
        "-af", f"silencedetect=noise={noise_db}dB:d={min_duration}",
        "-f", "null", "-"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    output = proc.stderr

    silence_starts = [float(x) for x in re.findall(r"silence_start:\s*([0-9.]+)", output)]
    silence_ends = [float(x) for x in re.findall(r"silence_end:\s*([0-9.]+)", output)]

    pairs = []
    for s, e in zip(silence_starts, silence_ends):
        if e > s:
            pairs.append((s, e))
    return pairs


def detect_action_segments(
    video_path: str,
    noise_db: float = -30.0,
    min_silence: float = 0.5,
    min_clip_len: float = 2.0
) -> List[Dict]:
    """
    Invert silent intervals into active/talking intervals.
    Returns list of dicts with start, end, duration.
    """
    info = probe_file(video_path)
    total_dur = info.get("duration", 0.0)
    if total_dur <= 0:
        return []

    silences = detect_silence(video_path, noise_db, min_silence)
    if not silences:
        # Whole video is active
        return [{"start": 0.0, "end": total_dur, "duration": round(total_dur, 2)}]

    active_spans = []
    cur = 0.0

    for s_start, s_end in silences:
        if s_start > cur + min_clip_len:
            active_spans.append({"start": round(cur, 2), "end": round(s_start, 2), "duration": round(s_start - cur, 2)})
        cur = max(cur, s_end)

    if total_dur > cur + min_clip_len:
        active_spans.append({"start": round(cur, 2), "end": round(total_dur, 2), "duration": round(total_dur - cur, 2)})

    return active_spans
