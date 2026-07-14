"""
Video pipeline for generation and editing.
Currently mocked for local testing.
"""

def generate_video(prompt: str):
    """
    Generate video from description (mocked).
    """
    return b"FAKE_VIDEO_BYTES"

def trim_video(video_bytes: bytes, start_time: int, end_time: int):
    """
    Simulate trimming a video (mocked).
    """
    return video_bytes + f" | TRIM_{start_time}_{end_time}".encode()

def overlay_text(video_bytes: bytes, text: str, position="bottom"):
    """
    Simulate overlaying text on a video (mocked).
    """
    return video_bytes + b" | TEXT_" + text.encode() + b"_POS_" + position.encode()

def add_transition(video_bytes: bytes, transition_type: str):
    """
    Simulate adding a transition effect (mocked).
    """
    return video_bytes + b" | TRANSITION_" + transition_type.encode()
