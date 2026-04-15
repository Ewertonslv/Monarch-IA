import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from agents.base import AgentResult
from core.orchestrator import Orchestrator
from core.task import Task, TaskStatus


def _result(output: dict | None = None, confidence: float = 0.9) -> AgentResult:
    out = output or {}
    out.setdefault("confidence", confidence)
    return AgentResult(output=out, confidence=confidence, concerns=[])


@pytest.fixture
async def db():
    from storage.database import Database

    database = Database("sqlite+aiosqlite:///:memory:")
    await database.init()
    yield database
    await database.close()


@pytest.mark.asyncio
async def test_orchestrator_syncs_task_lifecycle_to_monarch_core(db):
    orch = Orchestrator(db)
    orch._core_client._base_url = "http://monarch-core:8010"  # type: ignore[attr-defined]
    orch._core_client.ensure_project = AsyncMock(
        return_value={"id": "project-1", "business_unit_id": "bu-1"}
    )
    orch._core_client.create_idea = AsyncMock(return_value={"id": "idea-1"})
    orch._core_client.create_task = AsyncMock(return_value={"id": "task-1"})
    orch._core_client.create_execution = AsyncMock(return_value={"id": "execution-1"})
    orch._core_client.update_task = AsyncMock()
    orch._core_client.update_execution = AsyncMock()
    orch._core_client.create_approval = AsyncMock(return_value={"id": "approval-1"})
    orch._core_client.decide_approval = AsyncMock()

    with (
        patch("core.orchestrator.DiscoveryAgent") as DA,
        patch("core.orchestrator.PrioritizationAgent") as PA,
        patch("core.orchestrator.ArchitectureAgent") as AA,
        patch("core.orchestrator.PlanningAgent") as PLA,
        patch("core.orchestrator.DevilsAdvocateAgent") as DVA,
        patch("core.orchestrator.ImplementerAgent") as IA,
        patch("core.orchestrator.TestingAgent") as TA,
        patch("core.orchestrator.ReviewerAgent") as RA,
        patch("core.orchestrator.SecurityAgent") as SA,
        patch("core.orchestrator.DeployAgent") as DEPLOY,
        patch("core.orchestrator.DocumentationAgent") as DOC,
        patch("core.orchestrator.ObservabilityAgent") as OBS,
        patch("core.orchestrator.GitHubTools") as GH,
        patch.object(orch, "_request_approval", new=AsyncMock(return_value=True)),
    ):
        for AgentCls in [DA, PA, AA, PLA, IA, TA, RA, DEPLOY, DOC, OBS]:
            AgentCls.return_value.run = AsyncMock(return_value=_result())
        DVA.return_value.run = AsyncMock(return_value=_result({"approved": True}))
        RA.return_value.run = AsyncMock(return_value=_result({"approved": True}))
        SA.return_value.run = AsyncMock(return_value=_result({"approved": True}))
        GH.return_value.create_branch = MagicMock()
        GH.return_value.create_pr = MagicMock(return_value="https://github.com/owner/repo/pull/1")

        task = Task(raw_input="criar central operacional")
        task.requirements = {
            "summary": "Central operacional",
            "complexity": "medium",
            "affected_areas": [],
            "acceptance_criteria": [],
        }
        result = await orch.run(task)

    assert result.status == TaskStatus.DONE
    assert task.core_project_id == "project-1"
    assert task.core_idea_id == "idea-1"
    assert task.core_task_id == "task-1"
    assert task.core_execution_id == "execution-1"
    orch._core_client.create_task.assert_awaited_once()
    orch._core_client.create_execution.assert_awaited()
    orch._core_client.update_task.assert_awaited()
    orch._core_client.update_execution.assert_awaited()
