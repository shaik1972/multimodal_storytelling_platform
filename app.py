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

    story_text = run_text_pipeline(story_input)
    log("Generated Story")
    text_path = save_text(story_text)
    log(f"Story saved to {text_path}")

    audio = run_audio_pipeline(story_text, voice=config.DEFAULT_VOICE, tone=config.DEFAULT_TONE)
    log("Generated Audio")
    audio_path = save_audio(audio)
    log(f"Audio saved to {audio_path}")

    video = generate_video(story_text)
    log("Generated Video")
    video_path = save_video(video)
    log(f"Video saved to {video_path}")
