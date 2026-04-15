from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.roadmap_item import RoadmapItem
from app.schemas.roadmap_item import RoadmapItemCreate, RoadmapItemUpdate


async def list_roadmap_items(
    db: AsyncSession,
    *,
    project_id: UUID | None = None,
    status_filter: str | None = None,
    phase: str | None = None,
) -> list[RoadmapItem]:
    query: Select[tuple[RoadmapItem]] = select(RoadmapItem)
    if project_id:
        query = query.where(RoadmapItem.project_id == project_id)
    if status_filter:
        query = query.where(RoadmapItem.status == status_filter)
    if phase:
        query = query.where(RoadmapItem.phase == phase)
    query = query.order_by(RoadmapItem.order_index.asc(), RoadmapItem.created_at.asc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_roadmap_item(db: AsyncSession, payload: RoadmapItemCreate) -> RoadmapItem:
    item = RoadmapItem(**payload.model_dump(exclude_none=True))
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def get_roadmap_item_by_id(db: AsyncSession, item_id: UUID) -> RoadmapItem | None:
    return await db.get(RoadmapItem, item_id)


async def update_roadmap_item(
    db: AsyncSession,
    item_id: UUID,
    payload: RoadmapItemUpdate,
) -> RoadmapItem | None:
    item = await db.get(RoadmapItem, item_id)
    if item is None:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.commit()
    await db.refresh(item)
    return item
