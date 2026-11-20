"""Edge-TTS Voice Engine for OmniCut.
Generates ultra-natural neural speech for narrations and hooks without requiring any API keys.
"""
import asyncio
from pathlib import Path
from typing import Dict, List, Optional
import edge_tts

POPULAR_VOICES = [
    # English (US)
    {"id": "en-US-GuyNeural", "name": "Guy (Male, Energetic Narrator)", "lang": "English (US)", "gender": "Male"},
    {"id": "en-US-ChristopherNeural", "name": "Christopher (Male, Calm & Authoritative)", "lang": "English (US)", "gender": "Male"},
    {"id": "en-US-JennyNeural", "name": "Jenny (Female, Friendly)", "lang": "English (US)", "gender": "Female"},
    {"id": "en-US-AriaNeural", "name": "Aria (Female, Engaging)", "lang": "English (US)", "gender": "Female"},
    # English (UK)
    {"id": "en-GB-RyanNeural", "name": "Ryan (Male, British Documentary)", "lang": "English (UK)", "gender": "Male"},
    {"id": "en-GB-SoniaNeural", "name": "Sonia (Female, British)", "lang": "English (UK)", "gender": "Female"},
    # Bengali (Bangladesh)
    {"id": "bn-BD-PradeepNeural", "name": "Pradeep (Male, Bengali BD)", "lang": "Bengali (BD)", "gender": "Male"},
    {"id": "bn-BD-NabanitaNeural", "name": "Nabanita (Female, Bengali BD)", "lang": "Bengali (BD)", "gender": "Female"},
    # Bengali (India)
    {"id": "bn-IN-BashkarNeural", "name": "Bashkar (Male, Bengali IN)", "lang": "Bengali (IN)", "gender": "Male"},
    {"id": "bn-IN-TanishaaNeural", "name": "Tanishaa (Female, Bengali IN)", "lang": "Bengali (IN)", "gender": "Female"},
    # Hindi
    {"id": "hi-IN-MadhurNeural", "name": "Madhur (Male, Hindi)", "lang": "Hindi", "gender": "Male"},
    {"id": "hi-IN-SwaraNeural", "name": "Swara (Female, Hindi)", "lang": "Hindi", "gender": "Female"},
    # Urdu
    {"id": "ur-PK-AsadNeural", "name": "Asad (Male, Urdu)", "lang": "Urdu", "gender": "Male"},
    {"id": "ur-PK-UzmaNeural", "name": "Uzma (Female, Urdu)", "lang": "Urdu", "gender": "Female"},
]


async def generate_speech(
    text: str,
    output_path: str,
    voice: str = "en-US-GuyNeural",
    rate: str = "+0%",
    pitch: str = "+0Hz"
) -> str:
    """Generate speech audio file from text using edge_tts."""
    if not text or not text.strip():
        raise ValueError("Text cannot be empty.")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)

    communicate = edge_tts.Communicate(text=text.strip(), voice=voice, rate=rate, pitch=pitch)
    await communicate.save(str(output))

    if not output.is_file() or output.stat().st_size == 0:
        raise RuntimeError("Failed to generate speech audio file.")

    return str(output)


def get_voices() -> List[Dict]:
    """Get the list of popular curated natural voices."""
    return POPULAR_VOICES
