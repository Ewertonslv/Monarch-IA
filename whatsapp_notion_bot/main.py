from __future__ import annotations

import logging
import re
from contextlib import asynccontextmanager
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Request

from whatsapp_notion_bot.classifier import ClassificationError, ExpenseClassifier
from whatsapp_notion_bot.config import Settings, get_settings
from whatsapp_notion_bot.notion_client import NotionClient
from whatsapp_notion_bot.zapi_client import ZAPIClient


logger = logging.getLogger(__name__)

CATEGORY_LABELS = {
    "food": "Alimentacao",
    "transport": "Transporte",
    "health": "Saude",
    "entertainment": "Lazer",
    "housing": "Moradia",
    "other": "Outros",
}


def _normalize_phone(phone: str) -> str:
    return re.sub(r"\D+", "", phone)


def _extract_phone(payload: dict[str, Any]) -> str | None:
    candidates = [
        payload.get("phone"),
        payload.get("from"),
        payload.get("sender"),
        payload.get("chatLid"),
        payload.get("connectedPhone"),
        payload.get("participantPhone"),
        payload.get("senderPhone"),
    ]

    sender = payload.get("sender")
    if isinstance(sender, dict):
        candidates.extend(
            [
                sender.get("phone"),
                sender.get("id"),
                sender.get("sender"),
            ]
        )

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return _normalize_phone(candidate)
    return None


def _extract_text(payload: dict[str, Any]) -> str | None:
    candidates = [
        payload.get("text"),
        payload.get("message"),
        payload.get("body"),
    ]

    text_obj = payload.get("text")
    if isinstance(text_obj, dict):
        candidates.extend(
            [
                text_obj.get("message"),
                text_obj.get("body"),
                text_obj.get("text"),
            ]
        )

    message_obj = payload.get("message")
    if isinstance(message_obj, dict):
        candidates.extend(
            [
                message_obj.get("text"),
                message_obj.get("body"),
                message_obj.get("conversation"),
            ]
        )

    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def _format_confirmation(amount: float, category: str) -> str:
    label = CATEGORY_LABELS.get(category, "Outros")
    return f"\u2705 R${amount:.2f} em {label} - registrado"


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    app.state.classifier = ExpenseClassifier(api_key=settings.anthropic_api_key)
    app.state.notion_client = NotionClient(
        token=settings.notion_token,
        database_id=settings.notion_database_id,
    )
    app.state.zapi_client = ZAPIClient(
        instance_id=settings.zapi_instance_id,
        token=settings.zapi_token,
        client_token=settings.zapi_client_token,
    )
    try:
        yield
    finally:
        await app.state.notion_client.aclose()
        await app.state.zapi_client.aclose()


def create_app(settings: Settings | None = None) -> FastAPI:
    app = FastAPI(title="WhatsApp Notion Bot", lifespan=lifespan if settings is None else None)

    if settings is not None:
        app.state.settings = settings
        app.state.classifier = ExpenseClassifier(api_key=settings.anthropic_api_key)
        app.state.notion_client = NotionClient(
            token=settings.notion_token,
            database_id=settings.notion_database_id,
        )
        app.state.zapi_client = ZAPIClient(
            instance_id=settings.zapi_instance_id,
            token=settings.zapi_token,
            client_token=settings.zapi_client_token,
        )

    @app.get("/health")
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/webhook")
    async def receive_webhook(request: Request) -> dict[str, Any]:
        payload = await request.json()
        sender_phone = _extract_phone(payload)
        message_text = _extract_text(payload)
        app_settings = request.app.state.settings

        if not sender_phone or not message_text:
            logger.warning("Payload invalido recebido no webhook.")
            raise HTTPException(status_code=400, detail="Payload invalido.")

        if _normalize_phone(app_settings.my_phone_number) != sender_phone:
            logger.info("Mensagem ignorada para remetente nao autorizado: %s", sender_phone)
            return {"status": "ignored", "reason": "sender_not_allowed"}

        try:
            expense = await request.app.state.classifier.classify(message_text)
        except ClassificationError as exc:
            logger.warning("Falha ao classificar mensagem do WhatsApp: %s", exc)
            await request.app.state.zapi_client.send_message(
                sender_phone,
                "Nao consegui identificar esse gasto. Tente algo como: Gastei R$45 no almoco.",
            )
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        try:
            await request.app.state.notion_client.create_expense(
                amount=expense.amount,
                category=expense.category,
                description=expense.description,
                expense_date=expense.date,
            )
        except httpx.HTTPError as exc:
            logger.exception("Falha ao criar pagina no Notion.")
            raise HTTPException(status_code=502, detail="Falha ao gravar no Notion.") from exc

        confirmation = _format_confirmation(expense.amount, expense.category)
        try:
            await request.app.state.zapi_client.send_message(sender_phone, confirmation)
        except httpx.HTTPError as exc:
            logger.exception("Falha ao enviar confirmacao pela Z-API.")
            raise HTTPException(status_code=502, detail="Falha ao enviar confirmacao no WhatsApp.") from exc

        logger.info(
            "Gasto registrado com sucesso. telefone=%s categoria=%s valor=%.2f",
            sender_phone,
            expense.category,
            expense.amount,
        )
        return {
            "status": "processed",
            "expense": expense.model_dump(mode="json"),
            "confirmation": confirmation,
        }

    return app


app = create_app()
