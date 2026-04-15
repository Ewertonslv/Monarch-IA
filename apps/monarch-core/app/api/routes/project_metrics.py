from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.project_metric import ProjectMetricCreate, ProjectMetricRead
from app.services import project_metric_service

router = APIRouter()


@router.get("", response_model=list[ProjectMetricRead])
async def list_project_metrics(
    project_id: UUID | None = None,
    metric_name: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db_session),
) -> list[ProjectMetricRead]:
    return await project_metric_service.list_project_metrics(
        db,
        project_id=project_id,
        metric_name=metric_name,
    )


@router.post("", response_model=ProjectMetricRead, status_code=status.HTTP_201_CREATED)
async def create_project_metric(
    payload: ProjectMetricCreate,
    db: AsyncSession = Depends(get_db_session),
) -> ProjectMetricRead:
    return await project_metric_service.create_project_metric(db, payload)
