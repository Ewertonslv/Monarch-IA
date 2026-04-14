import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport


@pytest.fixture
async def client():
    from interfaces.web.app import app, _db, _orchestrator
    import interfaces.web.app as web_module

    mock_db = AsyncMock()
    mock_orch = AsyncMock()

    mock_db.list_active_tasks = AsyncMock(return_value=[])
    mock_db.get_task = AsyncMock(return_value=None)

    web_module._db = mock_db
    web_module._orchestrator = mock_orch

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac, mock_db, mock_orch

    web_module._db = None
    web_module._orchestrator = None


@pytest.mark.asyncio
async def test_list_tasks_empty(client):
    ac, mock_db, _ = client
    resp = await ac.get("/tasks")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_task_returns_task_id(client):
    ac, mock_db, mock_orch = client
    mock_orch.run = AsyncMock(return_value=MagicMock(
        task_id="monarch-abc", status=MagicMock(value="done"),
        raw_input="test", priority=None, branch_name=None, pr_url=None,
        created_at=MagicMock(isoformat=lambda: "2026-01-01T00:00:00"),
        updated_at=MagicMock(isoformat=lambda: "2026-01-01T00:00:00"),
        history=[]
    ))
    resp = await ac.post("/tasks", json={"raw_input": "build login page"})
    assert resp.status_code == 200
    data = resp.json()
    assert "task_id" in data
    assert data["task_id"].startswith("monarch-")


@pytest.mark.asyncio
async def test_get_task_not_found(client):
    ac, mock_db, _ = client
    mock_db.get_task = AsyncMock(return_value=None)
    resp = await ac.get("/tasks/monarch-nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_get_task_found(client):
    from core.task import Task
    ac, mock_db, _ = client
    task = Task(raw_input="build API")
    mock_db.get_task = AsyncMock(return_value=task)
    resp = await ac.get(f"/tasks/{task.task_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["raw_input"] == "build API"


@pytest.mark.asyncio
async def test_approve_task(client):
    ac, _, mock_orch = client
    resp = await ac.post("/tasks/monarch-123/approve")
    assert resp.status_code == 200
    mock_orch.approve_task.assert_called_once_with("monarch-123")


@pytest.mark.asyncio
async def test_reject_task(client):
    ac, _, mock_orch = client
    resp = await ac.post("/tasks/monarch-123/reject")
    assert resp.status_code == 200
    mock_orch.reject_task.assert_called_once_with("monarch-123")
