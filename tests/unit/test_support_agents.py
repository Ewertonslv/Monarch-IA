import json
import pytest
from unittest.mock import MagicMock, patch
from core.task import Task
from agents.documentation import DocumentationAgent
from agents.observability import ObservabilityAgent
from agents.base import HAIKU_MODEL


def _msg(payload: dict) -> MagicMock:
    m = MagicMock()
    m.stop_reason = "end_turn"
    m.content = [MagicMock(type="text", text=json.dumps(payload))]
    return m


# -----------------------------------------------------------------------
# Documentation
# -----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_documentation_returns_changelog():
    with patch("agents.documentation.GitHubTools"):
        agent = DocumentationAgent()
    task = Task(raw_input="add rate limiting to API")
    task.architecture = {"approach": "middleware"}
    task.review_report = {"approved": True}
    task.pr_url = None

    payload = {
        "confidence": 0.92,
        "changelog_entry": "## [1.1.0] - 2026-04-14\n### Added\n- Rate limiting middleware",
        "readme_sections": [{"heading": "Rate Limiting", "content": "..."}],
        "api_docs": [],
        "inline_docs": [],
        "concerns": [],
    }
    with patch.object(agent, "_call_claude", return_value=_msg(payload)):
        result = await agent.run(task)

    assert "changelog_entry" in result.output
    assert "Rate limiting" in result.output["changelog_entry"]
    assert any(e.agent == "documentation" for e in task.history)


@pytest.mark.asyncio
async def test_documentation_user_message_has_task(tmp_path):
    with patch("agents.documentation.GitHubTools"):
        agent = DocumentationAgent()
    task = Task(raw_input="implement OAuth2 login")
    task.architecture = {}
    msg = await agent.build_user_message(task)
    assert "OAuth2 login" in msg


def test_documentation_uses_haiku():
    with patch("agents.documentation.GitHubTools"):
        assert DocumentationAgent().model == HAIKU_MODEL


# -----------------------------------------------------------------------
# Observability
# -----------------------------------------------------------------------

@pytest.mark.asyncio
async def test_observability_returns_metrics():
    agent = ObservabilityAgent()
    task = Task(raw_input="add payment processing")
    task.architecture = {"approach": "service layer"}
    task.requirements = {"feature_type": "backend_api", "affected_areas": ["payments"]}

    payload = {
        "confidence": 0.88,
        "logging_recommendations": ["Log payment attempt", "Log payment result"],
        "metrics_to_add": [
            {"name": "payment_requests_total", "type": "counter", "description": "Total payment requests"},
            {"name": "payment_duration_seconds", "type": "histogram", "description": "Payment latency"},
        ],
        "alerts_to_configure": [
            {"name": "high_payment_failure_rate", "condition": "failure_rate > 0.05", "severity": "critical"}
        ],
        "tracing_spans": ["payment.process", "payment.validate"],
        "health_check_suggestions": ["Check payment gateway connectivity"],
        "concerns": [],
    }
    with patch.object(agent, "_call_claude", return_value=_msg(payload)):
        result = await agent.run(task)

    assert len(result.output["metrics_to_add"]) == 2
    assert len(result.output["alerts_to_configure"]) == 1
    assert any(e.agent == "observability" for e in task.history)


@pytest.mark.asyncio
async def test_observability_user_message_has_task():
    agent = ObservabilityAgent()
    task = Task(raw_input="add email notifications")
    task.architecture = {}
    task.requirements = {"feature_type": "backend_api", "affected_areas": ["notifications"]}
    msg = await agent.build_user_message(task)
    assert "email notifications" in msg
    assert "notifications" in msg


def test_observability_uses_haiku():
    assert ObservabilityAgent().model == HAIKU_MODEL
