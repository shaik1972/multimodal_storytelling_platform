import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.orchestration.orchestrator import (
    run_text_pipeline,
    run_audio_pipeline,
    run_image_pipeline,
    run_video_pipeline,
)
from src.video.video_pipeline import trim_video, overlay_text, add_transition

load_dotenv()

app = FastAPI()

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["POST"],
    allow_headers=["Content-Type"],
)

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "ui", "public")
os.makedirs(PUBLIC_DIR, exist_ok=True)


def _save(data: bytes, name: str) -> str:
    """Save bytes to ui/public/ and return the public URL path."""
    filepath = os.path.join(PUBLIC_DIR, name)
    with open(filepath, "wb") as f:
        f.write(data)
    return f"/{name}"


def _load_public(url_path: str) -> bytes:
    """Read a file previously saved to ui/public/ by its URL path."""
    filepath = os.path.join(PUBLIC_DIR, url_path.lstrip("/"))
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail=f"File not found: {url_path}")
    with open(filepath, "rb") as f:
        return f.read()


# ── Text ──────────────────────────────────────────────────────────────────────
@app.post("/text")
async def generate_text_route(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    story = run_text_pipeline(prompt)
    return JSONResponse({"story": story})


# ── Audio ─────────────────────────────────────────────────────────────────────

# Keywords sorted longest-first so "female" (6) is checked before "male" (4),
# preventing "female" from matching the "male" substring inside it.
_VOICE_KEYWORDS: list[tuple[str, str]] = sorted(
    [
        ("male voice",    "male"),
        ("male",          "male"),
        ("man ",          "male"),   # trailing space avoids matching "many", "manner" etc.
        ("british male",  "male2"),
        ("british man",   "male2"),
        ("female voice",  "female"),
        ("female",        "female"),
        ("woman",         "female"),
        ("british female","female2"),
        ("british woman", "female2"),
    ],
    key=lambda t: len(t[0]),
    reverse=True,   # longest keyword checked first
)

def _detect_voice(prompt: str) -> str | None:
    """Return voice alias detected from prompt keywords, else None."""
    lower = prompt.lower()
    for keyword, alias in _VOICE_KEYWORDS:
        if keyword in lower:
            return alias
    return None


@app.post("/audio")
async def generate_audio_route(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")

    # UI can send explicit voice/speed; prompt keywords act as fallback detection
    explicit_voice = data.get("voice", "").strip()
    speed = data.get("speed", "+0%").strip() or "+0%"

    voice = explicit_voice or _detect_voice(prompt) or "female"

    # Generate story text first, then narrate it with the chosen voice
    story = run_text_pipeline(prompt)
    audio_bytes = run_audio_pipeline(story, voice=voice, speed=speed)

    filename = f"audio_{uuid.uuid4().hex}.mp3"
    url = _save(audio_bytes, filename)
    return JSONResponse({"audioUrl": url, "story": story, "voice": voice})


# ── Image ─────────────────────────────────────────────────────────────────────
@app.post("/image")
async def generate_image_route(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    image_bytes = run_image_pipeline(prompt)

    filename = f"image_{uuid.uuid4().hex}.png"
    url = _save(image_bytes, filename)
    return JSONResponse({"imageUrl": url})


# ── Video ─────────────────────────────────────────────────────────────────────
@app.post("/video")
async def generate_video_route(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    video_bytes = run_video_pipeline(prompt)

    filename = f"video_{uuid.uuid4().hex}.mp4"
    url = _save(video_bytes, filename)
    return JSONResponse({"videoUrl": url})


# ── Video edits ───────────────────────────────────────────────────────────────
@app.post("/video/trim")
async def video_trim_route(request: Request):
    data = await request.json()
    video_bytes = _load_public(data["videoUrl"])
    result = trim_video(video_bytes, float(data.get("start", 0)), float(data.get("end", 5)))
    url = _save(result, f"video_{uuid.uuid4().hex}.mp4")
    return JSONResponse({"videoUrl": url})


@app.post("/video/overlay")
async def video_overlay_route(request: Request):
    data = await request.json()
    video_bytes = _load_public(data["videoUrl"])
    result = overlay_text(video_bytes, data.get("text", ""), data.get("position", "bottom"))
    url = _save(result, f"video_{uuid.uuid4().hex}.mp4")
    return JSONResponse({"videoUrl": url})


@app.post("/video/transition")
async def video_transition_route(request: Request):
    data = await request.json()
    video_bytes = _load_public(data["videoUrl"])
    result = add_transition(video_bytes, data.get("transition", "fade"))
    url = _save(result, f"video_{uuid.uuid4().hex}.mp4")
    return JSONResponse({"videoUrl": url})
