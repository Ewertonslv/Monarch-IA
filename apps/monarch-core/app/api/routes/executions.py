from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.execution import ExecutionCreate, ExecutionRead, ExecutionUpdate
from app.services import execution_service

router = APIRouter()


@router.get("", response_model=list[ExecutionRead])
async def list_executions(
    project_id: UUID | None = None,
    task_id: UUID | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    db: AsyncSession = Depends(get_db_session),
) -> list[ExecutionRead]:
    return await execution_service.list_executions(
        db,
        project_id=project_id,
        task_id=task_id,
        status_filter=status_filter,
    )


@router.post("", response_model=ExecutionRead, status_code=status.HTTP_201_CREATED)
async def create_execution(
    payload: ExecutionCreate,
    db: AsyncSession = Depends(get_db_session),
) -> ExecutionRead:
    return await execution_service.create_execution(db, payload)


@router.get("/{execution_id}", response_model=ExecutionRead)
async def get_execution(execution_id: UUID, db: AsyncSession = Depends(get_db_session)) -> ExecutionRead:
    execution = await execution_service.get_execution_by_id(db, execution_id)
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.patch("/{execution_id}", response_model=ExecutionRead)
async def update_execution(
    execution_id: UUID,
    payload: ExecutionUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> ExecutionRead:
    execution = await execution_service.update_execution(db, execution_id, payload)
    if execution is None:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution
