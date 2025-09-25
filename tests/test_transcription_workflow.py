"""Audio transcription workflow tests mirroring the Spring Boot example."""
from __future__ import annotations

import os
from pathlib import Path

import pytest
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY_SET = bool(os.getenv("OPENAI_API_KEY"))
pytestmark = pytest.mark.skipif(
    not API_KEY_SET, reason="requires OPENAI_API_KEY environment variable"
)

ASSETS_DIR = Path("tests/assets")
TRANSCRIPTION_MODEL = os.getenv("TRANSCRIPTION_MODEL", "gpt-4o-mini-transcribe")
TRANSLATION_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")


@pytest.fixture(scope="module")
def transcription_client() -> OpenAI:
    return OpenAI()


# 간단한 음성 텍스트 변환 테스트
def test_transcription_model(transcription_client: OpenAI) -> None:
    audio_path = ASSETS_DIR / "sample_audio.mp3"
    with audio_path.open("rb") as audio_file:
        transcription = transcription_client.audio.transcriptions.create(
            model=TRANSCRIPTION_MODEL,
            file=(audio_path.name, audio_file, "audio/mpeg"),
        )

    text = transcription.text or ""
    print(f"test_transcription_model result = {text}")
    assert text


# 음성 텍스트 변환 옵션 테스트
def test_transcription_model_options(transcription_client: OpenAI) -> None:
    audio_path = ASSETS_DIR / "sample_audio.mp3"
    with audio_path.open("rb") as audio_file:
        transcription = transcription_client.audio.transcriptions.create(
            model=TRANSCRIPTION_MODEL,
            file=(audio_path.name, audio_file, "audio/mpeg"),
        )

    source_text = transcription.text or ""
    assert source_text

    translation = transcription_client.chat.completions.create(
        model=TRANSLATION_MODEL,
        messages=[
            {
                "role": "system",
                "content": "당신은 전문 번역가입니다. 제공된 한국어 문장을 자연스러운 일본어로 번역하세요.",
            },
            {"role": "user", "content": source_text},
        ],
    )

    translated_text = translation.choices[0].message.content or ""
    print(f"test_transcription_model_options source = {source_text}")
    print(f"test_transcription_model_options translated = {translated_text}")
    assert translated_text
