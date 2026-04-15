from datetime import date

import httpx
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from whatsapp_notion_bot.classifier import ClassificationError, ExpenseData
from whatsapp_notion_bot.config import Settings
from whatsapp_notion_bot.main import create_app


class StubClassifier:
    def __init__(self, expense: ExpenseData) -> None:
        self.expense = expense
        self.calls: list[str] = []

    async def classify(self, message_text: str) -> ExpenseData:
        self.calls.append(message_text)
        return self.expense


class FailingClassifier:
    def __init__(self, error: Exception) -> None:
        self.error = error
        self.calls: list[str] = []

    async def classify(self, message_text: str) -> ExpenseData:
        self.calls.append(message_text)
        raise self.error


class StubNotionClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def create_expense(self, **kwargs) -> dict:
        self.calls.append(kwargs)
        return {"id": "page_123"}


class FailingNotionClient:
    def __init__(self, error: Exception) -> None:
        self.error = error
        self.calls: list[dict] = []

    async def create_expense(self, **kwargs) -> dict:
        self.calls.append(kwargs)
        raise self.error


class StubZAPIClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    async def send_message(self, phone: str, text: str) -> dict:
        self.calls.append({"phone": phone, "text": text})
        return {"id": "msg_123"}


class FailingZAPIClient:
    def __init__(self, error: Exception) -> None:
        self.error = error
        self.calls: list[dict] = []

    async def send_message(self, phone: str, text: str) -> dict:
        self.calls.append({"phone": phone, "text": text})
        raise self.error


def build_settings() -> Settings:
    return Settings(
        ANTHROPIC_API_KEY="test-anthropic",
        ZAPI_INSTANCE_ID="instance",
        ZAPI_TOKEN="token",
        ZAPI_CLIENT_TOKEN="client-token",
        NOTION_TOKEN="notion-token",
        NOTION_DATABASE_ID="database-id",
        MY_PHONE_NUMBER="5511999999999",
    )


@pytest.mark.asyncio
async def test_webhook_processes_authorized_message() -> None:
    settings = build_settings()
    app = create_app(settings)
    classifier = StubClassifier(
        ExpenseData(
            amount=45.0,
            category="food",
            description="Almoco",
            date=date(2026, 4, 15),
        )
    )
    notion_client = StubNotionClient()
    zapi_client = StubZAPIClient()

    app.state.classifier = classifier
    app.state.notion_client = notion_client
    app.state.zapi_client = zapi_client

    with TestClient(app) as client:
        response = client.post(
            "/webhook",
            json={
                "phone": "55 11 99999-9999",
                "text": {
                    "message": "Gastei R$45 no almoco",
                },
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "status": "processed",
        "expense": {
            "amount": 45.0,
            "category": "food",
            "description": "Almoco",
            "date": "2026-04-15",
        },
        "confirmation": "\u2705 R$45.00 em Alimentacao - registrado",
    }
    assert classifier.calls == ["Gastei R$45 no almoco"]
    assert notion_client.calls == [
        {
            "amount": 45.0,
            "category": "food",
            "description": "Almoco",
            "expense_date": date(2026, 4, 15),
        }
    ]
    assert zapi_client.calls == [
        {
            "phone": "5511999999999",
            "text": "\u2705 R$45.00 em Alimentacao - registrado",
        }
    ]


@pytest.mark.asyncio
async def test_webhook_ignores_unauthorized_sender() -> None:
    settings = build_settings()
    app = create_app(settings)
    classifier = StubClassifier(
        ExpenseData(
            amount=30.0,
            category="transport",
            description="Taxi",
            date=date(2026, 4, 15),
        )
    )
    notion_client = StubNotionClient()
    zapi_client = StubZAPIClient()

    app.state.classifier = classifier
    app.state.notion_client = notion_client
    app.state.zapi_client = zapi_client

    with TestClient(app) as client:
        response = client.post(
            "/webhook",
            json={
                "phone": "5511888888888",
                "text": {
                    "message": "Gastei R$30 de taxi",
                },
            },
        )

    assert response.status_code == 200
    assert response.json() == {
        "status": "ignored",
        "reason": "sender_not_allowed",
    }
    assert classifier.calls == []
    assert notion_client.calls == []
    assert zapi_client.calls == []


@pytest.mark.asyncio
async def test_webhook_returns_422_and_sends_help_message_on_classification_error() -> None:
    settings = build_settings()
    app = create_app(settings)
    classifier = FailingClassifier(ClassificationError("classificacao invalida"))
    notion_client = StubNotionClient()
    zapi_client = StubZAPIClient()

    app.state.classifier = classifier
    app.state.notion_client = notion_client
    app.state.zapi_client = zapi_client

    with TestClient(app) as client:
        response = client.post(
            "/webhook",
            json={
                "phone": "5511999999999",
                "text": {
                    "message": "mensagem confusa",
                },
            },
        )

    assert response.status_code == 422
    assert response.json() == {"detail": "classificacao invalida"}
    assert notion_client.calls == []
    assert zapi_client.calls == [
        {
            "phone": "5511999999999",
            "text": "Nao consegui identificar esse gasto. Tente algo como: Gastei R$45 no almoco.",
        }
    ]


@pytest.mark.asyncio
async def test_webhook_returns_502_when_notion_fails() -> None:
    settings = build_settings()
    app = create_app(settings)
    classifier = StubClassifier(
        ExpenseData(
            amount=45.0,
            category="food",
            description="Almoco",
            date=date(2026, 4, 15),
        )
    )
    notion_client = FailingNotionClient(httpx.ConnectError("notion offline"))
    zapi_client = StubZAPIClient()

    app.state.classifier = classifier
    app.state.notion_client = notion_client
    app.state.zapi_client = zapi_client

    with TestClient(app) as client:
        response = client.post(
            "/webhook",
            json={
                "phone": "5511999999999",
                "text": {
                    "message": "Gastei R$45 no almoco",
                },
            },
        )

    assert response.status_code == 502
    assert response.json() == {"detail": "Falha ao gravar no Notion."}
    assert len(notion_client.calls) == 1
    assert zapi_client.calls == []


@pytest.mark.asyncio
async def test_webhook_returns_502_when_confirmation_fails() -> None:
    settings = build_settings()
    app = create_app(settings)
    classifier = StubClassifier(
        ExpenseData(
            amount=45.0,
            category="food",
            description="Almoco",
            date=date(2026, 4, 15),
        )
    )
    notion_client = StubNotionClient()
    zapi_client = FailingZAPIClient(httpx.ConnectError("zapi offline"))

    app.state.classifier = classifier
    app.state.notion_client = notion_client
    app.state.zapi_client = zapi_client

    with TestClient(app) as client:
        response = client.post(
            "/webhook",
            json={
                "phone": "5511999999999",
                "text": {
                    "message": "Gastei R$45 no almoco",
                },
            },
        )

    assert response.status_code == 502
    assert response.json() == {"detail": "Falha ao enviar confirmacao no WhatsApp."}
    assert len(notion_client.calls) == 1
    assert zapi_client.calls == [
        {
            "phone": "5511999999999",
            "text": "\u2705 R$45.00 em Alimentacao - registrado",
        }
    ]


@pytest.mark.asyncio
async def test_webhook_rate_limit_returns_429() -> None:
    settings = build_settings()
    app = create_app(settings)

    with patch("whatsapp_notion_bot.main._webhook_limiter.allow", return_value=False):
        with TestClient(app) as client:
            response = client.post(
                "/webhook",
                json={
                    "phone": "5511999999999",
                    "text": {
                        "message": "Gastei R$45 no almoco",
                    },
                },
            )

    assert response.status_code == 429
    assert response.json() == {"detail": "Rate limit exceeded for webhook"}
