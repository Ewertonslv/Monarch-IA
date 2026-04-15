from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.execution import Execution
from app.schemas.execution import ExecutionCreate, ExecutionUpdate


async def list_executions(
    db: AsyncSession,
    *,
    project_id=None,
    task_id=None,
    status_filter: str | None = None,
) -> list[Execution]:
    query: Select[tuple[Execution]] = select(Execution)
    if project_id:
        query = query.where(Execution.project_id == project_id)
    if task_id:
        query = query.where(Execution.task_id == task_id)
    if status_filter:
        query = query.where(Execution.status == status_filter)
    query = query.order_by(Execution.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_execution(db: AsyncSession, payload: ExecutionCreate) -> Execution:
    execution = Execution(**payload.model_dump())
    db.add(execution)
    await db.commit()
    await db.refresh(execution)
    return execution


async def get_execution_by_id(db: AsyncSession, execution_id) -> Execution | None:
    return await db.get(Execution, execution_id)


async def update_execution(db: AsyncSession, execution_id, payload: ExecutionUpdate) -> Execution | None:
    execution = await db.get(Execution, execution_id)
    if execution is None:
        return None

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(execution, field, value)

    await db.commit()
    await db.refresh(execution)
    return execution
