"""Tool-calling workflow tests mirroring the Spring Boot example."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any, Callable, Dict

import pytest
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY_SET = bool(os.getenv("OPENAI_API_KEY"))
pytestmark = pytest.mark.skipif(
    not API_KEY_SET, reason="requires OPENAI_API_KEY environment variable"
)

CHAT_TOOL_MODEL = os.getenv("CHAT_TOOL_MODEL", os.getenv("CHAT_MODEL", "gpt-4o-mini"))


@dataclass
class ProductOrder:
    order_number: str
    product_name: str
    shipping_address: str
    shipping_status: str


class ProductOrderRepository:
    def __init__(self) -> None:
        self._orders: dict[str, ProductOrder] = {}

    def save(self, order: ProductOrder) -> None:
        self._orders[order.order_number] = order

    def delete_all(self) -> None:
        self._orders.clear()

    def list_orders(self) -> list[dict[str, str]]:
        return [
            {
                "order_number": order.order_number,
                "product_name": order.product_name,
                "shipping_address": order.shipping_address,
                "shipping_status": order.shipping_status,
            }
            for order in self._orders.values()
        ]

    def get_shipping_status(self, product_name: str) -> dict[str, str]:
        order = self._find_by_product_name(product_name)
        if not order:
            return {"success": False, "message": f"상품 '{product_name}' 주문을 찾을 수 없습니다."}
        return {
            "success": True,
            "order_number": order.order_number,
            "product_name": order.product_name,
            "shipping_status": order.shipping_status,
        }

    def cancel_order(self, product_name: str) -> dict[str, str]:
        order = self._find_by_product_name(product_name)
        if not order:
            return {"success": False, "message": f"상품 '{product_name}' 주문이 존재하지 않습니다."}

        order.shipping_status = "취소됨"
        return {
            "success": True,
            "order_number": order.order_number,
            "product_name": order.product_name,
            "shipping_status": order.shipping_status,
        }

    def _find_by_product_name(self, product_name: str) -> ProductOrder | None:
        for order in self._orders.values():
            if order.product_name == product_name:
                return order
        return None


@pytest.fixture(scope="module")
def chat_tool_client() -> OpenAI:
    return OpenAI()


@pytest.fixture
def product_order_repository() -> ProductOrderRepository:
    repository = ProductOrderRepository()
    repository.save(
        ProductOrder(
            order_number="1000000",
            product_name="맥북에어",
            shipping_address="서울시 영등포구 여의도동",
            shipping_status="배송중",
        )
    )
    repository.save(
        ProductOrder(
            order_number="1000001",
            product_name="아이폰",
            shipping_address="서울시 강남구 역삼동",
            shipping_status="준비중",
        )
    )
    yield repository
    repository.delete_all()


def _tool_definitions() -> list[dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "list_product_orders",
                "description": "사용자의 상품 주문 목록을 확인합니다.",
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_shipping_status",
                "description": "특정 상품의 배송 상태를 조회합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_name": {
                            "type": "string",
                            "description": "확인하려는 상품 이름",
                        }
                    },
                    "required": ["product_name"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "cancel_product_order",
                "description": "특정 상품의 주문을 취소합니다.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_name": {
                            "type": "string",
                            "description": "취소하려는 상품 이름",
                        }
                    },
                    "required": ["product_name"],
                },
            },
        },
    ]


def _tool_router(repository: ProductOrderRepository) -> Dict[str, Callable[[dict[str, Any]], dict[str, Any]]]:
    return {
        "list_product_orders": lambda _: {"orders": repository.list_orders()},
        "get_shipping_status": lambda payload: repository.get_shipping_status(
            payload["product_name"]
        ),
        "cancel_product_order": lambda payload: repository.cancel_order(
            payload["product_name"]
        ),
    }


# 상품 주문 관련 툴 호출 테스트
def test_product_order_tool_flow(
    chat_tool_client: OpenAI, product_order_repository: ProductOrderRepository
) -> None:
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "당신은 전자상거래 고객센터 챗봇입니다. 사용자의 요청을 처리할 때는 제공된 도구만을 사용해 답변하세요."
                " 사용자가 주문 취소를 요청하면 추가 확인 없이 반드시 'cancel_product_order' 함수를 호출해 취소를 완료하세요."
            ),
        },
        {"role": "user", "content": "맥북에어 주문을 취소해 주세요."},
    ]

    tools = _tool_definitions()
    tool_router = _tool_router(product_order_repository)

    initial_raw = chat_tool_client.chat.completions.with_raw_response.create(
        model=CHAT_TOOL_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    initial_response = initial_raw.parse()

    assistant_message = initial_response.choices[0].message
    tool_calls = assistant_message.tool_calls or []

    # 모델이 도구를 호출하지 않은 경우 한 차례 더 유도 메시지를 보낸다.
    if not tool_calls:
        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content or "",
            }
        )
        messages.append({"role": "user", "content": "이미 동의했으니 바로 취소를 진행해 주세요."})

        retry_raw = chat_tool_client.chat.completions.with_raw_response.create(
            model=CHAT_TOOL_MODEL,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        initial_response = retry_raw.parse()
        assistant_message = initial_response.choices[0].message
        tool_calls = assistant_message.tool_calls or []

    if tool_calls:
        messages.append(
            {
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": call.id,
                        "type": call.type,
                        "function": {
                            "name": call.function.name,
                            "arguments": call.function.arguments,
                        },
                    }
                    for call in tool_calls
                ],
            }
        )

    for call in tool_calls:
        arguments = json.loads(call.function.arguments or "{}")
        handler = tool_router.get(call.function.name)
        if not handler:
            output_payload = {"success": False, "message": "지원하지 않는 도구입니다."}
        else:
            output_payload = handler(arguments)
        messages.append(
            {
                "role": "tool",
                "tool_call_id": call.id,
                "name": call.function.name,
                "content": json.dumps(output_payload, ensure_ascii=False),
            }
        )

    final_raw = chat_tool_client.chat.completions.with_raw_response.create(
        model=CHAT_TOOL_MODEL,
        messages=messages,
    )
    final_response = final_raw.parse()

    usage = final_response.usage
    assert usage is not None
    print(
        "promptTokens =",
        usage.prompt_tokens,
        "completionTokens =",
        usage.completion_tokens,
        "totalTokens =",
        usage.total_tokens,
    )

    headers = dict(final_raw.headers)
    rate_limit_headers = {
        key: headers[key]
        for key in headers
        if key.startswith("x-ratelimit") or key == "x-request-id"
    }
    print(f"rate limit headers = {rate_limit_headers}")

    outputs = [choice.message.content or "" for choice in final_response.choices]
    for idx, content in enumerate(outputs, start=1):
        print(f"response[{idx}] = {content}")

    macbook_order = product_order_repository.get_shipping_status("맥북에어")
    assert macbook_order["success"] is True
    assert macbook_order["shipping_status"] == "취소됨"
    assert any("취소" in output for output in outputs)
