"""
Video pipeline — builds a real narrated MP4 using moviepy.

generate_video(prompt):
  1. Generates a story via the text pipeline (Groq / IBM / mock)
  2. Narrates it with gTTS into an in-memory MP3
  3. Generates an illustration via the image pipeline (HF / mock PNG)
  4. Assembles image + audio into an MP4 with moviepy
  5. Returns the MP4 bytes

Edit helpers (trim_video, overlay_text, add_transition) use moviepy too,
so every edit produces a real updated MP4.
"""

import io
import os
import tempfile


# ── Main generation ───────────────────────────────────────────────────────────

def generate_video(prompt: str) -> bytes:
    """
    Build a narrated MP4 from a generated story + illustration.
    Falls back to a minimal silent MP4 if moviepy is unavailable.
    """
    try:
        return _build_video(prompt)
    except Exception as exc:
        print(f"[video_pipeline] moviepy error: {exc}")
        return _silent_fallback_mp4()


def _build_video(prompt: str) -> bytes:
    from moviepy.editor import AudioFileClip, ImageClip

    from src.text.text_pipeline import generate_text
    from src.audio.audio_pipeline import generate_voice
    from src.image.image_pipeline import generate_image

    story = generate_text(prompt)
    audio_bytes = generate_voice(story)
    image_bytes = generate_image(prompt)

    with tempfile.TemporaryDirectory() as tmp:
        # Write image
        img_path = os.path.join(tmp, "frame.png")
        with open(img_path, "wb") as f:
            f.write(image_bytes)

        # Write audio
        audio_path = os.path.join(tmp, "narration.mp3")
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)

        # Assemble
        audio_clip = AudioFileClip(audio_path)
        video_clip = (
            ImageClip(img_path)
            .set_duration(audio_clip.duration)
            .set_audio(audio_clip)
        )

        out_path = os.path.join(tmp, "out.mp4")
        video_clip.write_videofile(
            out_path,
            fps=1,
            codec="libx264",
            audio_codec="aac",
            logger=None,       # suppress moviepy progress bars
        )

        with open(out_path, "rb") as f:
            return f.read()


def _silent_fallback_mp4() -> bytes:
    """Build a tiny black-frame MP4 using moviepy as last resort."""
    try:
        import tempfile
        import numpy as np
        from moviepy.editor import ImageClip

        black = np.zeros((240, 320, 3), dtype=np.uint8)
        with tempfile.TemporaryDirectory() as tmp:
            out = os.path.join(tmp, "blank.mp4")
            ImageClip(black, duration=2).write_videofile(
                out, fps=1, codec="libx264", audio=False, logger=None
            )
            with open(out, "rb") as f:
                return f.read()
    except Exception:
        return b""


# ── Edit helpers ──────────────────────────────────────────────────────────────

def trim_video(video_bytes: bytes, start_time: float, end_time: float) -> bytes:
    """Trim video to [start_time, end_time] seconds."""
    try:
        from moviepy.editor import VideoFileClip
        return _edit_video(video_bytes, lambda c: c.subclip(start_time, min(end_time, c.duration)))
    except Exception as exc:
        print(f"[video_pipeline] trim error: {exc}")
        return video_bytes


def overlay_text(video_bytes: bytes, text: str, position: str = "bottom") -> bytes:
    """Burn a text caption onto the video."""
    try:
        from moviepy.editor import TextClip, CompositeVideoClip, VideoFileClip

        pos_map = {"top": ("center", 0.05), "center": "center", "bottom": ("center", 0.90)}
        pos = pos_map.get(position, ("center", 0.90))

        def _apply(clip: VideoFileClip):
            txt = (
                TextClip(text, fontsize=36, color="white", stroke_color="black", stroke_width=1)
                .set_duration(clip.duration)
                .set_position(pos, relative=isinstance(pos, tuple))
            )
            return CompositeVideoClip([clip, txt])

        return _edit_video(video_bytes, _apply)
    except Exception as exc:
        print(f"[video_pipeline] overlay error: {exc}")
        return video_bytes


def add_transition(video_bytes: bytes, transition_type: str = "fade") -> bytes:
    """Apply a fade-in / fade-out transition."""
    try:
        def _apply(clip):
            if transition_type in ("fade", "fade-in"):
                return clip.fadein(0.5).fadeout(0.5)
            return clip

        return _edit_video(video_bytes, _apply)
    except Exception as exc:
        print(f"[video_pipeline] transition error: {exc}")
        return video_bytes


# ── Shared helper ─────────────────────────────────────────────────────────────

def _edit_video(video_bytes: bytes, transform) -> bytes:
    """
    Write video_bytes to a temp file, apply transform(VideoFileClip),
    encode to MP4, return bytes.
    """
    from moviepy.editor import VideoFileClip

    with tempfile.TemporaryDirectory() as tmp:
        in_path = os.path.join(tmp, "in.mp4")
        out_path = os.path.join(tmp, "out.mp4")

        with open(in_path, "wb") as f:
            f.write(video_bytes)

        clip = VideoFileClip(in_path)
        result = transform(clip)
        result.write_videofile(
            out_path,
            fps=clip.fps or 24,
            codec="libx264",
            audio_codec="aac",
            logger=None,
        )
        clip.close()

        with open(out_path, "rb") as f:
            return f.read()
