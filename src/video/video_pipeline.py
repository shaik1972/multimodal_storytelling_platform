"""Video generation pipeline.

Order of preference:
1) local text-to-video command (free / no signup)
2) hosted text-to-video API (fallback)
"""

import os
import shlex
import subprocess
import tempfile

_SCENE_CROSSFADE_SECONDS = 0.35


class VideoGenerationError(RuntimeError):
    """Raised when a real narrated video cannot be generated."""


# ── Main generation ───────────────────────────────────────────────────────────

def generate_video(prompt: str) -> bytes:
    """Build a narrated MP4 from scene-level text-to-video clips."""
    local_command = os.getenv("TEXT_VIDEO_LOCAL_COMMAND", "").strip()
    api_key = os.getenv("TEXT_VIDEO_API_KEY", "").strip()
    api_url = os.getenv("TEXT_VIDEO_API_URL", "").strip().rstrip("/")
    if not local_command:
        if not api_key or api_key == "your_text_video_api_key_here":
            raise VideoGenerationError(
                "Set TEXT_VIDEO_LOCAL_COMMAND or TEXT_VIDEO_API_KEY to enable text-to-video generation."
            )
        if not api_url or "your-api-url" in api_url:
            raise VideoGenerationError("Set TEXT_VIDEO_API_URL to your provider endpoint.")

    try:
        return _build_video(prompt)
    except Exception as exc:
        if isinstance(exc, VideoGenerationError):
            raise
        raise VideoGenerationError(f"Video generation failed: {exc}") from exc


def _build_video(prompt: str) -> bytes:
    from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_videoclips, vfx

    from src.text.text_pipeline import generate_text
    from src.audio.audio_pipeline import generate_voice

    story = generate_text(prompt)
    audio_bytes = generate_voice(story)

    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as tmp:
        audio_path = os.path.join(tmp, "narration.mp3")
        with open(audio_path, "wb") as f:
            f.write(audio_bytes)

        audio_clip = AudioFileClip(audio_path)
        scene_texts = _scene_prompts(story)
        scene_duration = (
            audio_clip.duration + _SCENE_CROSSFADE_SECONDS * (len(scene_texts) - 1)
        ) / len(scene_texts)

        scene_clips = []
        source_clips = []

        for index, scene_text in enumerate(scene_texts):
            video_bytes = _generate_text_video(_video_prompt(scene_text))
            video_path = os.path.join(tmp, f"scene_{index}.mp4")
            with open(video_path, "wb") as f:
                f.write(video_bytes)

            source_clip = VideoFileClip(video_path)
            source_clips.append(source_clip)
            if source_clip.duration >= scene_duration:
                scene_clip = source_clip.subclip(0, scene_duration).without_audio()
            else:
                scene_clip = vfx.loop(source_clip.without_audio(), duration=scene_duration)
            if index:
                scene_clip = scene_clip.crossfadein(_SCENE_CROSSFADE_SECONDS)
            scene_clips.append(scene_clip)

        video_clip = concatenate_videoclips(
            scene_clips,
            method="compose",
            padding=-_SCENE_CROSSFADE_SECONDS,
        ).set_audio(audio_clip)

        out_path = os.path.join(tmp, "out.mp4")
        try:
            video_clip.write_videofile(
                out_path,
                fps=24,
                codec="libx264",
                audio_codec="aac",
                logger=None,
            )
        finally:
            if getattr(video_clip, "audio", None) is not None:
                video_clip.audio.close()
            video_clip.close()
            if getattr(audio_clip, "reader", None) is not None:
                audio_clip.reader.close()
            audio_clip.close()
            for scene_clip in scene_clips:
                scene_clip.close()
            for source_clip in source_clips:
                source_clip.close()

        with open(out_path, "rb") as f:
            return f.read()


def _generate_text_video(prompt: str) -> bytes:
    """Prefer a local generator, then fall back to a hosted provider."""
    local_command = os.getenv("TEXT_VIDEO_LOCAL_COMMAND", "").strip()
    if local_command:
        try:
            return _generate_local_text_video(prompt, local_command)
        except Exception as local_exc:
            if not os.getenv("TEXT_VIDEO_API_KEY", "").strip():
                raise VideoGenerationError(
                    f"Local text-to-video generation failed and no hosted fallback is configured: {local_exc}"
                ) from local_exc

    api_key = os.getenv("TEXT_VIDEO_API_KEY", "").strip()
    api_url = os.getenv("TEXT_VIDEO_API_URL", "").strip().rstrip("/")
    if not api_key or api_key == "your_text_video_api_key_here":
        raise VideoGenerationError(
            "Set TEXT_VIDEO_LOCAL_COMMAND or TEXT_VIDEO_API_KEY to enable text-to-video generation."
        )
    if not api_url or "your-api-url" in api_url:
        raise VideoGenerationError("Set TEXT_VIDEO_API_URL to your provider endpoint.")

    import requests

    model = os.getenv("TEXT_VIDEO_MODEL", "text-to-video").strip() or "text-to-video"
    response = requests.post(
        f"{api_url}/text-to-video",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "prompt": prompt,
        },
        timeout=60,
    )
    response.raise_for_status()

    payload = response.json() if hasattr(response, "json") else {}
    video_url = payload.get("video_url") or payload.get("output", {}).get("video_url")
    if video_url:
        video_response = requests.get(video_url, timeout=60)
        video_response.raise_for_status()
        if video_response.content:
            return video_response.content

    if getattr(response, "content", None):
        return response.content

    raise VideoGenerationError("Text-to-video provider did not return video bytes.")


def _generate_local_text_video(prompt: str, command_template: str) -> bytes:
    """Execute a local command that writes a .mp4 file for the given prompt."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_path = os.path.join(tmp_dir, "local_prompt_video.mp4")
        command = command_template.replace("{prompt}", str(prompt).replace('"', '\\"'))
        command = command.replace("{out}", output_path)
        if "{prompt}" not in command_template and "{out}" not in command_template:
            command = f'{command_template} --prompt "{prompt}" --out "{output_path}"'
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or "local text-to-video command failed")
        if not os.path.exists(output_path):
            raise RuntimeError(f"local command did not create {output_path}")
        with open(output_path, "rb") as handle:
            data = handle.read()
        if not data:
            raise RuntimeError("local command created an empty video file")
        return data


def _generate_motion_video(image_bytes: bytes, prompt: str) -> bytes:
    """Backward-compatible alias for the previous image-based implementation."""
    return _generate_text_video(prompt)


def _video_prompt(scene_text: str) -> str:
    """Add motion and expression direction to a story scene prompt."""
    return (
        "Create a cinematic short video from this scene. Preserve the characters, setting, and style, "
        "but animate the action with clear body movement, natural expression, and expressive motion. "
        f"Scene: {scene_text}"
    )


def _motion_prompt(scene_text: str) -> str:
    """Backward-compatible alias for prompt conversion."""
    return _video_prompt(scene_text)


def _scene_prompts(story: str) -> list[str]:
    """Break a story into scene-level prompts for text-to-video generation."""
    sentences = [part.strip() for part in story.replace("\n", " ").split(".") if part.strip()]
    if not sentences:
        sentences = [story]

    scene_count = min(6, max(3, len(sentences)))
    step = max(1, len(sentences) // scene_count)
    scenes = []
    for start in range(0, len(sentences), step):
        block = " ".join(sentences[start:start + step])
        scenes.append(
            f"Cinematic story scene. {block}. Show expressive character motion, clear actions, and emotional detail."
        )
        if len(scenes) == scene_count:
            break
    return scenes


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
        from moviepy.editor import CompositeVideoClip, TextClip, VideoFileClip

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


def _edit_video(video_bytes: bytes, transform) -> bytes:
    """Write a temp mp4, edit it, and return bytes."""
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
