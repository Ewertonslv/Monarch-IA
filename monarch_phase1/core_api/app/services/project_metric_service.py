from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project_metric import ProjectMetric
from app.schemas.project_metric import ProjectMetricCreate


async def list_project_metrics(
    db: AsyncSession,
    *,
    project_id: UUID | None = None,
    metric_name: str | None = None,
) -> list[ProjectMetric]:
    query: Select[tuple[ProjectMetric]] = select(ProjectMetric)
    if project_id:
        query = query.where(ProjectMetric.project_id == project_id)
    if metric_name:
        query = query.where(ProjectMetric.metric_name == metric_name)
    query = query.order_by(ProjectMetric.captured_at.desc(), ProjectMetric.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_project_metric(db: AsyncSession, payload: ProjectMetricCreate) -> ProjectMetric:
    metric = ProjectMetric(**payload.model_dump(exclude_none=True))
    db.add(metric)
    await db.commit()
    await db.refresh(metric)
    return metric
