from datetime import date
from types import SimpleNamespace

import pytest

from whatsapp_notion_bot.classifier import (
    MODEL_NAME,
    ClassificationError,
    ExpenseClassifier,
)


class FakeMessagesAPI:
    def __init__(self, response_text: str) -> None:
        self.response_text = response_text
        self.calls: list[dict] = []

    async def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            content=[
                SimpleNamespace(type="text", text=self.response_text),
            ]
        )


class FakeAnthropicClient:
    def __init__(self, response_text: str) -> None:
        self.messages = FakeMessagesAPI(response_text)


@pytest.mark.asyncio
async def test_classifier_extracts_structured_expense() -> None:
    client = FakeAnthropicClient(
        '{"amount": 45.0, "category": "food", "description": "Almoco", "date": "2026-04-15"}'
    )
    classifier = ExpenseClassifier(api_key="test-key", client=client)

    result = await classifier.classify("Gastei R$45 no almoco", today=date(2026, 4, 15))

    assert result.amount == 45.0
    assert result.category == "food"
    assert result.description == "Almoco"
    assert result.date == date(2026, 4, 15)

    request_payload = client.messages.calls[0]
    assert request_payload["model"] == MODEL_NAME
    assert request_payload["system"][0]["cache_control"] == {"type": "ephemeral"}
    assert "Data de referencia: 2026-04-15" in request_payload["messages"][0]["content"]


@pytest.mark.asyncio
async def test_classifier_raises_for_invalid_json() -> None:
    client = FakeAnthropicClient("nao e json")
    classifier = ExpenseClassifier(api_key="test-key", client=client)

    with pytest.raises(ClassificationError):
        await classifier.classify("mensagem invalida")
