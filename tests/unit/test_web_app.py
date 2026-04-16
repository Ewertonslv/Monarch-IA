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
async def test_index_renders_hub_template(client):
    ac, _, _ = client
    resp = await ac.get("/")
    assert resp.status_code == 200
    assert "Monarch Hub" in resp.text


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


@pytest.mark.asyncio
async def test_hub_overview_returns_fallback_when_core_is_unavailable(client):
    ac, _, _ = client
    with patch("interfaces.web.app._fetch_monarch_core_json", new=AsyncMock(return_value=None)):
        resp = await ac.get("/hub/overview")
    assert resp.status_code == 200
    assert resp.json()["projects_count"] == 0


@pytest.mark.asyncio
async def test_hub_activity_returns_core_payload(client):
    ac, _, _ = client
    payload = [{"id": "exec-1", "agent_name": "legacy-orchestrator"}]
    with patch("interfaces.web.app._fetch_monarch_core_json", new=AsyncMock(return_value=payload)):
        resp = await ac.get("/hub/activity")
    assert resp.status_code == 200
    assert resp.json() == payload


@pytest.mark.asyncio
async def test_hub_business_units_returns_core_payload(client):
    ac, _, _ = client
    payload = [{"id": "bu-1", "name": "Conteudo"}]
    with patch("interfaces.web.app._fetch_monarch_core_json", new=AsyncMock(return_value=payload)):
        resp = await ac.get("/hub/business-units")
    assert resp.status_code == 200
    assert resp.json() == payload


@pytest.mark.asyncio
async def test_hub_project_detail_includes_implementation_summary(client):
    ac, _, _ = client

    async def fake_fetch(path: str):
        if path == "/api/projects/project-1":
            return {
                "id": "project-1",
                "name": "Instagram Automation",
                "slug": "instagram-automation",
                "status": "incubating",
                "priority": "medium",
                "stage": "planning",
            }
        if path == "/api/projects/project-1/execution-summary":
            return {"readiness": 52, "stage_label": "Planejamento", "momentum": "Ganhando forma", "roadmap_total": 1, "roadmap_done": 0, "tasks_total": 1, "task_done": 0, "task_active": 0, "task_blocked": 0, "pending_approvals": 0, "failed_executions": 0, "next_checkpoint": "Criar fila de conteudo"}
        if path == "/api/projects/project-1/implementation-summary":
            return {
                "implementation_status": "implementado localmente",
                "canonical_path": "apps/instagram-automation",
                "deliverable": "Pesquisa, fila, briefing e checklist de publicacao assistida.",
                "package_present": True,
                "readme_present": True,
                "test_suite_present": True,
                "module_count": 4,
                "module_labels": ["research", "queue", "briefing", "publication"],
            }
        return []

    with patch("interfaces.web.app._fetch_monarch_core_json", new=AsyncMock(side_effect=fake_fetch)):
        resp = await ac.get("/hub/projects/project-1")

    assert resp.status_code == 200
    data = resp.json()
    assert data["project"]["slug"] == "instagram-automation"
    assert data["implementation_summary"]["canonical_path"] == "apps/instagram-automation"
    assert data["implementation_summary"]["module_count"] == 4


@pytest.mark.asyncio
async def test_hub_create_business_unit_returns_core_payload(client):
    ac, _, _ = client
    post_mock = AsyncMock(return_value={"id": "bu-1", "name": "Conteudo"})
    with patch("interfaces.web.app._post_monarch_core_json", new=post_mock):
        resp = await ac.post(
            "/hub/business-units",
            json={
                "name": "Conteudo",
                "slug": "conteudo",
                "description": "Midia e distribuicao",
                "status": "active",
            },
        )
    assert resp.status_code == 200
    assert resp.json()["id"] == "bu-1"
    post_mock.assert_awaited_once_with(
        "/api/business-units",
        {
            "name": "Conteudo",
            "slug": "conteudo",
            "description": "Midia e distribuicao",
            "status": "active",
        },
    )


@pytest.mark.asyncio
async def test_hub_update_business_unit_returns_400_when_payload_is_empty(client):
    ac, _, _ = client
    resp = await ac.patch("/hub/business-units/bu-1", json={})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_hub_update_business_unit_returns_core_payload(client):
    ac, _, _ = client
    patch_mock = AsyncMock(return_value={"id": "bu-1", "status": "paused"})
    with patch("interfaces.web.app._patch_monarch_core_json", new=patch_mock):
        resp = await ac.patch(
            "/hub/business-units/bu-1",
            json={"name": "Conteudo", "slug": "conteudo", "status": "paused"},
        )
    assert resp.status_code == 200
    assert resp.json()["status"] == "paused"
    patch_mock.assert_awaited_once_with(
        "/api/business-units/bu-1",
        {"name": "Conteudo", "slug": "conteudo", "status": "paused"},
    )


@pytest.mark.asyncio
async def test_hub_business_unit_detail_returns_404_when_missing(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value=None)
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.get("/hub/business-units/bu-1")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_hub_business_unit_detail_returns_aggregated_payload(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(side_effect=[
        {"id": "bu-1", "name": "Conteudo", "status": "active"},
        [
            {"id": "project-1", "business_unit_id": "bu-1", "name": "Canal Dark", "status": "active", "priority": "high"},
            {"id": "project-2", "business_unit_id": "bu-2", "name": "Outro", "status": "paused", "priority": "low"},
        ],
        [
            {"id": "idea-1", "business_unit_id": "bu-1", "title": "Nova ideia", "status": "new"},
            {"id": "idea-2", "project_id": "project-1", "title": "Ideia ligada", "status": "reviewing"},
        ],
        [
            {"id": "task-1", "project_id": "project-1", "title": "Planejar", "status": "todo", "priority": "high"},
            {"id": "task-2", "project_id": "project-2", "title": "Outro", "status": "done", "priority": "low"},
        ],
        [
            {"id": "approval-1", "project_id": "project-1", "title": "Aprovar", "status": "pending"},
            {"id": "approval-2", "project_id": "project-2", "title": "Outra", "status": "approved"},
        ],
        [
            {"id": "metric-1", "project_id": "project-1", "metric_name": "revenue_brl", "metric_value": 500},
            {"id": "metric-2", "project_id": "project-1", "metric_name": "videos_published", "metric_value": 12},
        ],
    ])
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.get("/hub/business-units/bu-1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["business_unit"]["id"] == "bu-1"
    assert data["summary"]["projects_count"] == 1
    assert data["summary"]["active_projects_count"] == 1
    assert data["summary"]["open_ideas_count"] == 2
    assert data["summary"]["open_tasks_count"] == 1
    assert data["summary"]["pending_approvals_count"] == 1
    assert data["summary"]["metrics_count"] == 2
    assert data["summary"]["revenue_brl_total"] == 500.0
    assert data["projects"][0]["id"] == "project-1"
    assert data["metrics"][0]["id"] == "metric-1"


@pytest.mark.asyncio
async def test_hub_projects_returns_core_payload(client):
    ac, _, _ = client
    payload = [{"id": "project-1", "name": "Canal Dark"}]
    with patch("interfaces.web.app._fetch_monarch_core_json", new=AsyncMock(return_value=payload)):
        resp = await ac.get("/hub/projects")
    assert resp.status_code == 200
    assert resp.json() == payload


@pytest.mark.asyncio
async def test_hub_projects_forwards_filters(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value=[])
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.get("/hub/projects", params={"status": "active", "priority": "high"})
    assert resp.status_code == 200
    fetch_mock.assert_awaited_once_with("/api/projects?status=active&priority=high")


@pytest.mark.asyncio
async def test_hub_project_detail_returns_404_when_project_missing(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value=None)
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.get("/hub/projects/project-1")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_hub_project_detail_returns_aggregated_payload(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(side_effect=[
        {"id": "project-1", "name": "Canal Dark"},
        [{"id": "idea-1", "title": "Ideia"}],
        [{"id": "task-1", "title": "Tarefa"}],
        [{"id": "approval-1", "title": "Aprovacao"}],
        [{"id": "execution-1", "execution_type": "pipeline_run"}],
        [{"id": "metric-1", "metric_name": "videos_published"}],
        [{"id": "roadmap-1", "title": "Fase MVP"}],
    ])
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.get("/hub/projects/project-1")
    assert resp.status_code == 200
    data = resp.json()
    assert data["project"]["id"] == "project-1"
    assert data["ideas"][0]["id"] == "idea-1"
    assert data["tasks"][0]["id"] == "task-1"
    assert data["approvals"][0]["id"] == "approval-1"
    assert data["executions"][0]["id"] == "execution-1"
    assert data["metrics"][0]["id"] == "metric-1"
    assert data["roadmap_items"][0]["id"] == "roadmap-1"


@pytest.mark.asyncio
async def test_hub_project_update_returns_400_when_payload_is_empty(client):
    ac, _, _ = client
    resp = await ac.patch("/hub/projects/project-1", json={})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_hub_project_update_returns_core_payload(client):
    ac, _, _ = client
    patch_mock = AsyncMock(return_value={"id": "project-1", "status": "active"})
    with patch("interfaces.web.app._patch_monarch_core_json", new=patch_mock):
        resp = await ac.patch(
            "/hub/projects/project-1",
            json={
                "status": "active",
                "priority": "high",
                "current_focus": "Definir nicho",
                "next_action": "Listar 10 ideias",
            },
        )
    assert resp.status_code == 200
    assert resp.json()["id"] == "project-1"
    patch_mock.assert_awaited_once_with(
        "/api/projects/project-1",
        {
            "status": "active",
            "priority": "high",
            "current_focus": "Definir nicho",
            "next_action": "Listar 10 ideias",
        },
    )


@pytest.mark.asyncio
async def test_hub_project_update_returns_502_when_core_fails(client):
    ac, _, _ = client
    with patch("interfaces.web.app._patch_monarch_core_json", new=AsyncMock(return_value=None)):
        resp = await ac.patch("/hub/projects/project-1", json={"status": "paused"})
    assert resp.status_code == 502


@pytest.mark.asyncio
async def test_hub_ideas_returns_core_payload(client):
    ac, _, _ = client
    payload = [{"id": "idea-1", "title": "Achadinho promissor"}]
    with patch("interfaces.web.app._fetch_monarch_core_json", new=AsyncMock(return_value=payload)):
        resp = await ac.get("/hub/ideas")
    assert resp.status_code == 200
    assert resp.json() == payload


@pytest.mark.asyncio
async def test_hub_ideas_forwards_filters(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value=[])
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.get("/hub/ideas", params={"status": "new", "classification": "experiment"})
    assert resp.status_code == 200
    fetch_mock.assert_awaited_once_with("/api/ideas?status=new&classification=experiment")


@pytest.mark.asyncio
async def test_hub_create_idea_returns_core_payload(client):
    ac, _, _ = client
    post_mock = AsyncMock(return_value={"id": "idea-1", "title": "Canal dark de reviews"})
    with patch("interfaces.web.app._post_monarch_core_json", new=post_mock):
        resp = await ac.post(
            "/hub/ideas",
            json={
                "title": "Canal dark de reviews",
                "raw_input": "Quero testar um canal dark com produtos virais.",
                "classification": "content_opportunity",
                "priority_score": 8.7,
            },
        )
    assert resp.status_code == 200
    assert resp.json()["id"] == "idea-1"
    post_mock.assert_awaited_once_with(
        "/api/ideas",
        {
            "title": "Canal dark de reviews",
            "raw_input": "Quero testar um canal dark com produtos virais.",
            "source": "manual",
            "classification": "content_opportunity",
            "priority_score": 8.7,
        },
    )


@pytest.mark.asyncio
async def test_hub_update_idea_returns_400_when_payload_is_empty(client):
    ac, _, _ = client
    resp = await ac.patch("/hub/ideas/idea-1", json={})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_hub_update_idea_returns_core_payload(client):
    ac, _, _ = client
    patch_mock = AsyncMock(return_value={"id": "idea-1", "status": "reviewing"})
    with patch("interfaces.web.app._patch_monarch_core_json", new=patch_mock):
        resp = await ac.patch(
            "/hub/ideas/idea-1",
            json={"status": "reviewing", "classification": "experiment"},
        )
    assert resp.status_code == 200
    assert resp.json()["status"] == "reviewing"
    patch_mock.assert_awaited_once_with(
        "/api/ideas/idea-1",
        {"status": "reviewing", "classification": "experiment"},
    )


@pytest.mark.asyncio
async def test_hub_convert_idea_to_project_returns_404_when_idea_missing(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value=None)
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.post(
            "/hub/ideas/idea-1/convert-to-project",
            json={"business_unit_id": "bu-1", "project_type": "content"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_hub_convert_idea_to_project_creates_project_and_updates_idea(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value={
        "id": "idea-1",
        "title": "Canal dark de reviews",
        "raw_input": "Criar canal dark focado em reviews de produtos virais.",
        "priority_score": 8.7,
    })
    post_mock = AsyncMock(side_effect=[
        {"id": "project-1", "name": "Canal dark de reviews", "project_type": "content"},
        {"id": "task-1", "title": "Definir escopo inicial de Canal dark de reviews"},
        {"id": "task-2", "title": "Criar backlog base de Canal dark de reviews"},
        {"id": "task-3", "title": "Mapear pauta inicial de Canal dark de reviews"},
        {"id": "task-4", "title": "Definir criterio de validacao de Canal dark de reviews"},
    ])
    patch_mock = AsyncMock(return_value={"id": "idea-1", "status": "converted", "project_id": "project-1"})

    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock), \
         patch("interfaces.web.app._post_monarch_core_json", new=post_mock), \
         patch("interfaces.web.app._patch_monarch_core_json", new=patch_mock):
        resp = await ac.post(
            "/hub/ideas/idea-1/convert-to-project",
            json={"business_unit_id": "bu-1", "project_type": "content"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["project"]["id"] == "project-1"
    assert data["idea"]["status"] == "converted"
    assert len(data["created_tasks"]) == 4
    first_call = post_mock.await_args_list[0]
    assert first_call.args == (
        "/api/projects",
        {
            "business_unit_id": "bu-1",
            "name": "Canal dark de reviews",
            "slug": "canal-dark-de-reviews",
            "description": "Criar canal dark focado em reviews de produtos virais.",
            "project_type": "content",
            "status": "incubating",
            "priority": "high",
            "stage": "planning",
            "main_goal": "Criar canal dark focado em reviews de produtos virais.",
            "current_focus": "Validar escopo inicial",
            "next_action": "Criar backlog inicial",
        },
    )
    task_calls = post_mock.await_args_list[1:]
    assert len(task_calls) == 4
    assert task_calls[0].args[0] == "/api/tasks"
    assert task_calls[0].args[1]["title"] == "Definir escopo inicial de Canal dark de reviews"
    assert task_calls[1].args[1]["title"] == "Criar backlog base de Canal dark de reviews"
    assert task_calls[2].args[1]["owner_name"] == "content_researcher"
    assert task_calls[3].args[1]["approval_required"] is True
    patch_mock.assert_awaited_once_with(
        "/api/ideas/idea-1",
        {"status": "converted", "project_id": "project-1", "business_unit_id": "bu-1"},
    )


@pytest.mark.asyncio
async def test_hub_convert_idea_to_task_returns_404_when_idea_missing(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value=None)
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.post(
            "/hub/ideas/idea-1/convert-to-task",
            json={"project_id": "project-1", "task_type": "research"},
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_hub_convert_idea_to_task_returns_400_when_project_is_missing(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value={"id": "idea-1", "title": "Ideia solta", "raw_input": "Algo"})
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.post(
            "/hub/ideas/idea-1/convert-to-task",
            json={"task_type": "research"},
        )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_hub_convert_idea_to_task_creates_task_and_updates_idea(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value={
        "id": "idea-1",
        "title": "Pesquisar nicho do canal dark",
        "raw_input": "Mapear os nichos com maior potencial de retencao.",
        "business_unit_id": "bu-1",
    })
    post_mock = AsyncMock(return_value={"id": "task-1", "title": "Pesquisar nicho do canal dark"})
    patch_mock = AsyncMock(return_value={"id": "idea-1", "status": "converted", "project_id": "project-1"})

    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock), \
         patch("interfaces.web.app._post_monarch_core_json", new=post_mock), \
         patch("interfaces.web.app._patch_monarch_core_json", new=patch_mock):
        resp = await ac.post(
            "/hub/ideas/idea-1/convert-to-task",
            json={"project_id": "project-1", "task_type": "research"},
        )

    assert resp.status_code == 200
    data = resp.json()
    assert data["task"]["id"] == "task-1"
    assert data["idea"]["status"] == "converted"
    post_mock.assert_awaited_once_with(
        "/api/tasks",
        {
            "project_id": "project-1",
            "title": "Pesquisar nicho do canal dark",
            "description": "Mapear os nichos com maior potencial de retencao.",
            "task_type": "research",
            "status": "todo",
            "priority": "medium",
            "owner_type": "agent",
            "owner_name": None,
            "approval_required": False,
        },
    )
    patch_mock.assert_awaited_once_with(
        "/api/ideas/idea-1",
        {
            "status": "converted",
            "classification": "operational_task",
            "project_id": "project-1",
            "business_unit_id": "bu-1",
        },
    )


@pytest.mark.asyncio
async def test_hub_metrics_returns_core_payload(client):
    ac, _, _ = client
    payload = [{"id": "metric-1", "metric_name": "revenue_brl"}]
    with patch("interfaces.web.app._fetch_monarch_core_json", new=AsyncMock(return_value=payload)):
        resp = await ac.get("/hub/metrics")
    assert resp.status_code == 200
    assert resp.json() == payload


@pytest.mark.asyncio
async def test_hub_metrics_forwards_filters(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value=[])
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.get("/hub/metrics", params={"project_id": "project-1", "metric_name": "revenue_brl"})
    assert resp.status_code == 200
    fetch_mock.assert_awaited_once_with("/api/project-metrics?project_id=project-1&metric_name=revenue_brl")


@pytest.mark.asyncio
async def test_hub_create_metric_returns_core_payload(client):
    ac, _, _ = client
    post_mock = AsyncMock(return_value={"id": "metric-1", "metric_name": "revenue_brl"})
    with patch("interfaces.web.app._post_monarch_core_json", new=post_mock):
        resp = await ac.post(
            "/hub/metrics",
            json={
                "project_id": "project-1",
                "metric_name": "revenue_brl",
                "metric_value": 1250.5,
                "metric_unit": "BRL",
            },
        )
    assert resp.status_code == 200
    assert resp.json()["id"] == "metric-1"
    post_mock.assert_awaited_once_with(
        "/api/project-metrics",
        {
            "project_id": "project-1",
            "metric_name": "revenue_brl",
            "metric_value": 1250.5,
            "metric_unit": "BRL",
        },
    )


@pytest.mark.asyncio
async def test_hub_tasks_returns_core_payload(client):
    ac, _, _ = client
    payload = [{"id": "task-1", "title": "Mapear nichos"}]
    with patch("interfaces.web.app._fetch_monarch_core_json", new=AsyncMock(return_value=payload)):
        resp = await ac.get("/hub/tasks")
    assert resp.status_code == 200
    assert resp.json() == payload


@pytest.mark.asyncio
async def test_hub_tasks_forwards_filters(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value=[])
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.get(
            "/hub/tasks",
            params={"status": "todo", "priority": "high", "project_id": "project-1"},
        )
    assert resp.status_code == 200
    fetch_mock.assert_awaited_once_with("/api/tasks?status=todo&project_id=project-1&priority=high")


@pytest.mark.asyncio
async def test_hub_create_task_returns_core_payload(client):
    ac, _, _ = client
    post_mock = AsyncMock(return_value={"id": "task-1", "title": "Planejar canal dark"})
    with patch("interfaces.web.app._post_monarch_core_json", new=post_mock):
        resp = await ac.post(
            "/hub/tasks",
            json={
                "project_id": "project-1",
                "title": "Planejar canal dark",
                "description": "Definir quadro editorial",
                "task_type": "planning",
                "priority": "high",
            },
        )
    assert resp.status_code == 200
    assert resp.json()["id"] == "task-1"
    post_mock.assert_awaited_once_with(
        "/api/tasks",
        {
            "project_id": "project-1",
            "title": "Planejar canal dark",
            "description": "Definir quadro editorial",
            "task_type": "planning",
            "status": "todo",
            "priority": "high",
            "owner_type": "agent",
            "approval_required": False,
        },
    )


@pytest.mark.asyncio
async def test_hub_update_task_returns_400_when_payload_is_empty(client):
    ac, _, _ = client
    resp = await ac.patch("/hub/tasks/task-1", json={})
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_hub_update_task_returns_core_payload(client):
    ac, _, _ = client
    patch_mock = AsyncMock(return_value={"id": "task-1", "status": "in_progress"})
    with patch("interfaces.web.app._patch_monarch_core_json", new=patch_mock):
        resp = await ac.patch(
            "/hub/tasks/task-1",
            json={"status": "in_progress", "priority": "critical", "owner_name": "Monarch"},
        )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"
    patch_mock.assert_awaited_once_with(
        "/api/tasks/task-1",
        {"status": "in_progress", "priority": "critical", "owner_name": "Monarch"},
    )


@pytest.mark.asyncio
async def test_hub_approvals_returns_core_payload(client):
    ac, _, _ = client
    payload = [{"id": "approval-1", "title": "Publicar projeto"}]
    with patch("interfaces.web.app._fetch_monarch_core_json", new=AsyncMock(return_value=payload)):
        resp = await ac.get("/hub/approvals")
    assert resp.status_code == 200
    assert resp.json() == payload


@pytest.mark.asyncio
async def test_hub_approvals_forwards_filters(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value=[])
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.get("/hub/approvals", params={"status": "pending", "project_id": "project-1"})
    assert resp.status_code == 200
    fetch_mock.assert_awaited_once_with("/api/approvals?status=pending&project_id=project-1")


@pytest.mark.asyncio
async def test_hub_approve_approval_returns_core_payload(client):
    ac, _, _ = client
    post_mock = AsyncMock(return_value={"id": "approval-1", "status": "approved"})
    with patch("interfaces.web.app._post_monarch_core_json", new=post_mock):
        resp = await ac.post("/hub/approvals/approval-1/approve", json={"decided_by": "Ewerton"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "approved"
    post_mock.assert_awaited_once_with(
        "/api/approvals/approval-1/approve",
        {"decided_by": "Ewerton"},
    )


@pytest.mark.asyncio
async def test_hub_reject_approval_returns_core_payload(client):
    ac, _, _ = client
    post_mock = AsyncMock(return_value={"id": "approval-1", "status": "rejected"})
    with patch("interfaces.web.app._post_monarch_core_json", new=post_mock):
        resp = await ac.post("/hub/approvals/approval-1/reject", json={"decided_by": "Ewerton"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "rejected"
    post_mock.assert_awaited_once_with(
        "/api/approvals/approval-1/reject",
        {"decided_by": "Ewerton"},
    )


@pytest.mark.asyncio
async def test_hub_rate_limit_returns_429(client):
    ac, _, _ = client
    with patch("interfaces.web.app._hub_limiter.allow", return_value=False):
        resp = await ac.get("/hub/overview")
    assert resp.status_code == 429
    assert resp.json()["detail"] == "Rate limit exceeded for hub endpoints"


@pytest.mark.asyncio
async def test_hub_activity_forwards_filters(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value=[])
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.get(
            "/hub/activity",
            params={
                "limit": 10,
                "project_id": "project-1",
                "agent_name": "planner",
                "status": "running",
                "execution_type": "pipeline_run",
            },
        )
    assert resp.status_code == 200
    fetch_mock.assert_awaited_once_with(
        "/api/dashboard/activity?limit=10&project_id=project-1&agent_name=planner&status=running&execution_type=pipeline_run"
    )


@pytest.mark.asyncio
async def test_hub_performance_forwards_filters(client):
    ac, _, _ = client
    fetch_mock = AsyncMock(return_value=[])
    with patch("interfaces.web.app._fetch_monarch_core_json", new=fetch_mock):
        resp = await ac.get(
            "/hub/performance",
            params={"business_unit_id": "bu-1", "metric_name": "revenue_brl", "limit": 25},
        )
    assert resp.status_code == 200
    fetch_mock.assert_awaited_once_with(
        "/api/dashboard/performance?limit=25&business_unit_id=bu-1&metric_name=revenue_brl"
    )


@pytest.mark.asyncio
async def test_hub_agents_returns_core_payload(client):
    ac, _, _ = client
    payload = [{"id": "agent-1", "name": "Planner"}]
    with patch("interfaces.web.app._fetch_monarch_core_json", new=AsyncMock(return_value=payload)):
        resp = await ac.get("/hub/agents")
    assert resp.status_code == 200
    assert resp.json() == payload


@pytest.mark.asyncio
async def test_hub_roadmap_items_returns_core_payload(client):
    ac, _, _ = client
    payload = [{"id": "roadmap-1", "title": "MVP"}]
    with patch("interfaces.web.app._fetch_monarch_core_json", new=AsyncMock(return_value=payload)):
        resp = await ac.get("/hub/roadmap-items", params={"project_id": "project-1", "phase": "mvp"})
    assert resp.status_code == 200
    assert resp.json() == payload
