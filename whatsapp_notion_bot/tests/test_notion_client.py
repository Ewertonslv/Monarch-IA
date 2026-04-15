from datetime import date

import httpx
import pytest

from whatsapp_notion_bot.notion_client import NotionClient


@pytest.mark.asyncio
async def test_create_expense_posts_expected_payload() -> None:
    captured: dict = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["json"] = request.content.decode()
        return httpx.Response(200, json={"id": "page_123"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://api.notion.com/v1",
        headers={
            "Authorization": "Bearer notion-test",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        },
    ) as http_client:
        client = NotionClient(
            token="notion-test",
            database_id="db_123",
            client=http_client,
        )
        response = await client.create_expense(
            amount=45.0,
            category="food",
            description="Almoco",
            expense_date=date(2026, 4, 15),
        )

    assert response == {"id": "page_123"}
    assert captured["url"] == "https://api.notion.com/v1/pages"
    assert '"Amount":{"number":45.0}' in captured["json"]
    assert '"name":"food"' in captured["json"]
    assert '"start":"2026-04-15"' in captured["json"]
