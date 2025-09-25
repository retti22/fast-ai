"""Image generation workflow tests mirroring the Spring Boot example."""
from __future__ import annotations

import base64
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

IMAGE_MODEL = os.getenv("IMAGE_MODEL", "dall-e-3")
IMAGE_STYLE = os.getenv("IMAGE_STYLE", "natural")
IMAGE_QUALITY = os.getenv("IMAGE_QUALITY", "hd")
IMAGE_SIZE = os.getenv("IMAGE_SIZE", "1024x1024")
ARTIFACT_ROOT = Path(os.getenv("IMAGE_TEST_ARTIFACTS", "tests/artifacts"))


@pytest.fixture(scope="module")
def image_client() -> OpenAI:
    return OpenAI()


def _ensure_artifact_dir() -> Path:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    return ARTIFACT_ROOT


# 간단한 이미지 생성 테스트
def test_image_model_options(image_client: OpenAI) -> None:
    prompt = (
        "수채화 스타일로 그린 화성 탐사 로버 그림이 필요해.\n"
        "2족 보행 로봇이 함께 탐사하는 모습으로 해 줘.\n"
        "붓으로 그린 듯한 부드러운 필치와 여백의 미를 살려서 표현해 줘."
    )

    response = image_client.images.generate(
        model=IMAGE_MODEL,  # 예: 'dall-e-2', 'dall-e-3'
        prompt=prompt,
        size=IMAGE_SIZE,  # 예: '1024x1024', '512x512'
        quality=IMAGE_QUALITY,  # 예: 'standard', 'hd'
        style=IMAGE_STYLE,  # 예: 'natural', 'vivid'
        response_format="b64_json",  # 'url' 또는 base64 JSON 데이터
    )

    assert response.data
    image_data = response.data[0]
    assert image_data.b64_json

    image_bytes = base64.b64decode(image_data.b64_json)
    artifact_dir = _ensure_artifact_dir()
    output_path = artifact_dir / "ai_image_hd.png"
    output_path.write_bytes(image_bytes)

    print(f"test_image_model_options saved image to {output_path}")
    assert output_path.exists()
    assert output_path.stat().st_size > 0
