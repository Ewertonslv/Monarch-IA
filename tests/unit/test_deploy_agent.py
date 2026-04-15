import json
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from core.task import Task
from agents.base import SONNET_MODEL


def _msg(payload: dict) -> MagicMock:
    m = MagicMock()
    m.stop_reason = "end_turn"
    m.content = [MagicMock(type="text", text=json.dumps(payload))]
    return m


_FASTAPI_PAYLOAD = {
    "confidence": 0.92,
    "project_type": "fastapi_api",
    "deployment_target": "railway",
    "ci_workflow_path": ".github/workflows/ci.yml",
    "files_written": [".github/workflows/ci.yml"],
    "env_vars_needed": ["DATABASE_URL", "SECRET_KEY"],
    "deploy_commands": ["railway up"],
    "concerns": [],
}


@pytest.mark.asyncio
async def test_deploy_agent_sets_deploy_report():
    from agents.deploy import DeployAgent
    with patch("agents.deploy.GitHubTools") as MockGH:
        MockGH.return_value.list_files.return_value = ["main.py", "requirements.txt"]
        MockGH.return_value.write_file = MagicMock()
        agent = DeployAgent()

    task = Task(raw_input="create login endpoint")
    task.architecture = {"approach": "REST", "new_files": ["src/auth.py"]}
    task.branch_name = "feat/login"

    with patch.object(agent, "_call_claude", return_value=_msg(_FASTAPI_PAYLOAD)):
        result = await agent.run(task)

    assert task.deploy_report is not None
    assert task.deploy_report["project_type"] == "fastapi_api"
    assert any(e.agent == "deploy" for e in task.history)


@pytest.mark.asyncio
async def test_deploy_agent_writes_ci_workflow():
    from agents.deploy import DeployAgent
    with patch("agents.deploy.GitHubTools") as MockGH:
        mock_gh_instance = MockGH.return_value
        mock_gh_instance.list_files.return_value = ["main.py", "pyproject.toml"]
        mock_gh_instance.write_file = MagicMock()
        agent = DeployAgent()

    task = Task(raw_input="add search feature")
    task.branch_name = "feat/search"
    task.architecture = {}

    with patch.object(agent, "_call_claude", return_value=_msg(_FASTAPI_PAYLOAD)):
        await agent.run(task)

    # Should have written the CI workflow to the branch
    mock_gh_instance.write_file.assert_called_once()
    call_kwargs = mock_gh_instance.write_file.call_args
    written_path = call_kwargs[0][0] if call_kwargs[0] else call_kwargs[1].get("path", "")
    assert ".github/workflows" in written_path


@pytest.mark.asyncio
async def test_deploy_agent_user_message_has_context():
    from agents.deploy import DeployAgent
    with patch("agents.deploy.GitHubTools") as MockGH:
        MockGH.return_value.list_files.return_value = ["main.py"]
        agent = DeployAgent()

    task = Task(raw_input="add payment processing")
    task.architecture = {"approach": "service layer", "new_files": ["src/payments.py"]}
    task.branch_name = "feat/payments"

    msg = await agent.build_user_message(task)
    assert "payment processing" in msg
    assert "feat/payments" in msg


@pytest.mark.asyncio
async def test_deploy_agent_handles_missing_branch():
    from agents.deploy import DeployAgent
    with patch("agents.deploy.GitHubTools") as MockGH:
        MockGH.return_value.list_files.return_value = []
        MockGH.return_value.write_file = MagicMock()
        agent = DeployAgent()

    task = Task(raw_input="refactor module")
    task.branch_name = None  # no branch — should still run without crashing
    task.architecture = {}

    payload = {**_FASTAPI_PAYLOAD, "files_written": []}
    with patch.object(agent, "_call_claude", return_value=_msg(payload)):
        result = await agent.run(task)

    assert result.confidence > 0


def test_deploy_agent_uses_sonnet():
    from agents.deploy import DeployAgent
    with patch("agents.deploy.GitHubTools"):
        assert DeployAgent().model == SONNET_MODEL
