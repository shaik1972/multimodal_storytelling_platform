"""
Audio pipeline for voice synthesis and editing.
Currently mocked for local testing.
"""

def generate_voice(text: str, voice="female_narrator", tone="neutral"):
    """
    Generate audio narration from text (mocked).
    """
    return b"FAKE_AUDIO_BYTES"

def delete_word(audio_bytes: bytes, word: str):
    """
    Simulate deleting a word from audio (mocked).
    """
    return b"FAKE_AUDIO_WITHOUT_" + word.encode()

def add_word(audio_bytes: bytes, word: str, tone="neutral"):
    """
    Simulate adding a word with tone matching (mocked).
    """
    return b"FAKE_AUDIO_WITH_ADDED_" + word.encode() + b"_TONE_" + tone.encode()
