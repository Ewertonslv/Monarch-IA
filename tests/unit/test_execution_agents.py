import json
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.task import Task
from agents.implementer import ImplementerAgent
from agents.testing import TestingAgent
from agents.reviewer import ReviewerAgent
from agents.security import SecurityAgent
from agents.base import OPUS_MODEL, SONNET_MODEL


def _msg(payload: dict) -> MagicMock:
    m = MagicMock()
    m.stop_reason = "end_turn"
    m.content = [MagicMock(type="text", text=json.dumps(payload))]
    return m


# -----------------------------------------------------------------------
# Implementer
# -----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_implementer_records_files_written():
    with patch("agents.implementer.GitHubTools"):
        agent = ImplementerAgent()
    task = Task(raw_input="add health check endpoint")
    task.plan = [{"id": 1, "title": "write test", "type": "write_test", "files": [], "dependencies": [], "description": "", "acceptance": ""}]
    task.architecture = {}
    task.branch_name = "feat/health"

    payload = {
        "confidence": 0.95,
        "files_written": [{"path": "src/health.py", "description": "health endpoint"}],
        "summary": "Added /health endpoint",
        "next_step_hint": "run tests",
        "concerns": [],
    }
    with patch.object(agent, "_call_claude", return_value=_msg(payload)):
        result = await agent.run(task)

    assert len(result.output["files_written"]) == 1
    assert any(e.agent == "implementer" for e in task.history)


def test_implementer_uses_opus():
    with patch("agents.implementer.GitHubTools"):
        assert ImplementerAgent().model == OPUS_MODEL


# -----------------------------------------------------------------------
# Testing
# -----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_testing_agent_sets_test_results():
    good_checks = {
        "overall_passed": True,
        "pytest": {"passed": True, "output": "3 passed"},
        "ruff": {"passed": True, "issues": []},
        "mypy": {"passed": True, "output": "Success"},
        "bandit": {"passed": True, "high_severity": 0, "output": ""},
    }
    payload = {
        "confidence": 0.99,
        "all_passed": True,
        "pytest": {"passed": True, "summary": "3 passed"},
        "ruff": {"passed": True, "issue_count": 0},
        "mypy": {"passed": True, "summary": "clean"},
        "bandit": {"passed": True, "high_severity": 0},
        "blocking_issues": [],
        "recommendations": [],
        "concerns": [],
    }
    with patch("agents.testing.CodeTools") as MockCT:
        MockCT.return_value.run_all_checks.return_value = good_checks
        agent = TestingAgent(workdir="/tmp")

    task = Task(raw_input="add caching")
    with patch.object(agent, "_call_claude", return_value=_msg(payload)):
        result = await agent.run(task)

    assert task.test_results is not None
    assert task.test_results["all_passed"] is True


def test_testing_uses_sonnet():
    with patch("agents.testing.CodeTools"):
        assert TestingAgent().model == SONNET_MODEL


# -----------------------------------------------------------------------
# Reviewer
# -----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_reviewer_sets_review_report():
    with patch("agents.reviewer.GitHubTools"):
        agent = ReviewerAgent()
    task = Task(raw_input="refactor DB layer")
    task.pr_url = None

    payload = {
        "confidence": 0.88,
        "approved": True,
        "overall_quality": "good",
        "comments": [],
        "blocking_issues": [],
        "positive_highlights": ["clean separation of concerns"],
        "concerns": [],
    }
    with patch.object(agent, "_call_claude", return_value=_msg(payload)):
        result = await agent.run(task)

    assert task.review_report is not None
    assert task.review_report["approved"] is True


def test_reviewer_uses_opus():
    with patch("agents.reviewer.GitHubTools"):
        assert ReviewerAgent().model == OPUS_MODEL


# -----------------------------------------------------------------------
# Security
# -----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_security_agent_sets_security_report():
    agent = SecurityAgent()
    task = Task(raw_input="add user login")
    task.review_report = {"approved": True}
    task.test_results = {"all_passed": True}

    payload = {
        "confidence": 0.90,
        "approved": True,
        "risk_level": "low",
        "vulnerabilities": [],
        "blocking_vulnerabilities": [],
        "security_positives": ["passwords hashed with bcrypt"],
        "concerns": [],
    }
    with patch.object(agent, "_call_claude", return_value=_msg(payload)):
        result = await agent.run(task)

    assert task.security_report is not None
    assert task.security_report["risk_level"] == "low"


@pytest.mark.asyncio
async def test_security_agent_flags_blocking_vuln():
    agent = SecurityAgent()
    task = Task(raw_input="build SQL query from user input")
    task.review_report = {}
    task.test_results = {}

    vulns = [{"cwe": "CWE-89", "severity": "critical", "location": "src/query.py:12", "description": "SQL injection", "remediation": "Use parameterized queries"}]
    payload = {
        "confidence": 0.99,
        "approved": False,
        "risk_level": "critical",
        "vulnerabilities": vulns,
        "blocking_vulnerabilities": ["CWE-89 SQL Injection in src/query.py:12"],
        "security_positives": [],
        "concerns": [],
    }
    with patch.object(agent, "_call_claude", return_value=_msg(payload)):
        result = await agent.run(task)

    assert result.output["approved"] is False
    assert result.output["risk_level"] == "critical"


def test_security_uses_opus():
    assert SecurityAgent().model == OPUS_MODEL
