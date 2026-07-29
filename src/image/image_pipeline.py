"""
Image pipeline for generation and editing.
Uses Hugging Face Inference API (Stable Diffusion) when HF_API_KEY is set,
otherwise falls back to the local mock so the app still runs without credentials.
"""

import io
import os


# Placeholder sentinel — treat this as "no key"
_PLACEHOLDER = "your_huggingface_api_key_here"


def generate_image(prompt: str) -> bytes:
    """
    Generate image bytes from a text description.
    Falls back to a placeholder PNG when credentials are absent or invalid.
    """
    api_key = os.getenv("HF_API_KEY", "")

    if api_key and api_key != _PLACEHOLDER:
        try:
            return _generate_with_huggingface(prompt, api_key)
        except Exception as exc:
            print(f"[image_pipeline] HuggingFace error: {exc} — using placeholder")

    return _mock_png()


def _generate_with_huggingface(prompt: str, api_key: str) -> bytes:
    from huggingface_hub import InferenceClient

    client = InferenceClient(token=api_key)
    image = client.text_to_image(
        prompt,
        model="stabilityai/stable-diffusion-2-1",
    )
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    return buf.getvalue()


def _mock_png() -> bytes:
    """
    Return a 64×64 slate-blue PNG placeholder (no Pillow/HF required).
    Generated with: numpy array → PNG via zlib/struct — pure stdlib.
    """
    try:
        import numpy as np, struct, zlib

        w, h = 64, 64
        # Slate-blue pixels (RGB)
        img = np.full((h, w, 3), [100, 116, 139], dtype=np.uint8)

        def png_chunk(tag: bytes, data: bytes) -> bytes:
            c = zlib.crc32(tag + data) & 0xFFFFFFFF
            return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", c)

        raw = b"".join(b"\x00" + img[y].tobytes() for y in range(h))
        idat = zlib.compress(raw, 9)

        return (
            b"\x89PNG\r\n\x1a\n"
            + png_chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
            + png_chunk(b"IDAT", idat)
            + png_chunk(b"IEND", b"")
        )
    except Exception:
        import base64
        return base64.b64decode(
            "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        )


# ── Editing helpers (mocked — ready for real implementation) ──────────────────

def replace_background(image_bytes: bytes, new_background: str) -> bytes:
    return image_bytes + b" | BG_REPLACED_" + new_background.encode()


def add_object(image_bytes: bytes, object_description: str) -> bytes:
    return image_bytes + b" | OBJECT_ADDED_" + object_description.encode()


def apply_filter(image_bytes: bytes, filter_type: str) -> bytes:
    return image_bytes + b" | FILTER_" + filter_type.encode()
