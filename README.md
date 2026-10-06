# Multimodal Storytelling Platform

Turn a text prompt into a short story, narration, and (when configured) an illustration or video. The project has a FastAPI backend and a Next.js interface.

## Current capabilities

- **Prompt to story:** Gemini, Groq, or IBM watsonx.ai can generate stories when configured. With no working text provider, the pipeline returns a clearly marked mock story.
- **Text to voice:** Microsoft Edge TTS generates narration without a paid API key; gTTS is used as a fallback. Both require internet access.
- **Illustrations:** Hugging Face image generation is optional and requires a compatible access token/model.
- **Video:** The pipeline can call a configured local command or a provider implementing its expected HTTP interface. No video model or provider is bundled or configured by default, so real video generation is unavailable until one is supplied. Still-image motion is not presented as generated video.

## Requirements

- Python with support for the packages in `requirements.txt`
- Node.js and npm for the web interface
- Internet access for hosted text, voice, or image providers

## Setup

Create and activate a Python virtual environment, then install the backend dependencies:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Add credentials for the providers you intend to use to `.env`. Never commit `.env`; `.env.example` contains placeholders only. Without a text-provider key, story generation uses mock mode.

Install the frontend dependencies:

```powershell
npm ci --prefix ui
```

## Run

Start the backend and frontend in separate terminals:

```powershell
\.venv\Scripts\python.exe -m uvicorn backend:app --reload --port 8000
```

```powershell
npm --prefix ui run dev
```

Open `http://localhost:3000`. The backend API is available at `http://localhost:8000`.

The command-line demo can also be run with:

```powershell
\.venv\Scripts\python.exe app.py
```

## Tests

```powershell
\.venv\Scripts\python.exe -m pytest tests/test_video_pipeline.py -q
```

## Video provider contract

For a local engine, set `TEXT_VIDEO_LOCAL_COMMAND` to a command that accepts `{prompt}` and `{out}` placeholders and writes a real MP4 to the output path. A hosted provider uses `TEXT_VIDEO_API_KEY`, `TEXT_VIDEO_API_URL`, and optionally `TEXT_VIDEO_MODEL`; its API must accept `POST {TEXT_VIDEO_API_URL}/text-to-video` with a JSON body containing `model` and `prompt`, and return MP4 bytes or a JSON `video_url`. Provider APIs that differ need an adapter.

