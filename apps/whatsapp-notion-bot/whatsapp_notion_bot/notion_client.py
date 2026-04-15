from __future__ import annotations

from datetime import date

import httpx


class NotionClient:
    def __init__(
        self,
        token: str,
        database_id: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._database_id = database_id
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(
            base_url="https://api.notion.com/v1",
            headers={
                "Authorization": f"Bearer {token}",
                "Notion-Version": "2022-06-28",
                "Content-Type": "application/json",
            },
            timeout=20.0,
        )

    async def create_expense(
        self,
        *,
        amount: float,
        category: str,
        description: str,
        expense_date: date,
    ) -> dict:
        payload = {
            "parent": {"database_id": self._database_id},
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": description,
                            }
                        }
                    ]
                },
                "Amount": {"number": amount},
                "Category": {"select": {"name": category}},
                "Date": {"date": {"start": expense_date.isoformat()}},
            },
        }
        response = await self._client.post("/pages", json=payload)
        response.raise_for_status()
        return response.json()

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()
