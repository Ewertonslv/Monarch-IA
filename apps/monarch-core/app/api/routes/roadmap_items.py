from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.roadmap_item import RoadmapItemCreate, RoadmapItemRead, RoadmapItemUpdate
from app.services import roadmap_item_service

router = APIRouter()


@router.get("", response_model=list[RoadmapItemRead])
async def list_roadmap_items(
    project_id: UUID | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    phase: str | None = None,
    db: AsyncSession = Depends(get_db_session),
) -> list[RoadmapItemRead]:
    return await roadmap_item_service.list_roadmap_items(
        db,
        project_id=project_id,
        status_filter=status_filter,
        phase=phase,
    )


@router.post("", response_model=RoadmapItemRead, status_code=status.HTTP_201_CREATED)
async def create_roadmap_item(
    payload: RoadmapItemCreate,
    db: AsyncSession = Depends(get_db_session),
) -> RoadmapItemRead:
    return await roadmap_item_service.create_roadmap_item(db, payload)


@router.get("/{item_id}", response_model=RoadmapItemRead)
async def get_roadmap_item(item_id: UUID, db: AsyncSession = Depends(get_db_session)) -> RoadmapItemRead:
    item = await roadmap_item_service.get_roadmap_item_by_id(db, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Roadmap item not found")
    return item


@router.patch("/{item_id}", response_model=RoadmapItemRead)
async def update_roadmap_item(
    item_id: UUID,
    payload: RoadmapItemUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> RoadmapItemRead:
    item = await roadmap_item_service.update_roadmap_item(db, item_id, payload)
    if item is None:
        raise HTTPException(status_code=404, detail="Roadmap item not found")
    return item
