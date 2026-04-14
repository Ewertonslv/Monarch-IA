import asyncio
import json
import logging
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _db, _orchestrator
    _db = Database(config.database_url)
    await _db.init()
    _orchestrator = Orchestrator(_db)
    logger.info("Monarch AI web interface ready")
    yield
    if _db:
        await _db.close()


app = FastAPI(title="Monarch AI", lifespan=lifespan)

import os
_templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=_templates_dir)


# ------------------------------------------------------------------
# REST endpoints
# ------------------------------------------------------------------

class TaskRequest(BaseModel):
    raw_input: str


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


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
