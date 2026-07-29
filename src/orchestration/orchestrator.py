"""
Orchestration layer for multimodal storytelling platform.
Coordinates text, audio, image, and video pipelines.
"""

from src.text.text_pipeline import generate_text
from src.audio.audio_pipeline import generate_voice, delete_word, add_word
from src.image.image_pipeline import generate_image, replace_background, add_object, apply_filter
from src.video.video_pipeline import generate_video, trim_video, overlay_text, add_transition

# -------------------------------
# Orchestration Functions
# -------------------------------

def run_text_pipeline(prompt: str, max_tokens=300):
    return generate_text(prompt, max_tokens)

def run_audio_pipeline(text: str, voice: str = "female", speed: str = "+0%") -> bytes:
    return generate_voice(text, voice, speed)

def run_image_pipeline(prompt: str):
    return generate_image(prompt)

def run_video_pipeline(prompt: str):
    return generate_video(prompt)
