from __future__ import annotations

import httpx


class ZAPIClient:
    def __init__(
        self,
        instance_id: str,
        token: str,
        client_token: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url=f"https://api.z-api.io/instances/{instance_id}/token/{token}",
            headers={
                "Client-Token": client_token,
                "Content-Type": "application/json",
            },
            timeout=20.0,
        )

    async def send_message(self, phone: str, text: str) -> dict:
        response = await self._client.post(
            "/send-text",
            json={
                "phone": phone,
                "message": text,
            },
        )
        response.raise_for_status()
        return response.json()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()
