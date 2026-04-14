import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agents.base import BaseAgent, AgentResult
from core.task import Task


class ConcreteAgent(BaseAgent):
    name = "test_agent"
    system_prompt = "You are a test agent."

    async def build_user_message(self, task: Task) -> str:
        return f"Process: {task.raw_input}"


@pytest.mark.asyncio
async def test_agent_returns_result_on_text_response():
    agent = ConcreteAgent()
    task = Task(raw_input="create login endpoint")

    mock_message = MagicMock()
    mock_message.stop_reason = "end_turn"
    mock_message.content = [MagicMock(type="text", text='{"output": "done", "confidence": 0.9}')]

    with patch.object(agent, "_call_claude", return_value=mock_message):
        result = await agent.run(task)

    assert isinstance(result, AgentResult)
    assert result.confidence == 0.9


@pytest.mark.asyncio
async def test_agent_raises_on_empty_response():
    agent = ConcreteAgent()
    task = Task(raw_input="test")

    mock_message = MagicMock()
    mock_message.stop_reason = "end_turn"
    mock_message.content = []

    with patch.object(agent, "_call_claude", return_value=mock_message):
        with pytest.raises(ValueError, match="empty response"):
            await agent.run(task)


@pytest.mark.asyncio
async def test_agent_extracts_json_from_markdown():
    agent = ConcreteAgent()
    task = Task(raw_input="test")

    mock_message = MagicMock()
    mock_message.stop_reason = "end_turn"
    mock_message.content = [
        MagicMock(type="text", text='```json\n{"result": "ok", "confidence": 0.8}\n```')
    ]

    with patch.object(agent, "_call_claude", return_value=mock_message):
        result = await agent.run(task)

    assert result.confidence == 0.8
    assert result.output["result"] == "ok"


@pytest.mark.asyncio
async def test_agent_loops_on_tool_use():
    agent = ConcreteAgent()
    task = Task(raw_input="test")

    tool_msg = MagicMock()
    tool_msg.stop_reason = "tool_use"
    tool_block = MagicMock()
    tool_block.type = "tool_use"
    tool_block.id = "tu_1"
    tool_block.name = "read_file"
    tool_block.input = {"path": "test.py"}
    tool_msg.content = [tool_block]

    final_msg = MagicMock()
    final_msg.stop_reason = "end_turn"
    final_msg.content = [MagicMock(type="text", text='{"done": true, "confidence": 1.0}')]

    agent.execute_tool = AsyncMock(return_value="file content")

    with patch.object(agent, "_call_claude", side_effect=[tool_msg, final_msg]):
        result = await agent.run(task)

    assert result.output["done"] is True
    agent.execute_tool.assert_called_once_with("read_file", {"path": "test.py"})
