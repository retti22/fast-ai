"""Audio synthesis smoke tests mirroring the Spring Boot example, using OpenAI."""
import os
from pathlib import Path
import shutil

import pytest
from openai import OpenAI

API_KEY_SET = bool(os.getenv("OPENAI_API_KEY"))
pytestmark = pytest.mark.skipif(
    not API_KEY_SET, reason="requires OPENAI_API_KEY environment variable"
)

SPEECH_MODEL = os.getenv("SPEECH_MODEL", "gpt-4o-mini-tts")
DEFAULT_VOICE = os.getenv("SPEECH_VOICE", "alloy")
DEFAULT_FORMAT = os.getenv("SPEECH_FORMAT", "mp3")

ARTIFACT_ROOT = Path(os.getenv("AUDIO_TEST_ARTIFACTS", "tests/artifacts"))

@pytest.fixture(scope="module")
def speech_client() -> OpenAI:
    return OpenAI()

def _save_artifact(src: Path, target_name: str) -> Path:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    dest = ARTIFACT_ROOT / target_name
    shutil.copy2(src, dest)
    return dest

def _synthesize(
    client: OpenAI,
    text: str,
    out_path: Path,
    *,
    voice: str | None = None,
    output_format: str | None = None,
    speed: float | None = None,
) -> dict:
    kwargs: dict[str, object] = {
        "model": SPEECH_MODEL,
        "voice": voice or DEFAULT_VOICE,
        "input": text,
        "response_format": output_format or DEFAULT_FORMAT,
    }
    if speed is not None:
        kwargs["speed"] = speed

    with client.audio.speech.with_streaming_response.create(**kwargs) as stream:
        stream.stream_to_file(out_path)
        return dict(stream.headers)

# 간단한 음성 합성 테스트
def test_simple_tts(tmp_path: Path, speech_client: OpenAI) -> None:
    announcement = "안녕하세요 반갑습니다. 스프링부트는 자바 프레임워크 중에 가장 인기가 많은 프레임워크입니다."
    output_file = tmp_path / "ai_tts_simple.mp3"
    headers = _synthesize(speech_client, announcement, output_file)

    assert output_file.exists()
    assert output_file.stat().st_size > 0
    assert "x-ratelimit-limit-requests" in headers
    _save_artifact(output_file, "ai_tts_simple.mp3")

# 음성 합성 옵션 테스트
def test_tts_with_options(tmp_path: Path, speech_client: OpenAI) -> None:
    sample_text = "안녕하세요 반갑습니다. 스프링부트는 자바 프레임워크 중에 가장 인기가 많은 프레임워크입니다."
    output_file = tmp_path / "ai_tts_options.mp3"
    headers = _synthesize(
        speech_client,
        sample_text,
        output_file,
        voice="nova",
        speed=1.0,
    )

    assert output_file.exists()
    assert output_file.stat().st_size > 0
    assert headers.get("x-ratelimit-remaining-requests") is not None
    _save_artifact(output_file, "ai_tts_options.mp3")
