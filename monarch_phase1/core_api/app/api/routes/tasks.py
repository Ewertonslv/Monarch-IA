from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate
from app.services import task_service

router = APIRouter()


@router.get("", response_model=list[TaskRead])
async def list_tasks(
    status_filter: str | None = Query(default=None, alias="status"),
    project_id: UUID | None = None,
    priority: str | None = None,
    db: AsyncSession = Depends(get_db_session),
) -> list[TaskRead]:
    return await task_service.list_tasks(
        db,
        status_filter=status_filter,
        project_id=project_id,
        priority=priority,
    )


@router.post("", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(payload: TaskCreate, db: AsyncSession = Depends(get_db_session)) -> TaskRead:
    return await task_service.create_task(db, payload)


@router.get("/{task_id}", response_model=TaskRead)
async def get_task(task_id: UUID, db: AsyncSession = Depends(get_db_session)) -> TaskRead:
    task = await task_service.get_task_by_id(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: UUID,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> TaskRead:
    task = await task_service.update_task(db, task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
