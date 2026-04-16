import asyncio
import json
import logging
import re
import time
from collections import defaultdict, deque
from contextlib import asynccontextmanager
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel

from config import config
from core.orchestrator import Orchestrator
from core.task import Task, TaskStatus
from storage.database import Database

logger = logging.getLogger(__name__)

# Shared state
_db: Database | None = None
_orchestrator: Orchestrator | None = None
_ws_clients: list[WebSocket] = []


class SlidingWindowRateLimiter:
    def __init__(self, max_requests: int, window_seconds: int) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        window_start = now - self.window_seconds
        bucket = self._hits[key]
        while bucket and bucket[0] < window_start:
            bucket.popleft()
        if len(bucket) >= self.max_requests:
            return False
        bucket.append(now)
        return True


_hub_limiter = SlidingWindowRateLimiter(max_requests=300, window_seconds=60)
_task_limiter = SlidingWindowRateLimiter(max_requests=120, window_seconds=60)


def _client_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _db, _orchestrator
    _db = Database(config.database_url)
    await _db.init()
    _orchestrator = Orchestrator(_db)
    logger.info("Monarch AI web interface ready")
    yield
    if _orchestrator:
        await _orchestrator.aclose()
    if _db:
        await _db.close()


app = FastAPI(title="Monarch AI", lifespan=lifespan)

import os
_templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=_templates_dir)


@app.middleware("http")
async def add_security_and_rate_limit(request: Request, call_next):
    path = request.url.path
    client_ip = _client_ip(request)

    if path.startswith("/hub/") and not _hub_limiter.allow(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded for hub endpoints"},
            headers={"Retry-After": "60"},
        )
    if path.startswith("/tasks") and not _task_limiter.allow(client_ip):
        return JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded for task endpoints"},
            headers={"Retry-After": "60"},
        )

    response = await call_next(request)
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


# ------------------------------------------------------------------
# REST endpoints
# ------------------------------------------------------------------

class TaskRequest(BaseModel):
    raw_input: str


class ProjectUpdateRequest(BaseModel):
    status: str | None = None
    priority: str | None = None
    current_focus: str | None = None
    next_action: str | None = None


class IdeaCreateRequest(BaseModel):
    title: str
    raw_input: str
    source: str = "manual"
    classification: str | None = None
    business_unit_id: str | None = None
    project_id: str | None = None
    priority_score: float | None = None


class IdeaUpdateRequest(BaseModel):
    status: str | None = None
    classification: str | None = None
    project_id: str | None = None


class HubTaskCreateRequest(BaseModel):
    project_id: str
    title: str
    description: str | None = None
    task_type: str
    status: str = "todo"
    priority: str = "medium"
    owner_type: str = "agent"
    owner_name: str | None = None
    approval_required: bool = False
    due_at: str | None = None


class HubTaskUpdateRequest(BaseModel):
    status: str | None = None
    priority: str | None = None
    owner_name: str | None = None


class HubApprovalDecisionRequest(BaseModel):
    decided_by: str = "Ewerton Viggo"


class BusinessUnitCreateRequest(BaseModel):
    name: str
    slug: str
    description: str | None = None
    status: str = "active"


class BusinessUnitUpdateRequest(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    status: str | None = None


class ProjectMetricCreateRequest(BaseModel):
    project_id: str
    metric_name: str
    metric_value: float
    metric_unit: str | None = None


class AgentProfileCreateRequest(BaseModel):
    name: str
    slug: str
    role: str
    capabilities: str | None = None
    pipeline_name: str | None = None
    status: str = "active"
    notes: str | None = None


class AgentProfileUpdateRequest(BaseModel):
    name: str | None = None
    slug: str | None = None
    role: str | None = None
    capabilities: str | None = None
    pipeline_name: str | None = None
    status: str | None = None
    notes: str | None = None


class RoadmapItemCreateRequest(BaseModel):
    project_id: str
    title: str
    description: str | None = None
    phase: str = "backlog"
    status: str = "planned"
    priority: str = "medium"
    order_index: int = 0
    due_at: str | None = None


class RoadmapItemUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    phase: str | None = None
    status: str | None = None
    priority: str | None = None
    order_index: int | None = None
    due_at: str | None = None


class IdeaConvertRequest(BaseModel):
    business_unit_id: str
    project_type: str
    name: str | None = None
    slug: str | None = None
    priority: str | None = None
    status: str = "incubating"
    stage: str = "planning"


class IdeaConvertToTaskRequest(BaseModel):
    project_id: str | None = None
    task_type: str = "planning"
    priority: str = "medium"
    owner_type: str = "agent"
    owner_name: str | None = None
    approval_required: bool = False
    status: str = "todo"


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "novo-projeto"


def _build_initial_backlog(project: dict[str, Any], idea: dict[str, Any]) -> list[dict[str, Any]]:
    project_type = project.get("project_type", "internal_tool")
    project_id = project["id"]
    project_name = project["name"]
    common_backlog = [
        {
            "project_id": project_id,
            "title": f"Definir escopo inicial de {project_name}",
            "description": idea.get("raw_input") or "Traduzir a ideia em escopo executavel.",
            "task_type": "planning",
            "status": "todo",
            "priority": "high",
            "owner_type": "agent",
            "owner_name": "planner",
            "approval_required": False,
        },
        {
            "project_id": project_id,
            "title": f"Criar backlog base de {project_name}",
            "description": "Quebrar o projeto em entregas curtas, com foco na primeira validacao.",
            "task_type": "planning",
            "status": "todo",
            "priority": "high",
            "owner_type": "agent",
            "owner_name": "planner",
            "approval_required": False,
        },
    ]

    type_specific: dict[str, list[dict[str, Any]]] = {
        "content": [
            {
                "project_id": project_id,
                "title": f"Mapear pauta inicial de {project_name}",
                "description": "Selecionar temas, formatos e ganchos para a primeira leva de conteudo.",
                "task_type": "content",
                "status": "todo",
                "priority": "high",
                "owner_type": "agent",
                "owner_name": "content_researcher",
                "approval_required": False,
            },
            {
                "project_id": project_id,
                "title": f"Definir criterio de validacao de {project_name}",
                "description": "Estabelecer como medir se o formato e o nicho estao funcionando.",
                "task_type": "research",
                "status": "todo",
                "priority": "medium",
                "owner_type": "human",
                "owner_name": "ewerton",
                "approval_required": True,
            },
        ],
        "ecommerce": [
            {
                "project_id": project_id,
                "title": f"Definir criterio de produto vencedor em {project_name}",
                "description": "Estabelecer sinais de margem, apelo e potencial de venda.",
                "task_type": "research",
                "status": "todo",
                "priority": "high",
                "owner_type": "agent",
                "owner_name": "offer_hunter",
                "approval_required": False,
            },
            {
                "project_id": project_id,
                "title": f"Selecionar primeiras ofertas para {project_name}",
                "description": "Montar a primeira lista curta de produtos ou ofertas para teste.",
                "task_type": "research",
                "status": "todo",
                "priority": "high",
                "owner_type": "agent",
                "owner_name": "offer_hunter",
                "approval_required": False,
            },
        ],
        "product": [
            {
                "project_id": project_id,
                "title": f"Definir oferta inicial de {project_name}",
                "description": "Transformar a ideia em proposta de produto clara e vendavel.",
                "task_type": "planning",
                "status": "todo",
                "priority": "high",
                "owner_type": "agent",
                "owner_name": "planner",
                "approval_required": False,
            },
            {
                "project_id": project_id,
                "title": f"Mapear validacao comercial de {project_name}",
                "description": "Definir como o produto sera testado no mercado rapidamente.",
                "task_type": "research",
                "status": "todo",
                "priority": "medium",
                "owner_type": "human",
                "owner_name": "ewerton",
                "approval_required": True,
            },
        ],
        "automation": [
            {
                "project_id": project_id,
                "title": f"Desenhar fluxo principal de {project_name}",
                "description": "Definir entrada, processamento e saida do fluxo automatizado.",
                "task_type": "planning",
                "status": "todo",
                "priority": "high",
                "owner_type": "agent",
                "owner_name": "architect",
                "approval_required": False,
            },
            {
                "project_id": project_id,
                "title": f"Definir validacao tecnica de {project_name}",
                "description": "Especificar como o modulo sera testado e colocado em runtime.",
                "task_type": "review",
                "status": "todo",
                "priority": "medium",
                "owner_type": "agent",
                "owner_name": "reviewer",
                "approval_required": False,
            },
        ],
        "lab": [
            {
                "project_id": project_id,
                "title": f"Definir experimento inicial de {project_name}",
                "description": "Escolher um experimento pequeno e validavel para iniciar o lab.",
                "task_type": "research",
                "status": "todo",
                "priority": "medium",
                "owner_type": "human",
                "owner_name": "ewerton",
                "approval_required": True,
            }
        ],
        "internal_tool": [
            {
                "project_id": project_id,
                "title": f"Definir arquitetura inicial de {project_name}",
                "description": "Mapear os componentes e contratos principais do sistema.",
                "task_type": "planning",
                "status": "todo",
                "priority": "high",
                "owner_type": "agent",
                "owner_name": "architect",
                "approval_required": False,
            }
        ],
    }

    return common_backlog + type_specific.get(project_type, [])


def _monarch_core_headers() -> dict[str, str]:
    if not config.monarch_core_api_key:
        return {}
    return {"X-API-Key": config.monarch_core_api_key}


async def _fetch_monarch_core_json(path: str) -> Any:
    if not config.monarch_core_api_url:
        return None

    base_url = config.monarch_core_api_url.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{base_url}{path}", headers=_monarch_core_headers())
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        logger.warning("Could not fetch monarch-core data from %s: %s", path, exc)
        return None


async def _patch_monarch_core_json(path: str, payload: dict[str, Any]) -> Any:
    if not config.monarch_core_api_url:
        return None

    base_url = config.monarch_core_api_url.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.patch(f"{base_url}{path}", json=payload, headers=_monarch_core_headers())
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        logger.warning("Could not patch monarch-core data at %s: %s", path, exc)
        return None


async def _post_monarch_core_json(path: str, payload: dict[str, Any]) -> Any:
    if not config.monarch_core_api_url:
        return None

    base_url = config.monarch_core_api_url.rstrip("/")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(f"{base_url}{path}", json=payload, headers=_monarch_core_headers())
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as exc:
        logger.warning("Could not post monarch-core data at %s: %s", path, exc)
        return None


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="hub.html")


@app.post("/tasks")
async def create_task(body: TaskRequest):
    task = Task(raw_input=body.raw_input)
    asyncio.create_task(_run_task_and_broadcast(task))
    return {"task_id": task.task_id, "status": task.status}


@app.get("/tasks")
async def list_tasks():
    assert _db is not None
    tasks = await _db.list_active_tasks()
    return [_task_to_dict(t) for t in tasks]


@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    assert _db is not None
    task = await _db.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return _task_to_dict(task)


@app.post("/tasks/{task_id}/approve")
async def approve_task(task_id: str):
    assert _orchestrator is not None
    await _orchestrator.approve_task(task_id)
    return {"task_id": task_id, "action": "approved"}


@app.post("/tasks/{task_id}/reject")
async def reject_task(task_id: str):
    assert _orchestrator is not None
    await _orchestrator.reject_task(task_id)
    return {"task_id": task_id, "action": "rejected"}


@app.get("/hub/overview")
async def hub_overview():
    payload = await _fetch_monarch_core_json("/api/dashboard/overview")
    return payload or {
        "business_units_count": 0,
        "projects_count": 0,
        "active_projects_count": 0,
        "incubating_projects_count": 0,
        "open_ideas_count": 0,
        "high_priority_projects_count": 0,
        "open_tasks_count": 0,
        "pending_approvals_count": 0,
    }


@app.get("/hub/activity")
async def hub_activity(
    limit: int = 20,
    project_id: str | None = None,
    agent_name: str | None = None,
    status: str | None = None,
    execution_type: str | None = None,
):
    params: dict[str, str] = {"limit": str(limit)}
    if project_id:
        params["project_id"] = project_id
    if agent_name:
        params["agent_name"] = agent_name
    if status:
        params["status"] = status
    if execution_type:
        params["execution_type"] = execution_type

    path = "/api/dashboard/activity"
    if params:
        path = f"{path}?{urlencode(params)}"

    payload = await _fetch_monarch_core_json(path)
    return payload or []


@app.get("/hub/performance")
async def hub_performance(
    business_unit_id: str | None = None,
    metric_name: str | None = None,
    limit: int = 50,
):
    params: dict[str, str] = {"limit": str(limit)}
    if business_unit_id:
        params["business_unit_id"] = business_unit_id
    if metric_name:
        params["metric_name"] = metric_name

    path = "/api/dashboard/performance"
    if params:
        path = f"{path}?{urlencode(params)}"

    payload = await _fetch_monarch_core_json(path)
    return payload or []


@app.get("/hub/business-units")
async def hub_business_units():
    payload = await _fetch_monarch_core_json("/api/business-units")
    return payload or []


@app.post("/hub/business-units")
async def hub_create_business_unit(body: BusinessUnitCreateRequest):
    result = await _post_monarch_core_json("/api/business-units", body.model_dump(exclude_none=True))
    if not result:
        raise HTTPException(status_code=502, detail="Could not create business unit in monarch-core")
    return result


@app.patch("/hub/business-units/{business_unit_id}")
async def hub_update_business_unit(business_unit_id: str, body: BusinessUnitUpdateRequest):
    payload = body.model_dump(exclude_none=True)
    if not payload:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await _patch_monarch_core_json(f"/api/business-units/{business_unit_id}", payload)
    if not result:
        raise HTTPException(status_code=502, detail="Could not update business unit in monarch-core")
    return result


@app.get("/hub/business-units/{business_unit_id}")
async def hub_business_unit_detail(business_unit_id: str):
    business_unit = await _fetch_monarch_core_json(f"/api/business-units/{business_unit_id}")
    if not business_unit:
        raise HTTPException(status_code=404, detail="Business unit not found")

    projects = await _fetch_monarch_core_json("/api/projects") or []
    ideas = await _fetch_monarch_core_json("/api/ideas") or []
    tasks = await _fetch_monarch_core_json("/api/tasks") or []
    approvals = await _fetch_monarch_core_json("/api/approvals") or []
    metrics = await _fetch_monarch_core_json("/api/project-metrics") or []

    bu_projects = [project for project in projects if project.get("business_unit_id") == business_unit_id]
    bu_project_ids = {project["id"] for project in bu_projects}
    bu_ideas = [idea for idea in ideas if idea.get("business_unit_id") == business_unit_id or idea.get("project_id") in bu_project_ids]
    bu_tasks = [task for task in tasks if task.get("project_id") in bu_project_ids]
    bu_approvals = [approval for approval in approvals if approval.get("project_id") in bu_project_ids]
    bu_metrics = [metric for metric in metrics if metric.get("project_id") in bu_project_ids]

    return {
        "business_unit": business_unit,
        "summary": {
            "projects_count": len(bu_projects),
            "active_projects_count": sum(1 for project in bu_projects if project.get("status") == "active"),
            "open_ideas_count": sum(1 for idea in bu_ideas if idea.get("status") in {"new", "reviewing"}),
            "open_tasks_count": sum(1 for task in bu_tasks if task.get("status") in {"todo", "in_progress", "blocked"}),
            "pending_approvals_count": sum(1 for approval in bu_approvals if approval.get("status") == "pending"),
            "metrics_count": len(bu_metrics),
            "revenue_brl_total": round(
                sum(float(metric.get("metric_value") or 0) for metric in bu_metrics if metric.get("metric_name") == "revenue_brl"),
                2,
            ),
        },
        "projects": bu_projects[:8],
        "ideas": bu_ideas[:8],
        "tasks": bu_tasks[:8],
        "approvals": bu_approvals[:8],
        "metrics": bu_metrics[:8],
    }


@app.get("/hub/projects")
async def hub_projects(status: str | None = None, priority: str | None = None):
    params: dict[str, str] = {}
    if status:
        params["status"] = status
    if priority:
        params["priority"] = priority

    path = "/api/projects"
    if params:
        path = f"{path}?{urlencode(params)}"

    payload = await _fetch_monarch_core_json(path)
    return payload or []


@app.get("/hub/projects/{project_id}")
async def hub_project_detail(project_id: str):
    project = await _fetch_monarch_core_json(f"/api/projects/{project_id}")
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    execution_summary = await _fetch_monarch_core_json(
        f"/api/projects/{project_id}/execution-summary"
    )
    implementation_summary = await _fetch_monarch_core_json(
        f"/api/projects/{project_id}/implementation-summary"
    )
    ideas = await _fetch_monarch_core_json(f"/api/ideas?project_id={project_id}") or []
    tasks = await _fetch_monarch_core_json(f"/api/tasks?project_id={project_id}") or []
    approvals = await _fetch_monarch_core_json(f"/api/approvals?project_id={project_id}") or []
    executions = await _fetch_monarch_core_json(f"/api/executions?project_id={project_id}") or []
    metrics = await _fetch_monarch_core_json(f"/api/project-metrics?project_id={project_id}") or []
    roadmap_items = await _fetch_monarch_core_json(f"/api/roadmap-items?project_id={project_id}") or []

    return {
        "project": project,
        "ideas": ideas[:8],
        "tasks": tasks[:8],
        "approvals": approvals[:8],
        "executions": executions[:8],
        "metrics": metrics[:8],
        "roadmap_items": roadmap_items[:12],
        "execution_summary": execution_summary,
        "implementation_summary": implementation_summary,
    }


@app.patch("/hub/projects/{project_id}")
async def hub_project_update(project_id: str, body: ProjectUpdateRequest):
    payload = body.model_dump(exclude_none=True)
    if not payload:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await _patch_monarch_core_json(f"/api/projects/{project_id}", payload)
    if not result:
        raise HTTPException(status_code=502, detail="Could not update project in monarch-core")
    return result


@app.get("/hub/ideas")
async def hub_ideas(status: str | None = None, classification: str | None = None):
    params: dict[str, str] = {}
    if status:
        params["status"] = status
    if classification:
        params["classification"] = classification

    path = "/api/ideas"
    if params:
        path = f"{path}?{urlencode(params)}"

    payload = await _fetch_monarch_core_json(path)
    return payload or []


@app.post("/hub/ideas")
async def hub_create_idea(body: IdeaCreateRequest):
    result = await _post_monarch_core_json("/api/ideas", body.model_dump(exclude_none=True))
    if not result:
        raise HTTPException(status_code=502, detail="Could not create idea in monarch-core")
    return result


@app.patch("/hub/ideas/{idea_id}")
async def hub_update_idea(idea_id: str, body: IdeaUpdateRequest):
    payload = body.model_dump(exclude_none=True)
    if not payload:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await _patch_monarch_core_json(f"/api/ideas/{idea_id}", payload)
    if not result:
        raise HTTPException(status_code=502, detail="Could not update idea in monarch-core")
    return result


@app.post("/hub/ideas/{idea_id}/convert-to-project")
async def hub_convert_idea_to_project(idea_id: str, body: IdeaConvertRequest):
    idea = await _fetch_monarch_core_json(f"/api/ideas/{idea_id}")
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    project_name = body.name or idea["title"]
    project_slug = body.slug or _slugify(project_name)
    project_priority = body.priority or ("high" if (idea.get("priority_score") or 0) >= 8 else "medium")

    project_payload = {
        "business_unit_id": body.business_unit_id,
        "name": project_name,
        "slug": project_slug,
        "description": idea.get("raw_input"),
        "project_type": body.project_type,
        "status": body.status,
        "priority": project_priority,
        "stage": body.stage,
        "main_goal": idea.get("raw_input"),
        "current_focus": "Validar escopo inicial",
        "next_action": "Criar backlog inicial",
    }

    project = await _post_monarch_core_json("/api/projects", project_payload)
    if not project:
        raise HTTPException(status_code=502, detail="Could not create project in monarch-core")

    idea_update = await _patch_monarch_core_json(
        f"/api/ideas/{idea_id}",
        {
            "status": "converted",
            "project_id": project["id"],
            "business_unit_id": body.business_unit_id,
        },
    )
    if not idea_update:
        raise HTTPException(status_code=502, detail="Project created but idea sync failed in monarch-core")

    created_tasks: list[dict[str, Any]] = []
    for task_payload in _build_initial_backlog(project, idea):
        created_task = await _post_monarch_core_json("/api/tasks", task_payload)
        if created_task:
            created_tasks.append(created_task)

    return {"project": project, "idea": idea_update, "created_tasks": created_tasks}


@app.post("/hub/ideas/{idea_id}/convert-to-task")
async def hub_convert_idea_to_task(idea_id: str, body: IdeaConvertToTaskRequest):
    idea = await _fetch_monarch_core_json(f"/api/ideas/{idea_id}")
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")

    project_id = body.project_id or idea.get("project_id")
    if not project_id:
        raise HTTPException(status_code=400, detail="Project is required to convert idea to task")

    task_payload = {
        "project_id": project_id,
        "title": idea["title"],
        "description": idea.get("raw_input"),
        "task_type": body.task_type,
        "status": body.status,
        "priority": body.priority,
        "owner_type": body.owner_type,
        "owner_name": body.owner_name,
        "approval_required": body.approval_required,
    }

    task = await _post_monarch_core_json("/api/tasks", task_payload)
    if not task:
        raise HTTPException(status_code=502, detail="Could not create task in monarch-core")

    idea_update_payload: dict[str, Any] = {
        "status": "converted",
        "classification": "operational_task",
        "project_id": project_id,
    }
    if idea.get("business_unit_id"):
        idea_update_payload["business_unit_id"] = idea["business_unit_id"]

    idea_update = await _patch_monarch_core_json(f"/api/ideas/{idea_id}", idea_update_payload)
    if not idea_update:
        raise HTTPException(status_code=502, detail="Task created but idea sync failed in monarch-core")

    return {"task": task, "idea": idea_update}


@app.get("/hub/metrics")
async def hub_metrics(project_id: str | None = None, metric_name: str | None = None):
    params: dict[str, str] = {}
    if project_id:
        params["project_id"] = project_id
    if metric_name:
        params["metric_name"] = metric_name

    path = "/api/project-metrics"
    if params:
        path = f"{path}?{urlencode(params)}"

    payload = await _fetch_monarch_core_json(path)
    return payload or []


@app.post("/hub/metrics")
async def hub_create_metric(body: ProjectMetricCreateRequest):
    result = await _post_monarch_core_json("/api/project-metrics", body.model_dump(exclude_none=True))
    if not result:
        raise HTTPException(status_code=502, detail="Could not create metric in monarch-core")
    return result


@app.get("/hub/agents")
async def hub_agents(status: str | None = None, pipeline_name: str | None = None):
    params: dict[str, str] = {}
    if status:
        params["status"] = status
    if pipeline_name:
        params["pipeline_name"] = pipeline_name

    path = "/api/agent-profiles"
    if params:
        path = f"{path}?{urlencode(params)}"

    payload = await _fetch_monarch_core_json(path)
    return payload or []


@app.post("/hub/agents")
async def hub_create_agent(body: AgentProfileCreateRequest):
    result = await _post_monarch_core_json("/api/agent-profiles", body.model_dump(exclude_none=True))
    if not result:
        raise HTTPException(status_code=502, detail="Could not create agent profile in monarch-core")
    return result


@app.patch("/hub/agents/{agent_id}")
async def hub_update_agent(agent_id: str, body: AgentProfileUpdateRequest):
    payload = body.model_dump(exclude_none=True)
    if not payload:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await _patch_monarch_core_json(f"/api/agent-profiles/{agent_id}", payload)
    if not result:
        raise HTTPException(status_code=502, detail="Could not update agent profile in monarch-core")
    return result


@app.get("/hub/roadmap-items")
async def hub_roadmap_items(
    project_id: str | None = None,
    status: str | None = None,
    phase: str | None = None,
):
    params: dict[str, str] = {}
    if project_id:
        params["project_id"] = project_id
    if status:
        params["status"] = status
    if phase:
        params["phase"] = phase

    path = "/api/roadmap-items"
    if params:
        path = f"{path}?{urlencode(params)}"

    payload = await _fetch_monarch_core_json(path)
    return payload or []


@app.post("/hub/roadmap-items")
async def hub_create_roadmap_item(body: RoadmapItemCreateRequest):
    result = await _post_monarch_core_json("/api/roadmap-items", body.model_dump(exclude_none=True))
    if not result:
        raise HTTPException(status_code=502, detail="Could not create roadmap item in monarch-core")
    return result


@app.patch("/hub/roadmap-items/{item_id}")
async def hub_update_roadmap_item(item_id: str, body: RoadmapItemUpdateRequest):
    payload = body.model_dump(exclude_none=True)
    if not payload:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await _patch_monarch_core_json(f"/api/roadmap-items/{item_id}", payload)
    if not result:
        raise HTTPException(status_code=502, detail="Could not update roadmap item in monarch-core")
    return result


@app.get("/hub/tasks")
async def hub_tasks(
    status: str | None = None,
    project_id: str | None = None,
    priority: str | None = None,
):
    params: dict[str, str] = {}
    if status:
        params["status"] = status
    if project_id:
        params["project_id"] = project_id
    if priority:
        params["priority"] = priority

    path = "/api/tasks"
    if params:
        path = f"{path}?{urlencode(params)}"

    payload = await _fetch_monarch_core_json(path)
    return payload or []


@app.post("/hub/tasks")
async def hub_create_task(body: HubTaskCreateRequest):
    result = await _post_monarch_core_json("/api/tasks", body.model_dump(exclude_none=True))
    if not result:
        raise HTTPException(status_code=502, detail="Could not create task in monarch-core")
    return result


@app.patch("/hub/tasks/{task_id}")
async def hub_update_task(task_id: str, body: HubTaskUpdateRequest):
    payload = body.model_dump(exclude_none=True)
    if not payload:
        raise HTTPException(status_code=400, detail="No fields to update")

    result = await _patch_monarch_core_json(f"/api/tasks/{task_id}", payload)
    if not result:
        raise HTTPException(status_code=502, detail="Could not update task in monarch-core")
    return result


@app.get("/hub/approvals")
async def hub_approvals(status: str | None = None, project_id: str | None = None):
    params: dict[str, str] = {}
    if status:
        params["status"] = status
    if project_id:
        params["project_id"] = project_id

    path = "/api/approvals"
    if params:
        path = f"{path}?{urlencode(params)}"

    payload = await _fetch_monarch_core_json(path)
    return payload or []


@app.post("/hub/approvals/{approval_id}/approve")
async def hub_approve_approval(approval_id: str, body: HubApprovalDecisionRequest):
    result = await _post_monarch_core_json(f"/api/approvals/{approval_id}/approve", body.model_dump())
    if not result:
        raise HTTPException(status_code=502, detail="Could not approve in monarch-core")
    return result


@app.post("/hub/approvals/{approval_id}/reject")
async def hub_reject_approval(approval_id: str, body: HubApprovalDecisionRequest):
    result = await _post_monarch_core_json(f"/api/approvals/{approval_id}/reject", body.model_dump())
    if not result:
        raise HTTPException(status_code=502, detail="Could not reject in monarch-core")
    return result


# ------------------------------------------------------------------
# WebSocket — real-time task updates
# ------------------------------------------------------------------

@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    _ws_clients.append(ws)
    try:
        while True:
            await ws.receive_text()  # keep-alive ping support
    except WebSocketDisconnect:
        _ws_clients.remove(ws)


async def _broadcast(event: dict[str, Any]) -> None:
    dead: list[WebSocket] = []
    for ws in _ws_clients:
        try:
            await ws.send_text(json.dumps(event))
        except Exception:
            dead.append(ws)
    for ws in dead:
        _ws_clients.remove(ws)


async def _run_task_and_broadcast(task: Task) -> None:
    assert _orchestrator is not None
    await _broadcast({"type": "task_started", "task_id": task.task_id})
    try:
        result = await _orchestrator.run(task)
        await _broadcast({"type": "task_updated", "task": _task_to_dict(result)})
    except Exception as exc:
        logger.exception("Pipeline error for %s", task.task_id)
        await _broadcast({"type": "task_error", "task_id": task.task_id, "error": str(exc)})


def _task_to_dict(task: Task) -> dict[str, Any]:
    return {
        "task_id": task.task_id,
        "status": task.status.value,
        "raw_input": task.raw_input,
        "priority": task.priority,
        "branch_name": task.branch_name,
        "pr_url": task.pr_url,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
        "history": [
            {"agent": h.agent, "action": h.action, "detail": h.detail, "timestamp": h.timestamp.isoformat()}
            for h in task.history
        ],
    }
