"""OpenAI chat workflow tests mirroring the Spring Boot examples."""
from __future__ import annotations

import base64
import os
from pathlib import Path

import pytest
from openai import OpenAI

API_KEY_SET = bool(os.getenv("OPENAI_API_KEY"))
pytestmark = pytest.mark.skipif(
    not API_KEY_SET, reason="requires OPENAI_API_KEY environment variable"
)

CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-4o-mini")
CHAT_AUDIO_MODEL = os.getenv("CHAT_AUDIO_MODEL", "gpt-4o-audio-preview")
CHAT_IMAGE_MODEL = os.getenv("CHAT_IMAGE_MODEL", CHAT_MODEL)

ASSETS_DIR = Path("tests/assets")
ARTIFACT_ROOT = Path(os.getenv("AUDIO_TEST_ARTIFACTS", "tests/artifacts"))


@pytest.fixture(scope="module")
def chat_client() -> OpenAI:
    return OpenAI()


def _ensure_artifact_dir() -> Path:
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    return ARTIFACT_ROOT


# 간단한 채팅 질의 테스트
def test_chat_model_simple(chat_client: OpenAI) -> None:
    # https://platform.openai.com/docs/api-reference/chat/create?lang=python
    response = chat_client.chat.completions.create(
        model="gpt-4o-mini",
        # 최종 사용자가 보낸 메시지로, 프롬프트나 추가 컨텍스트 정보가 포함되어 있습니다.
        messages=[{"role": "user", "content": "서울 올림픽은 몇회 올림픽이야?"}],
    )
    content = response.choices[0].message.content
    assert content
    print(f"test_chat_model_simple response = {content}")


# 시스템 메시지를 포함한 채팅 테스트
def test_chat_model_message(chat_client: OpenAI) -> None:
    # https://platform.openai.com/docs/api-reference/chat/create?lang=python
    response = chat_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            # 사용자가 보낸 메시지와 관계없이 모델이 따라야 하는 개발자 제공 지침
            {"role": "system", "content": "답변은 간략하게 하고, 마지막에는 실제 뉴스를 참고하라는 말을 해 주세요"},
            {"role": "user", "content": "서울 올림픽에 대해 알려 주세요"},
        ],
        temperature=1.0,
    )
    content = response.choices[0].message.content
    print(f"test_chat_model_message response = {content}")
    assert content.endswith("참고하세요.") or "참고" in content


# 대화 히스토리 컨텍스트 테스트
def test_chat_model_message_context(chat_client: OpenAI) -> None:
    history = [
        {"role": "system", "content": "간략하게 답변해 주세요."},
        {
            "role": "user",
            "content": "서울 올림픽에 대해 알려 주세요",
        },
        {
            "role": "assistant",
            "content": (
                "서울 올림픽, 공식명칭은 제24회 하계 올림픽대회는 1988년 9월 17일부터 10월 2일까지 "
                "대한민국 서울에서 개최되었습니다."
            ),
        },
        {"role": "user", "content": "그럼 바로 그 이전 올림픽은 어디야?"},
        {
            "role": "assistant",
            "content": "바로 이전 올림픽은 1984년 하계 올림픽으로, 미국 로스앤젤레스에서 개최되었습니다.",
        },
        {"role": "user", "content": "그럼 그 두개의 올림픽중 참여 국가는 어디가 많아?"},
    ]
    response = chat_client.chat.completions.create(
        model=CHAT_MODEL,
        messages=history,
        temperature=0.6
    )
    content = response.choices[0].message.content
    print(f"test_chat_model_message_context response = {content}")
    assert content
    assert "국" in content or "country" in content.lower()


# 다중 응답과 사용량·레이트리밋 확인
def test_chat_prompt_with_usage_and_ratelimit(chat_client: OpenAI) -> None:

    raw = chat_client.chat.completions.with_raw_response.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "간략하게 답변해 주세요."},
            {"role": "user", "content": "서울 올림픽에 대해 알려 주세요"},
            {
                "role": "assistant", # 사용자 메시지에 대한 응답으로 모델이 보낸 메시지입니다.
                "content": (
                    "서울 올림픽, 공식명칭은 제24회 하계 올림픽대회는 1988년 9월 17일부터 10월 2일까지 대한민국 서울에서"
                    " 개최되었습니다."
                ),
            },
            {"role": "user", "content": "그럼 바로 그 이전 올림픽은 어디야?"},
            {
                "role": "assistant", # 사용자 메시지에 대한 응답으로 모델이 보낸 메시지입니다.
                "content": "바로 이전 올림픽은 1984년 하계 올림픽으로, 미국 로스앤젤레스에서 개최되었습니다.",
            },
            {"role": "user", "content": "그럼 그 두개의 올림픽중 참여 국가는 어디가 많아?"},
        ],
        temperature=1.0,
        n=2,  # 각 입력 메시지에 대해 생성할 채팅 완료 선택지의 개수입니다. 모든 선택지에서 생성된 토큰 수에 따라 요금이 부과됩니다. 비용을 최소화하려면 n을 1로 유지하세요.
    )

    response = raw.parse()
    assert response.choices

    usage = response.usage
    assert usage is not None
    print(f"usage tokens: prompt={usage.prompt_tokens} completion={usage.completion_tokens} total={usage.total_tokens}")
    assert usage.total_tokens > 0

    headers = dict(raw.headers)
    print(f"rate limit headers: { {k: headers[k] for k in headers if k.startswith("x-ratelimit") or k == "x-request-id"} }")
    assert "x-request-id" in headers

    outputs = [choice.message.content for choice in response.choices]
    for idx, out in enumerate(outputs, start=1):
        print(f"response[{idx}] = {out}")
    assert all(outputs)


@pytest.mark.skipif(not (ASSETS_DIR / "Disney_World_1.jpg").exists(), reason="requires Disney_World_1.jpg asset")
# 이미지 기반 제목 제안 테스트
def test_chat_model_image(chat_client: OpenAI) -> None:
    image_path = ASSETS_DIR / "Disney_World_1.jpg"
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")

    response = chat_client.chat.completions.create(
        model=CHAT_IMAGE_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "사진에 제목을 붙인다면 무엇이 좋을까?"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded}", "detail": "auto"},
                    },
                ],
            }
        ],
    )
    content = response.choices[0].message.content or ""
    print(f"test_chat_model_image response = {content}")
    assert content


@pytest.mark.skipif(not (ASSETS_DIR / "Disney_World_2.jpg").exists(), reason="requires Disney_World_2.jpg asset")
# 이미지 기반 시 제안 테스트
def test_chat_model_image_poem(chat_client: OpenAI) -> None:
    image_path = ASSETS_DIR / "Disney_World_2.jpg"
    encoded = base64.b64encode(image_path.read_bytes()).decode("utf-8")

    response = chat_client.chat.completions.create(
        model=CHAT_IMAGE_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "사진 속의 풍경을 멋진 시로 써 주세요"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{encoded}", "detail": "auto"},
                    },
                ],
            }
        ],
    )
    content = response.choices[0].message.content or ""
    print(f"test_chat_model_image_poem response = {content}")
    assert content


@pytest.mark.skipif(not (ASSETS_DIR / "sample_audio.mp3").exists(), reason="requires sample_audio.mp3 asset")
# 오디오 입력 요약 테스트
def test_chat_model_audio_input(chat_client: OpenAI) -> None:
    audio_path = ASSETS_DIR / "sample_audio.mp3"
    audio_b64 = base64.b64encode(audio_path.read_bytes()).decode("utf-8")

    response = chat_client.chat.completions.create(
        model=CHAT_AUDIO_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "이 오디오 파일의 내용에 대해 요약해 주세요"},
                    {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "mp3"}},
                ],
            }
        ],
        modalities=["text"],
    )

    message = response.choices[0].message
    text_out = message.content
    if not text_out and message.audio:
        text_out = message.audio.transcript
    print(f"test_chat_model_audio_input response = {text_out}")
    assert text_out


# 텍스트 요청에 대한 오디오 생성 테스트
def test_chat_model_audio_output(chat_client: OpenAI) -> None:
    response = chat_client.chat.completions.create(
        model=CHAT_AUDIO_MODEL,
        messages=[{"role": "user", "content": "스프링부트에 대해 간단하게 설명해 주세요"}],
        modalities=["text", "audio"],
        audio={"voice": "nova", "format": "mp3"},
    )

    message = response.choices[0].message
    text_out = message.content or ""
    if not text_out and message.audio:
        text_out = message.audio.transcript 

    print(f"test_chat_model_audio_output text = {text_out}")
    assert text_out
    assert message.audio is not None

    artifact_dir = _ensure_artifact_dir()
    audio_path = artifact_dir / "ai_chat_audio.mp3"
    audio_path.write_bytes(base64.b64decode(message.audio.data))


@pytest.mark.skipif(not (ASSETS_DIR / "sample_audio_ask.mp3").exists(), reason="requires sample_audio_ask.mp3 asset")
# 오디오 입력과 오디오 출력 결합 테스트
def test_chat_model_audio_input_output(chat_client: OpenAI) -> None:
    audio_path = ASSETS_DIR / "sample_audio_ask.mp3"
    audio_b64 = base64.b64encode(audio_path.read_bytes()).decode("utf-8")

    response = chat_client.chat.completions.create(
        model=CHAT_AUDIO_MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "질문에 친절하고 간략하게 답변해 주세요"},
                    {"type": "input_audio", "input_audio": {"data": audio_b64, "format": "mp3"}},
                ],
            }
        ],
        modalities=["text", "audio"],
        audio={"voice": "nova", "format": "mp3"},
    )

    message = response.choices[0].message
    text_out = message.content or ""
    if not text_out and message.audio:
        text_out = message.audio.transcript
    print(f"test_chat_model_audio_input_output text = {text_out}")
    assert text_out
    assert message.audio is not None

    artifact_dir = _ensure_artifact_dir()
    (artifact_dir / "ai_chat_audio_answer.mp3").write_bytes(base64.b64decode(message.audio.data))
