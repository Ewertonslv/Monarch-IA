import asyncio
import json
import logging
import os
import re
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import anthropic

from config import config
from core.task import Task

logger = logging.getLogger(__name__)

_api_client = anthropic.AsyncAnthropic(api_key=config.anthropic_api_key) if config.anthropic_api_key else None

OPUS_MODEL = "claude-opus-4-6"
SONNET_MODEL = "claude-sonnet-4-6"
HAIKU_MODEL = "claude-haiku-4-5-20251001"

# Path to the claude CLI (Claude Code binary — uses Pro subscription)
_CLAUDE_BIN: str | None = None

def _find_claude_bin() -> str | None:
    """Locate the claude CLI binary."""
    # Check PATH first
    import shutil
    if shutil.which("claude"):
        return "claude"
    # Known VS Code extension path on Windows
    vscode_ext = Path.home() / ".vscode" / "extensions"
    if vscode_ext.exists():
        for p in sorted(vscode_ext.glob("anthropic.claude-code-*/resources/native-binary/claude.exe"), reverse=True):
            if p.exists():
                return str(p)
    return None


def _get_claude_bin() -> str:
    global _CLAUDE_BIN
    if _CLAUDE_BIN is None:
        _CLAUDE_BIN = _find_claude_bin()
    if not _CLAUDE_BIN:
        raise RuntimeError("claude CLI not found. Install Claude Code or add it to PATH.")
    return _CLAUDE_BIN


# ---------------------------------------------------------------------------
# Mock message types (local mode — no real Anthropic SDK objects)
# ---------------------------------------------------------------------------

@dataclass
class _LocalTextBlock:
    type: str = "text"
    text: str = ""


@dataclass
class _LocalMessage:
    content: list = field(default_factory=list)
    stop_reason: str = "end_turn"


# ---------------------------------------------------------------------------
# Shared tool definitions
# ---------------------------------------------------------------------------

_ASK_USER_TOOL = {
    "name": "ask_user",
    "description": (
        "Ask the user a clarifying question and wait for their answer. "
        "Use this when you genuinely need more information to proceed correctly. "
        "Do NOT use it for yes/no confirmations — only for open questions where "
        "the answer meaningfully changes your implementation."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question to ask the user. Be specific and concise.",
            }
        },
        "required": ["question"],
    },
}


# ---------------------------------------------------------------------------
# Agent result
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Base agent
# ---------------------------------------------------------------------------

class BaseAgent(ABC):
    name: str = "base"
    display_name: str | None = None
    model: str = SONNET_MODEL
    system_prompt: str = ""
    tools: list[dict[str, Any]] = []
    max_tokens: int = 8096

    def __init__(self) -> None:
        self._ask_user_fn: Any = None
        self._current_task: Task | None = None

    @property
    def label(self) -> str:
        return self.display_name or self.name

    @property
    def _local_mode(self) -> bool:
        return config.local_mode

    # ------------------------------------------------------------------
    # System prompt builder (API mode)
    # ------------------------------------------------------------------

    def _build_system(self) -> list[dict[str, Any]]:
        return [
            {
                "type": "text",
                "text": self.system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    # ------------------------------------------------------------------
    # Abstract interface
    # ------------------------------------------------------------------

    @abstractmethod
    async def build_user_message(self, task: Task) -> str:
        """Build the user message for this agent given the task context."""

    # ------------------------------------------------------------------
    # Claude call — API or local
    # ------------------------------------------------------------------

    async def _call_claude(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> Any:
        if self._local_mode:
            return await self._call_claude_local(messages)
        return await self._call_claude_api(messages, tools)

    async def _call_claude_api(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> anthropic.types.Message:
        if not _api_client:
            raise RuntimeError("ANTHROPIC_API_KEY not configured.")
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "system": self._build_system(),
            "messages": messages,
        }
        if tools:
            kwargs["tools"] = tools
        return await _api_client.messages.create(**kwargs)

    async def _call_claude_local(self, messages: list[dict[str, Any]]) -> _LocalMessage:
        """Call the claude CLI (uses Pro subscription — no API credits)."""
        bin_path = _get_claude_bin()

        # Flatten the conversation into a single user prompt for the CLI
        parts = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if isinstance(content, str):
                parts.append(f"[{role.upper()}]\n{content}")
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            parts.append(f"[{role.upper()}]\n{block['text']}")
                        elif block.get("type") == "tool_result":
                            parts.append(f"[TOOL RESULT]\n{block.get('content', '')}")
        prompt = "\n\n".join(parts)

        # Pass prompt via stdin to avoid Windows command-line length limits
        cmd = [
            bin_path,
            "-p",
            "--system-prompt", self.system_prompt,
            "--model", "sonnet",
            "--output-format", "text",
        ]

        logger.debug("[%s] Calling claude CLI (local mode)", self.label)
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate(input=prompt.encode("utf-8"))

        if proc.returncode != 0:
            err = stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"[{self.label}] claude CLI failed (exit {proc.returncode}): {err}")

        text = stdout.decode("utf-8", errors="replace").strip()
        return _LocalMessage(content=[_LocalTextBlock(text=text)], stop_reason="end_turn")

    # ------------------------------------------------------------------
    # User interaction
    # ------------------------------------------------------------------

    async def _handle_ask_user(self, question: str) -> str:
        if self._ask_user_fn is not None:
            import inspect
            if inspect.iscoroutinefunction(self._ask_user_fn):
                return await self._ask_user_fn(self.label, question)
            return self._ask_user_fn(self.label, question)

        print(f"\n{'='*60}")
        print(f"[{self.label}] needs your input:")
        print(f"  {question}")
        try:
            answer = input("Your answer: ").strip()
        except EOFError:
            answer = ""
            print("(no terminal — continuing without answer)")
        print(f"{'='*60}\n")
        if self._current_task:
            self._current_task.add_history(
                agent=self.label,
                action="asked_user",
                detail=f"Q: {question[:80]} | A: {answer[:80]}",
            )
        return answer

    # ------------------------------------------------------------------
    # Tool use loop (API mode only — local mode never uses tools)
    # ------------------------------------------------------------------

    async def _handle_tool_use(
        self,
        message: Any,
        messages: list[dict[str, Any]],
    ) -> Any:
        tool_results = []
        for block in message.content:
            if block.type == "tool_use":
                try:
                    if block.name == "ask_user":
                        result = await self._handle_ask_user(block.input["question"])
                    else:
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
        interactive = os.environ.get("MONARCH_INTERACTIVE", "0") == "1" or self._ask_user_fn is not None
        extra = [_ASK_USER_TOOL] if interactive else []
        all_tools = (self.tools or []) + extra
        return await self._call_claude_api(messages, all_tools or None)

    async def execute_tool(self, name: str, inputs: dict[str, Any]) -> Any:
        raise NotImplementedError(f"Tool not implemented: {name}")

    # ------------------------------------------------------------------
    # JSON extraction
    # ------------------------------------------------------------------

    def _extract_json(self, text: str) -> dict[str, Any]:
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            text = "\n".join(lines[1:-1])
        candidates = [text]

        json_fence_matches = re.findall(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        candidates.extend(json_fence_matches)

        first_brace = text.find("{")
        last_brace = text.rfind("}")
        if first_brace != -1 and last_brace != -1 and first_brace < last_brace:
            candidates.append(text[first_brace:last_brace + 1])

        for candidate in candidates:
            candidate = candidate.strip()
            if not candidate:
                continue
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                continue

        raise json.JSONDecodeError("Could not extract valid JSON object", text, 0)

    # ------------------------------------------------------------------
    # Main run
    # ------------------------------------------------------------------

    async def run(self, task: Task) -> AgentResult:
        self._current_task = task
        user_content = await self.build_user_message(task)
        messages: list[dict[str, Any]] = [{"role": "user", "content": user_content}]

        logger.info(f"[{self.label}] Starting for task {task.task_id} (local={self._local_mode})")

        if self._local_mode:
            # Local mode: single call via claude CLI, no tool loops
            message = await self._call_claude_local(messages)
        else:
            # API mode: full tool_use loop
            interactive = os.environ.get("MONARCH_INTERACTIVE", "0") == "1" or self._ask_user_fn is not None
            extra = [_ASK_USER_TOOL] if interactive else []
            all_tools = (self.tools or []) + extra
            message = await self._call_claude_api(messages, all_tools or None)

            while message.stop_reason == "tool_use":
                message = await self._handle_tool_use(message, messages)

        if not message.content:
            raise ValueError(f"[{self.name}] Got empty response from Claude")

        text_blocks = [b for b in message.content if b.type == "text"]
        if not text_blocks:
            raise ValueError(f"[{self.name}] No text block in response")

        raw = self._extract_json("\n".join(block.text for block in text_blocks))
        result = AgentResult.from_dict(raw)
        logger.info(f"[{self.label}] Done. Confidence: {result.confidence:.2f}")
        return result
