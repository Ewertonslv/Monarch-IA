"""
Integration test: full orchestrator pipeline with all agents mocked at the
Claude API level (no real HTTP calls). Verifies that all 11 agents fire in order,
task state is persisted, and the final status is DONE.
"""
import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

import anthropic

from core.task import Task, TaskStatus
from core.orchestrator import Orchestrator
from storage.database import Database
from agents.base import AgentResult


def _claude_msg(payload: dict) -> anthropic.types.Message:
    """Build a fake Anthropic Message that passes through BaseAgent.run()."""
    block = MagicMock()
    block.type = "text"
    block.text = json.dumps(payload)
    msg = MagicMock(spec=anthropic.types.Message)
    msg.stop_reason = "end_turn"
    msg.content = [block]
    return msg


# Minimal valid payloads for each agent
_DISCOVERY = {"confidence": 0.9, "summary": "Add search", "feature_type": "backend_api", "complexity": "medium", "affected_areas": ["search"], "acceptance_criteria": ["returns results"], "out_of_scope": [], "concerns": []}
_PRIORITIZATION = {"confidence": 0.85, "priority": "high", "priority_score": 80, "rationale": "...", "suggested_sprint": "current", "dependencies": [], "risks": [], "concerns": []}
_ARCHITECTURE = {"confidence": 0.88, "approach": "REST", "new_files": ["src/search.py"], "modified_files": [], "deleted_files": [], "database_changes": [], "api_endpoints": [], "test_strategy": "unit", "patterns": [], "concerns": []}
_PLANNING = {"confidence": 0.90, "steps": [{"id": 1, "title": "write test", "description": "", "type": "write_test", "files": [], "dependencies": [], "acceptance": ""}], "branch_name": "feat/search", "estimated_steps": 1, "concerns": []}
_DEVILS = {"confidence": 0.95, "approved": True, "issues": [], "must_fix_before_implementation": [], "nice_to_have": [], "concerns": []}
_IMPLEMENTER = {"confidence": 0.92, "files_written": [{"path": "src/search.py", "description": "search"}], "summary": "done", "next_step_hint": "", "concerns": []}
_TESTING = {"confidence": 0.99, "all_passed": True, "pytest": {"passed": True, "summary": "1 passed"}, "ruff": {"passed": True, "issue_count": 0}, "mypy": {"passed": True, "summary": "clean"}, "bandit": {"passed": True, "high_severity": 0}, "blocking_issues": [], "recommendations": [], "concerns": []}
_REVIEWER = {"confidence": 0.88, "approved": True, "overall_quality": "good", "comments": [], "blocking_issues": [], "positive_highlights": [], "concerns": []}
_SECURITY = {"confidence": 0.90, "approved": True, "risk_level": "low", "vulnerabilities": [], "blocking_vulnerabilities": [], "security_positives": [], "concerns": []}
_DOCUMENTATION = {"confidence": 0.85, "changelog_entry": "## Added\n- search", "readme_sections": [], "api_docs": [], "inline_docs": [], "concerns": []}
_OBSERVABILITY = {"confidence": 0.80, "logging_recommendations": [], "metrics_to_add": [], "alerts_to_configure": [], "tracing_spans": [], "health_check_suggestions": [], "concerns": []}

_AGENT_RESPONSES = [
    _DISCOVERY, _PRIORITIZATION, _ARCHITECTURE, _PLANNING, _DEVILS,
    _IMPLEMENTER, _TESTING, _REVIEWER, _SECURITY, _DOCUMENTATION, _OBSERVABILITY,
]


@pytest.fixture
async def db(tmp_path):
    url = f"sqlite+aiosqlite:///{tmp_path}/test.db"
    database = Database(url)
    await database.init()
    yield database
    await database.close()


@pytest.mark.asyncio
async def test_full_pipeline_reaches_done(db):
    orch = Orchestrator(db)
    # Auto-approve both gates
    orch._request_approval = AsyncMock(return_value=True)

    response_iter = iter(_AGENT_RESPONSES)

    def next_msg(*args, **kwargs):
        return _claude_msg(next(response_iter))

    with (
        patch("agents.base._client") as mock_client,
        patch("core.orchestrator.GitHubTools") as MockGHOrch,
        patch("agents.implementer.GitHubTools") as MockGH,
        patch("agents.reviewer.GitHubTools"),
        patch("agents.documentation.GitHubTools"),
        patch("agents.testing.CodeTools") as MockCT,
    ):
        mock_client.messages.create = AsyncMock(side_effect=next_msg)
        for gh_mock in [MockGHOrch, MockGH]:
            gh_mock.return_value.as_tools_schema.return_value = []
            gh_mock.return_value.create_branch = MagicMock()
            gh_mock.return_value.create_pr = MagicMock(return_value="https://github.com/o/r/pull/1")
        MockCT.return_value.run_all_checks.return_value = {
            "overall_passed": True, "pytest": {"passed": True, "output": ""}, "ruff": {"passed": True, "issues": []}, "mypy": {"passed": True, "output": ""}, "bandit": {"passed": True, "high_severity": 0, "output": ""},
        }

        task = Task(raw_input="Add search feature")
        result = await orch.run(task)

    assert result.status == TaskStatus.DONE
    agent_names = {h.agent for h in result.history}
    assert "discovery" in agent_names
    assert "planning" in agent_names
    assert "implementer" in agent_names
    assert "security" in agent_names
    assert "documentation" in agent_names


@pytest.mark.asyncio
async def test_pipeline_persists_task_to_db(db):
    orch = Orchestrator(db)
    orch._request_approval = AsyncMock(return_value=True)

    response_iter = iter(_AGENT_RESPONSES)

    def next_msg(*args, **kwargs):
        return _claude_msg(next(response_iter))

    with (
        patch("agents.base._client") as mock_client,
        patch("core.orchestrator.GitHubTools") as MockGHOrch,
        patch("agents.implementer.GitHubTools") as MockGH,
        patch("agents.reviewer.GitHubTools"),
        patch("agents.documentation.GitHubTools"),
        patch("agents.testing.CodeTools") as MockCT,
    ):
        mock_client.messages.create = AsyncMock(side_effect=next_msg)
        for gh_mock in [MockGHOrch, MockGH]:
            gh_mock.return_value.as_tools_schema.return_value = []
            gh_mock.return_value.create_branch = MagicMock()
            gh_mock.return_value.create_pr = MagicMock(return_value="https://github.com/o/r/pull/2")
        MockCT.return_value.run_all_checks.return_value = {
            "overall_passed": True, "pytest": {"passed": True, "output": ""}, "ruff": {"passed": True, "issues": []}, "mypy": {"passed": True, "output": ""}, "bandit": {"passed": True, "high_severity": 0, "output": ""},
        }

        task = Task(raw_input="Persist me to DB")
        result = await orch.run(task)

    loaded = await db.get_task(result.task_id)
    assert loaded is not None
    assert loaded.status == TaskStatus.DONE
    assert loaded.raw_input == "Persist me to DB"
