import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import anthropic

from config import config
from core.task import Task

logger = logging.getLogger(__name__)

_client = anthropic.AsyncAnthropic(api_key=config.anthropic_api_key)

OPUS_MODEL = "claude-opus-4-6"
SONNET_MODEL = "claude-sonnet-4-6"
HAIKU_MODEL = "claude-haiku-4-5-20251001"


@dataclass
class AgentResult:
    output: dict[str, Any]
    confidence: float
    concerns: list[str]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentResult":
        return cls(
            output=data,
            confidence=float(data.get("confidence", 1.0)),
            concerns=data.get("concerns", []),
        )


class BaseAgent(ABC):
    name: str = "base"
    model: str = OPUS_MODEL
    system_prompt: str = ""
    tools: list[dict[str, Any]] = []
    max_tokens: int = 8096

    def _build_system(self) -> list[dict[str, Any]]:
        """System prompt with prompt caching — reduces cost ~80% on repeated calls."""
        return [
            {
                "type": "text",
                "text": self.system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    @abstractmethod
    async def build_user_message(self, task: Task) -> str:
        """Build the user message for this agent given the task context."""

    async def _call_claude(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> anthropic.types.Message:
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": self._build_system(),
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
        return await _client.messages.create(**kwargs)

    async def _handle_tool_use(
        self,
        message: anthropic.types.Message,
        messages: list[dict[str, Any]],
    ) -> anthropic.types.Message:
        """Process tool_use blocks and continue the conversation loop."""
        tool_results = []
        for block in message.content:
            if block.type == "tool_use":
                try:
                    result = await self.execute_tool(block.name, block.input)
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(result, default=str),
                    })
                except Exception as e:
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Error: {e}",
                        "is_error": True,
                    })

        messages.append({"role": "assistant", "content": message.content})
        messages.append({"role": "user", "content": tool_results})
        return await self._call_claude(messages, self.tools or None)

    async def execute_tool(self, name: str, inputs: dict[str, Any]) -> Any:
        """Override in subclasses to handle tool calls."""
        raise NotImplementedError(f"Tool not implemented: {name}")

    def _extract_json(self, text: str) -> dict[str, Any]:
        """Extract JSON from text — handles markdown code blocks."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        return json.loads(text)

    async def run(self, task: Task) -> AgentResult:
        user_content = await self.build_user_message(task)
        messages: list[dict[str, Any]] = [{"role": "user", "content": user_content}]

        logger.info(f"[{self.name}] Starting for task {task.task_id}")
        message = await self._call_claude(messages, self.tools or None)

        # Tool use loop — keep going until Claude stops using tools
        while message.stop_reason == "tool_use":
            message = await self._handle_tool_use(message, messages)

        if not message.content:
            raise ValueError(f"[{self.name}] Got empty response from Claude")

        text_blocks = [b for b in message.content if b.type == "text"]
        if not text_blocks:
            raise ValueError(f"[{self.name}] No text block in response")

        raw = self._extract_json(text_blocks[0].text)
        result = AgentResult.from_dict(raw)
        logger.info(f"[{self.name}] Done. Confidence: {result.confidence:.2f}")
        return result
