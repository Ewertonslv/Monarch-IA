import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from core.orchestrator import Orchestrator
from core.task import Task, TaskStatus
from agents.base import AgentResult


def _result(output: dict = None, confidence: float = 0.9) -> AgentResult:
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
async def test_orchestrator_runs_full_pipeline(db):
    orch = Orchestrator(db)

    # Patch all agents to succeed immediately
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
        for AgentCls in [DA, PA, AA, PLA, IA, TA, DEPLOY, DOC, OBS]:
            AgentCls.return_value.run = AsyncMock(return_value=_result())
        DVA.return_value.run = AsyncMock(return_value=_result({"approved": True}))

        async def _review_run(task):
            assert task.pr_url == "https://github.com/owner/repo/pull/1"
            return _result({"approved": True, "overall_quality": "good"})

        RA.return_value.run = AsyncMock(side_effect=_review_run)
        SA.return_value.run = AsyncMock(return_value=_result({"approved": True, "risk_level": "low"}))
        GH.return_value.create_branch = MagicMock()
        GH.return_value.create_pr = MagicMock(return_value="https://github.com/owner/repo/pull/1")

        task = Task(raw_input="add search endpoint")
        task.branch_name = "feat/search"
        task.requirements = {"summary": "Search endpoint", "complexity": "medium", "affected_areas": [], "acceptance_criteria": []}
        result = await orch.run(task)

    assert result.status == TaskStatus.DONE


@pytest.mark.asyncio
async def test_orchestrator_marks_failed_on_agent_error(db):
    orch = Orchestrator(db)

    with (
        patch("core.orchestrator.DiscoveryAgent") as DA,
        patch("core.orchestrator.PrioritizationAgent"),
        patch("core.orchestrator.ArchitectureAgent"),
        patch("core.orchestrator.PlanningAgent"),
        patch("core.orchestrator.DevilsAdvocateAgent"),
        patch("core.orchestrator.ImplementerAgent"),
        patch("core.orchestrator.TestingAgent"),
        patch("core.orchestrator.ReviewerAgent"),
        patch("core.orchestrator.SecurityAgent"),
        patch("core.orchestrator.DeployAgent"),
        patch("core.orchestrator.DocumentationAgent"),
        patch("core.orchestrator.ObservabilityAgent"),
        patch("core.orchestrator.GitHubTools"),
    ):
        DA.return_value.run = AsyncMock(side_effect=RuntimeError("Claude is down"))
        task = Task(raw_input="failing task")
        result = await orch.run(task)

    assert result.status == TaskStatus.FAILED


@pytest.mark.asyncio
async def test_orchestrator_discarded_on_rejection(db):
    orch = Orchestrator(db)

    with (
        patch("core.orchestrator.DiscoveryAgent") as DA,
        patch("core.orchestrator.PrioritizationAgent") as PA,
        patch("core.orchestrator.ArchitectureAgent") as AA,
        patch("core.orchestrator.PlanningAgent") as PLA,
        patch("core.orchestrator.DevilsAdvocateAgent") as DVA,
        patch("core.orchestrator.ImplementerAgent"),
        patch("core.orchestrator.TestingAgent"),
        patch("core.orchestrator.ReviewerAgent"),
        patch("core.orchestrator.SecurityAgent"),
        patch("core.orchestrator.DeployAgent"),
        patch("core.orchestrator.DocumentationAgent"),
        patch("core.orchestrator.ObservabilityAgent"),
        patch("core.orchestrator.GitHubTools"),
        patch.object(orch, "_request_approval", new=AsyncMock(return_value=False)),
    ):
        for AgentCls in [DA, PA, AA, PLA]:
            AgentCls.return_value.run = AsyncMock(return_value=_result())
        DVA.return_value.run = AsyncMock(return_value=_result({"approved": True}))

        task = Task(raw_input="rejected task")
        result = await orch.run(task)

    assert result.status == TaskStatus.DISCARDED


@pytest.mark.asyncio
async def test_request_approval_persists_core_approval_id(db):
    orch = Orchestrator(db)
    task = Task(raw_input="aprovar tarefa")
    await db.save_task(task)
    original_get_task = db.get_task

    async def _fake_sync(task_obj, stage):
        task_obj.current_core_approval_id = "approval-123"

    async def _fake_get_task(task_id):
        fresh = await original_get_task(task_id)
        assert fresh is not None
        fresh.status = TaskStatus.RUNNING
        return fresh

    with (
        patch.object(orch, "_sync_approval_request", new=AsyncMock(side_effect=_fake_sync)),
        patch("core.orchestrator.asyncio.sleep", new=AsyncMock()),
        patch.object(db, "get_task", new=AsyncMock(side_effect=_fake_get_task)),
    ):
        approved = await orch._request_approval(task, "post_planning")

    persisted = await db.get_task(task.task_id)
    assert approved is True
    assert persisted is not None
    assert persisted.current_core_approval_id == "approval-123"
