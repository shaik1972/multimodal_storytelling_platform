"""
Audio pipeline — uses Microsoft Edge TTS (edge-tts) for real male/female voices.

Supported voice values (passed from UI or parsed from prompt):
  "female"  → en-US-JennyNeural   (warm, natural female)
  "male"    → en-US-GuyNeural     (clear, natural male)
  "female2" → en-GB-SoniaNeural   (British female)
  "male2"   → en-GB-RyanNeural    (British male)

Speed is a percentage string like "+0%", "+20%", "-20%".
Falls back to gTTS if edge-tts is unavailable.
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
import io
import tempfile
import os

# ── Voice map ─────────────────────────────────────────────────────────────────

VOICE_MAP: dict[str, str] = {
    "female":  "en-US-JennyNeural",
    "male":    "en-US-GuyNeural",
    "female2": "en-GB-SoniaNeural",
    "male2":   "en-GB-RyanNeural",
}

DEFAULT_VOICE = "female"


def _resolve_voice(voice: str) -> str:
    """Return the edge-tts voice name for the given alias or full name."""
    return VOICE_MAP.get(voice.lower(), VOICE_MAP[DEFAULT_VOICE])


# ── Main entry point ──────────────────────────────────────────────────────────

def generate_voice(text: str, voice: str = DEFAULT_VOICE, speed: str = "+0%") -> bytes:
    """
    Generate MP3 audio bytes.
    voice : "female" | "male" | "female2" | "male2"  (default: "female")
    speed : edge-tts rate string, e.g. "+0%", "+20%", "-20%"
    """
    try:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(_edge_tts(text, voice, speed))

        with ThreadPoolExecutor(max_workers=1) as executor:
            return executor.submit(
                asyncio.run, _edge_tts(text, voice, speed)
            ).result()
    except Exception as exc:
        print(f"[audio_pipeline] edge-tts error: {exc} — falling back to gTTS")
        return _gtts_fallback(text)


async def _edge_tts(text: str, voice: str, speed: str) -> bytes:
    import edge_tts

    voice_name = _resolve_voice(voice)
    communicate = edge_tts.Communicate(text, voice_name, rate=speed)

    buf = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            buf.write(chunk["data"])

    buf.seek(0)
    return buf.read()


def _gtts_fallback(text: str) -> bytes:
    try:
        from gtts import gTTS
        buf = io.BytesIO()
        gTTS(text=text, lang="en").write_to_fp(buf)
        return buf.getvalue()
    except Exception:
        return b""


# ── Edit helpers ──────────────────────────────────────────────────────────────

def delete_word(audio_bytes: bytes, word: str) -> bytes:
    """Mocked — no-op until pydub editing is wired."""
    return audio_bytes


def add_word(audio_bytes: bytes, word: str, tone: str = "neutral") -> bytes:
    """Mocked — no-op until pydub editing is wired."""
    return audio_bytes
