import pytest

from core.monarch_core_client import MonarchCoreClient


class DummyResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._payload


class DummyHTTPClient:
    def __init__(self) -> None:
        self.calls: list[tuple[str, str, dict | None, dict | None]] = []

    async def get(self, url: str, params=None, headers=None):
        self.calls.append(("GET", url, params, headers))
        return DummyResponse([{"id": "project-1", "business_unit_id": "bu-1", "slug": "monarch-ai"}])

    async def post(self, url: str, json=None, headers=None):
        self.calls.append(("POST", url, json, headers))
        return DummyResponse({"id": "created-1"})

    async def patch(self, url: str, json=None, headers=None):
        self.calls.append(("PATCH", url, json, headers))
        return DummyResponse({"id": "updated-1"})


@pytest.mark.asyncio
async def test_monarch_core_client_uses_slug_filter() -> None:
    http_client = DummyHTTPClient()
    client = MonarchCoreClient(
        base_url="http://monarch-core:8010",
        project_slug="monarch-ai",
        client=http_client,
    )

    project = await client.ensure_project()

    assert project["id"] == "project-1"
    assert http_client.calls[0] == (
        "GET",
        "http://monarch-core:8010/api/projects",
        {"slug": "monarch-ai"},
        {},
    )


@pytest.mark.asyncio
async def test_monarch_core_client_creates_and_updates_task() -> None:
    http_client = DummyHTTPClient()
    client = MonarchCoreClient(
        base_url="http://monarch-core:8010",
        project_slug="monarch-ai",
        client=http_client,
    )

    created = await client.create_task(
        project_id="project-1",
        title="Teste",
        description="Descricao",
        status="in_progress",
        priority="high",
        approval_required=True,
    )
    updated = await client.update_task(
        task_id="task-1",
        status="blocked",
        priority="high",
        approval_required=True,
    )

    assert created == {"id": "created-1"}
    assert updated == {"id": "updated-1"}
    assert http_client.calls[0][0] == "POST"
    assert http_client.calls[1] == (
        "PATCH",
        "http://monarch-core:8010/api/tasks/task-1",
        {"status": "blocked", "priority": "high", "approval_required": True},
        {},
    )


@pytest.mark.asyncio
async def test_monarch_core_client_creates_and_updates_execution() -> None:
    http_client = DummyHTTPClient()
    client = MonarchCoreClient(
        base_url="http://monarch-core:8010",
        project_slug="monarch-ai",
        client=http_client,
    )

    created = await client.create_execution(
        project_id="project-1",
        task_id="task-1",
        agent_name="legacy-orchestrator",
        execution_type="pipeline_run",
        status="running",
        input_payload="entrada",
    )
    updated = await client.update_execution(
        execution_id="execution-1",
        status="completed",
        output_summary="ok",
    )

    assert created == {"id": "created-1"}
    assert updated == {"id": "updated-1"}
    assert http_client.calls[0][1] == "http://monarch-core:8010/api/executions"
    assert http_client.calls[1] == (
        "PATCH",
        "http://monarch-core:8010/api/executions/execution-1",
        {"status": "completed", "output_summary": "ok"},
        {},
    )
