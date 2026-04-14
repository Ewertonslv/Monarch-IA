import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from agents.discovery import DiscoveryAgent
from agents.base import AgentResult
from core.task import Task


@pytest.fixture
def agent():
    return DiscoveryAgent()


@pytest.mark.asyncio
async def test_discovery_returns_result(agent):
    task = Task(raw_input="Create a login endpoint with JWT auth")

    response_json = {
        "confidence": 0.92,
        "summary": "Build JWT login endpoint",
        "feature_type": "backend_api",
        "complexity": "medium",
        "affected_areas": ["auth", "users"],
        "acceptance_criteria": ["returns 200 on valid creds", "returns 401 on invalid"],
        "out_of_scope": [],
        "concerns": [],
    }

    mock_message = MagicMock()
    mock_message.stop_reason = "end_turn"
    mock_message.content = [
        MagicMock(type="text", text=f'{{"confidence": 0.92, "summary": "Build JWT login endpoint", "feature_type": "backend_api", "complexity": "medium", "affected_areas": ["auth", "users"], "acceptance_criteria": ["returns 200 on valid creds", "returns 401 on invalid"], "out_of_scope": [], "concerns": []}}')
    ]

    with patch.object(agent, "_call_claude", return_value=mock_message):
        result = await agent.run(task)

    assert isinstance(result, AgentResult)
    assert result.confidence == 0.92
    assert result.output["feature_type"] == "backend_api"
    assert result.output["complexity"] == "medium"


@pytest.mark.asyncio
async def test_discovery_populates_task(agent):
    task = Task(raw_input="Add pagination to /products endpoint")

    mock_message = MagicMock()
    mock_message.stop_reason = "end_turn"
    mock_message.content = [
        MagicMock(type="text", text='{"confidence": 0.85, "summary": "Paginate products", "feature_type": "enhancement", "complexity": "low", "affected_areas": ["products"], "acceptance_criteria": [], "out_of_scope": [], "concerns": []}')
    ]

    with patch.object(agent, "_call_claude", return_value=mock_message):
        result = await agent.run(task)

    # After running discovery, requirements should be set on the task
    assert task.requirements is not None
    assert task.requirements["summary"] == "Paginate products"


@pytest.mark.asyncio
async def test_discovery_user_message_contains_input(agent):
    task = Task(raw_input="migrate database to PostgreSQL")
    msg = await agent.build_user_message(task)
    assert "migrate database to PostgreSQL" in msg


def test_discovery_uses_opus_model(agent):
    from agents.base import OPUS_MODEL
    assert agent.model == OPUS_MODEL
