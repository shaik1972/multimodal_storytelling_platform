"""
Image pipeline for generation and editing.
Currently mocked for local testing.
"""

def generate_image(prompt: str):
    """
    Generate image from description (mocked).
    """
    return b"FAKE_IMAGE_BYTES"

def replace_background(image_bytes: bytes, new_background: str):
    """
    Simulate replacing background in an image (mocked).
    """
    return image_bytes + b" | BG_REPLACED_" + new_background.encode()

def add_object(image_bytes: bytes, object_description: str):
    """
    Simulate adding an object to an image (mocked).
    """
    return image_bytes + b" | OBJECT_ADDED_" + object_description.encode()

def apply_filter(image_bytes: bytes, filter_type: str):
    """
    Simulate applying a filter to an image (mocked).
    """
    return image_bytes + b" | FILTER_" + filter_type.encode()
