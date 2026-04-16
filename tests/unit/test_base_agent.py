import pytest

from agents.base import BaseAgent
from core.task import Task


class _DummyAgent(BaseAgent):
    async def build_user_message(self, task: Task) -> str:
        return task.raw_input


def test_extract_json_accepts_markdown_fence():
    agent = _DummyAgent()
    text = """```json
{"confidence": 0.9, "concerns": [], "value": "ok"}
```"""
    result = agent._extract_json(text)
    assert result["value"] == "ok"


def test_extract_json_recovers_from_surrounding_text():
    agent = _DummyAgent()
    text = 'Segue a resposta final:\n{"confidence": 0.8, "concerns": [], "value": "ok"}\nObrigado.'
    result = agent._extract_json(text)
    assert result["confidence"] == 0.8


def test_extract_json_raises_when_no_object_found():
    agent = _DummyAgent()
    with pytest.raises(Exception):
        agent._extract_json("sem json aqui")
