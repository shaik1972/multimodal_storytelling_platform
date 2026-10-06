import base64
from types import SimpleNamespace

import pytest

from src.video.video_pipeline import (
    VideoGenerationError,
    _generate_text_video,
    _video_prompt,
    generate_video,
)


def test_generate_text_video_prefers_local_command(monkeypatch):
    calls = []

    def fake_run(command, shell, check, capture_output, text):
        calls.append(command)
        output_index = command.find("--out ")
        quoted = command[output_index + 6 :].strip()
        output_path = quoted.strip('"')
        with open(output_path, "wb") as handle:
            handle.write(b"local-video")
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setenv("TEXT_VIDEO_LOCAL_COMMAND", 'python local_model.py --prompt "{prompt}" --out "{out}"')
    monkeypatch.delenv("TEXT_VIDEO_API_KEY", raising=False)
    monkeypatch.delenv("TEXT_VIDEO_API_URL", raising=False)
    monkeypatch.setattr("subprocess.run", fake_run)

    result = _generate_text_video("A character smiles and waves")

    assert result == b"local-video"
    assert calls and "--prompt" in calls[0]


def test_generate_text_video_calls_provider_and_downloads_result(monkeypatch):
    calls = []

    class FakeResponse:
        def __init__(self, payload=None, content=b""):
            self.payload = payload or {}
            self.content = content

        def raise_for_status(self):
            pass

        def json(self):
            return self.payload

    def fake_post(url, **kwargs):
        calls.append(("post", url, kwargs))
        return FakeResponse({"video_url": "https://video.example/result.mp4"})

    def fake_get(url, **kwargs):
        calls.append(("get", url, kwargs))
        return FakeResponse(content=b"animated-mp4")

    monkeypatch.setenv("TEXT_VIDEO_API_KEY", "test-token")
    monkeypatch.setenv("TEXT_VIDEO_API_URL", "https://api.example/v1")
    monkeypatch.setenv("TEXT_VIDEO_MODEL", "test-video-model")
    monkeypatch.delenv("TEXT_VIDEO_LOCAL_COMMAND", raising=False)
    monkeypatch.setitem(
        __import__("sys").modules,
        "requests",
        SimpleNamespace(post=fake_post, get=fake_get),
    )

    result = _generate_text_video("A character smiles and waves")

    assert result == b"animated-mp4"
    assert calls[0][1] == "https://api.example/v1/text-to-video"
    request_body = calls[0][2]["json"]
    assert request_body["model"] == "test-video-model"
    assert request_body["prompt"] == "A character smiles and waves"


def test_generate_video_fails_clearly_without_text_video_key(monkeypatch):
    monkeypatch.delenv("TEXT_VIDEO_API_KEY", raising=False)
    monkeypatch.delenv("TEXT_VIDEO_LOCAL_COMMAND", raising=False)

    with pytest.raises(VideoGenerationError, match="Set TEXT_VIDEO_LOCAL_COMMAND|TEXT_VIDEO_API_KEY"):
        generate_video("A story about a moonlit forest")


def test_generate_video_accepts_local_command_without_hosted_key(monkeypatch):
    monkeypatch.setenv("TEXT_VIDEO_LOCAL_COMMAND", "python local_model.py")
    monkeypatch.delenv("TEXT_VIDEO_API_KEY", raising=False)
    monkeypatch.delenv("TEXT_VIDEO_API_URL", raising=False)
    monkeypatch.setattr("src.video.video_pipeline._build_video", lambda prompt: b"local-video")

    assert generate_video("A story about a moonlit forest") == b"local-video"


def test_video_prompt_requests_motion_and_expression():
    prompt = _video_prompt("The rabbit laughs and jumps over a log")

    assert "cinematic" in prompt.lower()
    assert "character" in prompt.lower()
    assert "expression" in prompt.lower()
    assert "rabbit laughs and jumps" in prompt.lower()