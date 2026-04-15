from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idea import Idea
from app.schemas.idea import IdeaCreate, IdeaUpdate


async def list_ideas(
    db: AsyncSession,
    *,
    status_filter: str | None = None,
    classification: str | None = None,
    business_unit_id: UUID | None = None,
    project_id: UUID | None = None,
) -> list[Idea]:
    query: Select[tuple[Idea]] = select(Idea)
    if status_filter:
        query = query.where(Idea.status == status_filter)
    if classification:
        query = query.where(Idea.classification == classification)
    if business_unit_id:
        query = query.where(Idea.business_unit_id == business_unit_id)
    if project_id:
        query = query.where(Idea.project_id == project_id)
    query = query.order_by(Idea.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_idea(db: AsyncSession, payload: IdeaCreate) -> Idea:
    idea = Idea(**payload.model_dump())
    db.add(idea)
    await db.commit()
    await db.refresh(idea)
    return idea


async def get_idea_by_id(db: AsyncSession, idea_id: UUID) -> Idea | None:
    return await db.get(Idea, idea_id)


async def update_idea(db: AsyncSession, idea_id: UUID, payload: IdeaUpdate) -> Idea | None:
    idea = await db.get(Idea, idea_id)
    if idea is None:
        return None

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(idea, field, value)

    await db.commit()
    await db.refresh(idea)
    return idea
