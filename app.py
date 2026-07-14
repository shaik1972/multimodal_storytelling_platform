from src.orchestration.orchestrator import (
    run_text_pipeline,
    run_audio_pipeline,
    delete_word,
    add_word,
    run_image_pipeline,
    run_video_pipeline
)
from src.image.image_pipeline import (
    generate_image,
    replace_background,
    add_object,
    apply_filter
)
from src.video.video_pipeline import (
    generate_video,
    trim_video,
    overlay_text,
    add_transition
)
from src.utils.file_utils import (
    save_text,
    save_audio,
    save_image,
    save_video
)
from src.utils.logger import log
from src import config

if __name__ == "__main__":
    story_input = "A young girl discovers a hidden world inside a library."

    # Text
    story_text = run_text_pipeline(story_input)
    log("Generated Story")
    text_path = save_text(story_text)
    log(f"Story saved to {text_path}")

    # Audio
    audio = run_audio_pipeline(story_text, voice=config.DEFAULT_VOICE, tone=config.DEFAULT_TONE)
    log("Generated Audio")
    audio_deleted = delete_word(audio, "library")
    log("Deleted word 'library' from audio")
    audio_added = add_word(audio, "magical", tone="warm")
    log("Added word 'magical' with tone 'warm'")
    audio_path = save_audio(audio)
    log(f"Audio saved to {audio_path}")

    # Image
    image = generate_image("Illustration of a magical library with glowing books")
    log("Generated Image")
    image_bg = replace_background(image, "starry night sky")
    log("Replaced background with 'starry night sky'")
    image_obj = add_object(image, "floating lanterns")
    log("Added object 'floating lanterns'")
    image_filtered = apply_filter(image, "sepia")
    log("Applied filter 'sepia'")
    image_path = save_image(image)
    log(f"Image saved to {image_path}")

    # Video
    video = generate_video("10s clip of glowing books opening in a magical library")
    log("Generated Video")
    video_trimmed = trim_video(video, 0, 5)
    log("Trimmed video from 0s to 5s")
    video_text = overlay_text(video, "Magical Library", position=config.DEFAULT_TEXT_POSITION)
    log("Overlayed text 'Magical Library' at top")
    video_transition = add_transition(video, config.DEFAULT_TRANSITION)
    log("Added transition 'fade-in'")
    video_path = save_video(video)
    log(f"Video saved to {video_path}")
