"""Audio synthesis smoke tests mirroring the Spring Boot example, using OpenAI."""
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

@pytest.fixture(scope="module")
def speech_client() -> OpenAI:
    return OpenAI()  # 테스트 전역에서 재사용할 OpenAI 클라이언트를 생성한다


def _write_artifact(data: bytes, filename: str) -> Path:
    artifact_root = Path("tests/artifacts")  # 음성 아티팩트를 보관할 기본 폴더
    artifact_root.mkdir(parents=True, exist_ok=True)  # 아티팩트 저장 폴더가 없다면 생성한다
    target_path = artifact_root / filename  # 최종 저장 경로를 계산한다
    target_path.write_bytes(data)  # 음성 데이터를 파일에 기록한다
    return target_path  # 저장된 파일 경로를 반환한다

# 간단한 음성 합성 테스트 (TTS)
def test_speech_model_simple(tmp_path: Path, speech_client: OpenAI) -> None:
    output_file = tmp_path / "ai_tts_simple.mp3"  # 임시 디렉터리에 결과 파일 경로를 준비한다

    # https://platform.openai.com/docs/guides/text-to-speech#page-top
    # https://platform.openai.com/docs/api-reference/audio/createSpeech
    audio = speech_client.audio.speech.create(
        model="tts-1-hd",
        voice="nova",
        input="안녕하세요 반갑습니다. 스프링부트는 자바 프레임워크 중에 가장 인기가 많은 프레임워크입니다."
    )

    output_file.write_bytes(audio.content)

    assert output_file.exists()  # 파일이 생성되었는지 확인한다
    assert output_file.stat().st_size > 0  # 생성된 파일 크기가 0보다 큰지 검증한다

    saved_path = _write_artifact(audio.content, "ai_tts_simple3.mp3")  # 결과 파일을 아티팩트 폴더에 복사한다
    assert saved_path.exists()  # 복사된 아티팩트가 존재하는지 확인한다

# 음성 합성 옵션 테스트 (스트리밍)
def test_speech_model_options(tmp_path: Path, speech_client: OpenAI) -> None:
    
    speech_file_path = tmp_path / "ai_tts_options.mp3"  # 임시 디렉터리에 옵션 결과 파일 경로를 준비한다

    # https://platform.openai.com/docs/guides/text-to-speech#page-top
    # https://platform.openai.com/docs/api-reference/audio/createSpeech
    with speech_client.audio.speech.with_streaming_response.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input="안녕하세요 반갑습니다. 스프링부트는 자바 프레임워크 중에 가장 인기가 많은 프레임워크입니다."
    ) as response:
        response.stream_to_file(speech_file_path)

    assert speech_file_path.exists()  # 파일 생성 여부를 확인한다
    assert speech_file_path.stat().st_size > 0  # 파일 크기가 유효한지 검증한다

    saved_path = _write_artifact(speech_file_path.read_bytes(), "ai_tts_options4.mp3")  # 결과물을 아티팩트 폴더에 남긴다
    assert saved_path.exists()  # 아티팩트가 존재하는지 확인한다
