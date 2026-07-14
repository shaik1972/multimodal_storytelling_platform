import os
from src import config

def ensure_output_dir():
    if not os.path.exists(config.OUTPUT_DIR):
        os.makedirs(config.OUTPUT_DIR)

def save_text(content: str, filename=config.TEXT_FILE):
    ensure_output_dir()
    path = os.path.join(config.OUTPUT_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    return path

def save_audio(audio_bytes: bytes, filename=config.AUDIO_FILE):
    ensure_output_dir()
    path = os.path.join(config.OUTPUT_DIR, filename)
    with open(path, "wb") as f:
        f.write(audio_bytes)
    return path

def save_image(image_bytes: bytes, filename=config.IMAGE_FILE):
    ensure_output_dir()
    path = os.path.join(config.OUTPUT_DIR, filename)
    with open(path, "wb") as f:
        f.write(image_bytes)
    return path

def save_video(video_bytes: bytes, filename=config.VIDEO_FILE):
    ensure_output_dir()
    path = os.path.join(config.OUTPUT_DIR, filename)
    with open(path, "wb") as f:
        f.write(video_bytes)
    return path
