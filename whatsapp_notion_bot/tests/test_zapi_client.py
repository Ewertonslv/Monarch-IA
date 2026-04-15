import httpx
import pytest

from whatsapp_notion_bot.zapi_client import ZAPIClient


@pytest.mark.asyncio
async def test_send_message_posts_expected_payload() -> None:
    captured: dict = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        captured["headers"] = dict(request.headers)
        captured["json"] = request.content.decode()
        return httpx.Response(200, json={"zaapId": "msg_123"})

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="https://api.z-api.io/instances/instance/token/token",
        headers={
            "Client-Token": "client-token",
            "Content-Type": "application/json",
        },
    ) as http_client:
        client = ZAPIClient(
            instance_id="instance",
            token="token",
            client_token="client-token",
            client=http_client,
        )
        response = await client.send_message("5511999999999", "teste")

    assert response == {"zaapId": "msg_123"}
    assert captured["url"] == "https://api.z-api.io/instances/instance/token/token/send-text"
    assert '"phone":"5511999999999"' in captured["json"]
    assert '"message":"teste"' in captured["json"]
