from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import Approval
from app.models.execution import Execution
from app.models.project import Project
from app.models.roadmap_item import RoadmapItem
from app.models.task import Task
from app.schemas.project import ProjectCreate, ProjectUpdate


async def list_projects(
    db: AsyncSession,
    *,
    status_filter: str | None = None,
    business_unit_id: UUID | None = None,
    priority: str | None = None,
    slug: str | None = None,
) -> list[Project]:
    query: Select[tuple[Project]] = select(Project)
    if status_filter:
        query = query.where(Project.status == status_filter)
    if business_unit_id:
        query = query.where(Project.business_unit_id == business_unit_id)
    if priority:
        query = query.where(Project.priority == priority)
    if slug:
        query = query.where(Project.slug == slug)
    query = query.order_by(Project.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_project(db: AsyncSession, payload: ProjectCreate) -> Project:
    project = Project(**payload.model_dump())
    db.add(project)
    await db.commit()
    await db.refresh(project)
    return project


async def get_project_by_id(db: AsyncSession, project_id: UUID) -> Project | None:
    return await db.get(Project, project_id)


async def update_project(db: AsyncSession, project_id: UUID, payload: ProjectUpdate) -> Project | None:
    project = await db.get(Project, project_id)
    if project is None:
        return None

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(project, field, value)

    await db.commit()
    await db.refresh(project)
    return project


def _normalize_stage(stage: str | None) -> tuple[str, int]:
    mapping = {
        "discovery": ("Descoberta", 15),
        "planning": ("Planejamento", 35),
        "building": ("Construcao", 60),
        "testing": ("Validacao", 80),
        "active": ("Operacao", 100),
    }
    return mapping.get(stage or "", (stage or "Indefinido", 20))


async def get_project_execution_summary(db: AsyncSession, project_id: UUID) -> dict[str, int | str] | None:
    project = await db.get(Project, project_id)
    if project is None:
        return None

    task_result = await db.execute(select(Task).where(Task.project_id == project_id))
    approval_result = await db.execute(select(Approval).where(Approval.project_id == project_id))
    execution_result = await db.execute(select(Execution).where(Execution.project_id == project_id))
    roadmap_result = await db.execute(select(RoadmapItem).where(RoadmapItem.project_id == project_id))

    tasks = list(task_result.scalars().all())
    approvals = list(approval_result.scalars().all())
    executions = list(execution_result.scalars().all())
    roadmap_items = list(roadmap_result.scalars().all())

    roadmap_done = sum(
        1 for item in roadmap_items if (item.status or "").lower() in {"done", "completed", "shipped"}
    )
    task_done = sum(1 for item in tasks if item.status == "done")
    task_active = sum(1 for item in tasks if item.status == "in_progress")
    task_blocked = sum(1 for item in tasks if item.status == "blocked")
    pending_approvals = sum(1 for item in approvals if item.status == "pending")
    failed_executions = sum(1 for item in executions if item.status == "failed")

    stage_label, stage_score = _normalize_stage(project.stage)
    completion_base = round((roadmap_done / len(roadmap_items)) * 100) if roadmap_items else stage_score
    status_boost = 10 if project.status == "active" else 0 if project.status == "incubating" else -5
    risk_penalty = (task_blocked * 10) + (pending_approvals * 6) + (failed_executions * 12)
    readiness = max(0, min(100, completion_base + status_boost - risk_penalty))

    momentum = "Estruturando"
    if readiness >= 85:
        momentum = "Quase pronto"
    elif readiness >= 65:
        momentum = "Executando"
    elif readiness >= 40:
        momentum = "Ganhando forma"

    next_open_roadmap = next(
        (
            item for item in sorted(roadmap_items, key=lambda value: value.order_index)
            if (item.status or "").lower() not in {"done", "completed", "shipped"}
        ),
        None,
    )

    return {
        "readiness": readiness,
        "stage_label": stage_label,
        "momentum": momentum,
        "roadmap_total": len(roadmap_items),
        "roadmap_done": roadmap_done,
        "tasks_total": len(tasks),
        "task_done": task_done,
        "task_active": task_active,
        "task_blocked": task_blocked,
        "pending_approvals": pending_approvals,
        "failed_executions": failed_executions,
        "next_checkpoint": (
            next_open_roadmap.title
            if next_open_roadmap
            else project.next_action or "Definir proxima entrega"
        ),
    }
