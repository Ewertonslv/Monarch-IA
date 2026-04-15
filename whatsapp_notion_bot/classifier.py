from __future__ import annotations

import json
from datetime import date
from typing import Any

from anthropic import AsyncAnthropic
from pydantic import BaseModel, ConfigDict, Field, ValidationError


MODEL_NAME = "claude-haiku-4-5-20251001"

SYSTEM_PROMPT = """
Voce e um classificador de gastos pessoais.
Extraia a mensagem do usuario para um JSON valido com estas chaves:
- amount: numero decimal positivo
- category: uma destas opcoes exatas: food, transport, health, entertainment, housing, other
- description: texto curto e claro em portugues
- date: data no formato ISO YYYY-MM-DD

Regras:
- Considere a mensagem como um gasto financeiro pessoal.
- Se a data nao for informada, use a data de hoje recebida no contexto.
- Nunca inclua markdown, comentarios ou texto fora do JSON.
- Normalize a categoria para uma das opcoes permitidas.
""".strip()


class ClassificationError(RuntimeError):
    """Raised when Claude does not return a valid expense payload."""


class ExpenseData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    amount: float = Field(gt=0)
    category: str
    description: str = Field(min_length=1)
    date: date


class ExpenseClassifier:
    def __init__(self, api_key: str, client: AsyncAnthropic | None = None) -> None:
        self._client = client or AsyncAnthropic(api_key=api_key)

    async def classify(self, message_text: str, *, today: date | None = None) -> ExpenseData:
        reference_date = today or date.today()
        response = await self._client.messages.create(
            model=MODEL_NAME,
            max_tokens=300,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Data de referencia: "
                        f"{reference_date.isoformat()}\n"
                        f"Mensagem: {message_text}"
                    ),
                }
            ],
        )

        payload = self._extract_text(response)
        try:
            raw_data = json.loads(payload)
            return ExpenseData.model_validate(raw_data)
        except (json.JSONDecodeError, ValidationError) as exc:
            raise ClassificationError("Claude retornou uma classificacao invalida.") from exc

    @staticmethod
    def _extract_text(response: Any) -> str:
        parts = getattr(response, "content", None)
        if not parts:
            raise ClassificationError("Claude nao retornou conteudo.")

        text_chunks = [
            getattr(part, "text", "")
            for part in parts
            if getattr(part, "type", "") == "text" and getattr(part, "text", "")
        ]
        if not text_chunks:
            raise ClassificationError("Claude nao retornou texto utilizavel.")
        return "".join(text_chunks).strip()
