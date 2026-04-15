from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


async def list_tasks(
    db: AsyncSession,
    *,
    status_filter: str | None = None,
    project_id: UUID | None = None,
    priority: str | None = None,
) -> list[Task]:
    query: Select[tuple[Task]] = select(Task)
    if status_filter:
        query = query.where(Task.status == status_filter)
    if project_id:
        query = query.where(Task.project_id == project_id)
    if priority:
        query = query.where(Task.priority == priority)
    query = query.order_by(Task.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_task(db: AsyncSession, payload: TaskCreate) -> Task:
    task = Task(**payload.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task_by_id(db: AsyncSession, task_id: UUID) -> Task | None:
    return await db.get(Task, task_id)


async def update_task(db: AsyncSession, task_id: UUID, payload: TaskUpdate) -> Task | None:
    task = await db.get(Task, task_id)
    if task is None:
        return None

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task
