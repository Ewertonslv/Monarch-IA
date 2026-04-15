from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.idea import IdeaCreate, IdeaRead, IdeaUpdate
from app.services import idea_service

router = APIRouter()


@router.get("", response_model=list[IdeaRead])
async def list_ideas(
    status_filter: str | None = Query(default=None, alias="status"),
    classification: str | None = None,
    business_unit_id: UUID | None = None,
    project_id: UUID | None = None,
    db: AsyncSession = Depends(get_db_session),
) -> list[IdeaRead]:
    return await idea_service.list_ideas(
        db,
        status_filter=status_filter,
        classification=classification,
        business_unit_id=business_unit_id,
        project_id=project_id,
    )


@router.post("", response_model=IdeaRead, status_code=status.HTTP_201_CREATED)
async def create_idea(payload: IdeaCreate, db: AsyncSession = Depends(get_db_session)) -> IdeaRead:
    return await idea_service.create_idea(db, payload)


@router.get("/{idea_id}", response_model=IdeaRead)
async def get_idea(idea_id: UUID, db: AsyncSession = Depends(get_db_session)) -> IdeaRead:
    idea = await idea_service.get_idea_by_id(db, idea_id)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea


@router.patch("/{idea_id}", response_model=IdeaRead)
async def update_idea(
    idea_id: UUID,
    payload: IdeaUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> IdeaRead:
    idea = await idea_service.update_idea(db, idea_id, payload)
    if idea is None:
        raise HTTPException(status_code=404, detail="Idea not found")
    return idea
