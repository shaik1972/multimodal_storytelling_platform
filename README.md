# Multimodal Storytelling Platform (Mock Mode)

A modular Python project that orchestrates **text, audio, image, and video pipelines** to create interactive storytelling experiences.  
Currently runs in **mock mode** (no external SDKs required), making it easy to test orchestration, file saving, and logging locally.  
Later, the mock clients can be swapped with real AI SDKs (e.g., IBM Bob, Granite, Stable Diffusion, TTS, video editors).

---

## 🚀 Features
- **Text Pipeline** → Generates story text (mocked).
- **Audio Pipeline** → Narrates text, supports editing (delete/add words with tone).
- **Image Pipeline** → Creates illustrations, supports editing (replace background, add objects, apply filters).
- **Video Pipeline** → Generates clips, supports editing (trim, overlay text, add transitions).
- **Orchestration Layer** → Coordinates all pipelines.
- **Utilities** → File saving (`.txt`, `.mp3`, `.png`, `.mp4`) and logging with timestamps.
- **Config** → Centralized settings for filenames, voice, tone, transitions.

---

## 📂 Project Structure

multimodal-storytelling-platform/
│
├── src/
│   ├── text/
│   │   └── text_pipeline.py
│   ├── audio/
│   │   └── audio_pipeline.py
│   ├── image/
│   │   └── image_pipeline.py
│   ├── video/
│   │   └── video_pipeline.py
│   ├── orchestration/
│   │   └── orchestrator.py
│   ├── utils/
│   │   ├── file_utils.py
│   │   ├── logger.py
│   │   └── config.py
│
├── outputs/        # Generated files (story.txt, story.mp3, story.png, story.mp4, run.log)
├── app.py          # Entry point
├── requirements.txt
└── README.md


## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/multimodal-storytelling-platform.git
cd multimodal-storytelling-platform

### 2. Install dependencies
pip install -r requirements.txt
Note: Pillow is excluded because it doesn’t yet support Python 3.13.
For full image editing support, use Python 3.12 and re‑add Pillow.

## Usage
python app.py
Logs are written to: outputs/run.log

🛠️ Next Steps
Swap MockBobClient with real SDKs (IBM Bob, Granite, Stable Diffusion, etc.).

Enable Pillow once Python 3.13 wheels are available (or use Python 3.12).

Extend pipelines with real audio/image/video editing logic.

Add CLI or web interface for interactive storytelling.

📜 License

---

