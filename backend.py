from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from gtts import gTTS
import os
import uuid
from src.orchestration.orchestrator import run_text_pipeline, run_audio_pipeline, run_image_pipeline, run_video_pipeline


app = FastAPI()

PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "ui", "public")

@app.post("/text")
async def generate_text(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    story = f"Generated story from prompt: {prompt}"
    return JSONResponse({"story": story})

@app.post("/audio")
async def generate_audio(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")

    filename = f"audio_{uuid.uuid4().hex}.mp3"
    filepath = os.path.join(PUBLIC_DIR, filename)

    tts = gTTS(text=prompt, lang="en")
    tts.save(filepath)

    return JSONResponse({"audioUrl": f"/{filename}"})

@app.post("/image")
async def generate_image(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    image_file = run_image_pipeline(prompt)

    return JSONResponse({"imageUrl": f"/{image_file}"})


@app.post("/video")
async def generate_video(request: Request):
    data = await request.json()
    prompt = data.get("prompt", "")
    video_file = run_video_pipeline(prompt)

    return JSONResponse({"videoUrl": f"/{video_file}"})


