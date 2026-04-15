from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
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
