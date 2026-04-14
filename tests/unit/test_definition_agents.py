import pytest
from unittest.mock import MagicMock, patch
from core.task import Task
from agents.prioritization import PrioritizationAgent
from agents.architecture import ArchitectureAgent
from agents.planning import PlanningAgent
from agents.devils_advocate import DevilsAdvocateAgent
from agents.base import OPUS_MODEL, SONNET_MODEL


def _mock_message(json_text: str) -> MagicMock:
    msg = MagicMock()
    msg.stop_reason = "end_turn"
    msg.content = [MagicMock(type="text", text=json_text)]
    return msg


# -----------------------------------------------------------------------
# Prioritization
# -----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_prioritization_sets_task_priority():
    agent = PrioritizationAgent()
    task = Task(raw_input="add caching to /search")
    task.requirements = {"complexity": "low"}

    msg = _mock_message('{"confidence": 0.88, "priority": "high", "priority_score": 78, "rationale": "...", "suggested_sprint": "next", "dependencies": [], "risks": [], "concerns": []}')
    with patch.object(agent, "_call_claude", return_value=msg):
        result = await agent.run(task)

    assert task.priority == "high"
    assert result.output["priority_score"] == 78


def test_prioritization_uses_sonnet():
    assert PrioritizationAgent().model == SONNET_MODEL


# -----------------------------------------------------------------------
# Architecture
# -----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_architecture_sets_task_architecture():
    agent = ArchitectureAgent()
    task = Task(raw_input="create user profile endpoint")
    task.requirements = {}

    msg = _mock_message('{"confidence": 0.90, "approach": "REST endpoint", "new_files": ["src/api/profile.py"], "modified_files": [], "deleted_files": [], "database_changes": [], "api_endpoints": [], "test_strategy": "unit", "patterns": ["repository"], "concerns": []}')
    with patch.object(agent, "_call_claude", return_value=msg):
        result = await agent.run(task)

    assert task.architecture is not None
    assert "src/api/profile.py" in task.architecture["new_files"]


def test_architecture_uses_opus():
    assert ArchitectureAgent().model == OPUS_MODEL


# -----------------------------------------------------------------------
# Planning
# -----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_planning_sets_task_plan_and_branch():
    agent = PlanningAgent()
    task = Task(raw_input="add search feature")
    task.requirements = {}
    task.architecture = {}

    steps = [
        {"id": 1, "title": "Write test", "description": "...", "type": "write_test", "files": ["tests/test_search.py"], "dependencies": [], "acceptance": "test fails"},
        {"id": 2, "title": "Implement", "description": "...", "type": "write_code", "files": ["src/search.py"], "dependencies": [1], "acceptance": "test passes"},
    ]
    msg = _mock_message(f'{{"confidence": 0.95, "steps": {__import__("json").dumps(steps)}, "branch_name": "feat/search", "estimated_steps": 2, "concerns": []}}')
    with patch.object(agent, "_call_claude", return_value=msg):
        result = await agent.run(task)

    assert len(task.plan) == 2
    assert task.branch_name == "feat/search"


def test_planning_uses_opus():
    assert PlanningAgent().model == OPUS_MODEL


# -----------------------------------------------------------------------
# Devil's Advocate
# -----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_devils_advocate_approved_appends_round():
    agent = DevilsAdvocateAgent()
    task = Task(raw_input="refactor auth module")
    task.requirements = {}
    task.architecture = {}
    task.plan = []

    msg = _mock_message('{"confidence": 0.80, "approved": true, "issues": [], "must_fix_before_implementation": [], "nice_to_have": [], "concerns": []}')
    with patch.object(agent, "_call_claude", return_value=msg):
        result = await agent.run(task)

    assert len(task.devils_advocate_rounds) == 1
    assert task.devils_advocate_rounds[0]["approved"] is True


@pytest.mark.asyncio
async def test_devils_advocate_records_issues():
    agent = DevilsAdvocateAgent()
    task = Task(raw_input="delete all users endpoint")
    task.requirements = {}
    task.architecture = {}
    task.plan = []

    issues = [{"severity": "critical", "category": "security", "description": "No auth", "suggestion": "Add JWT check"}]
    msg = _mock_message(f'{{"confidence": 0.30, "approved": false, "issues": {__import__("json").dumps(issues)}, "must_fix_before_implementation": ["Add authentication"], "nice_to_have": [], "concerns": []}}')
    with patch.object(agent, "_call_claude", return_value=msg):
        result = await agent.run(task)

    assert result.output["approved"] is False
    assert len(result.output["issues"]) == 1
    assert result.output["issues"][0]["severity"] == "critical"


def test_devils_advocate_uses_opus():
    assert DevilsAdvocateAgent().model == OPUS_MODEL
