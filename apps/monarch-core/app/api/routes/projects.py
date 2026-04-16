from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.project import (
    ProjectCreate,
    ProjectExecutionSummaryRead,
    ProjectImplementationSummaryRead,
    ProjectRead,
    ProjectUpdate,
)
from app.services import project_service

router = APIRouter()


@router.get("", response_model=list[ProjectRead])
async def list_projects(
    status_filter: str | None = Query(default=None, alias="status"),
    business_unit_id: UUID | None = None,
    priority: str | None = None,
    slug: str | None = None,
    db: AsyncSession = Depends(get_db_session),
) -> list[ProjectRead]:
    return await project_service.list_projects(
        db,
        status_filter=status_filter,
        business_unit_id=business_unit_id,
        priority=priority,
        slug=slug,
    )


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    payload: ProjectCreate,
    db: AsyncSession = Depends(get_db_session),
) -> ProjectRead:
    return await project_service.create_project(db, payload)


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(project_id: UUID, db: AsyncSession = Depends(get_db_session)) -> ProjectRead:
    project = await project_service.get_project_by_id(db, project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/execution-summary", response_model=ProjectExecutionSummaryRead)
async def get_project_execution_summary(
    project_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> ProjectExecutionSummaryRead:
    summary = await project_service.get_project_execution_summary(db, project_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectExecutionSummaryRead(**summary)


@router.get("/{project_id}/implementation-summary", response_model=ProjectImplementationSummaryRead)
async def get_project_implementation_summary(
    project_id: UUID,
    db: AsyncSession = Depends(get_db_session),
) -> ProjectImplementationSummaryRead:
    summary = await project_service.get_project_implementation_summary(db, project_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return ProjectImplementationSummaryRead(**summary)


@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    project_id: UUID,
    payload: ProjectUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> ProjectRead:
    project = await project_service.update_project(db, project_id, payload)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project
