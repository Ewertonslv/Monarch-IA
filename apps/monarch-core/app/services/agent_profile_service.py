from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agent_profile import AgentProfile
from app.schemas.agent_profile import AgentProfileCreate, AgentProfileUpdate


async def list_agent_profiles(
    db: AsyncSession,
    *,
    status_filter: str | None = None,
    pipeline_name: str | None = None,
) -> list[AgentProfile]:
    query: Select[tuple[AgentProfile]] = select(AgentProfile)
    if status_filter:
        query = query.where(AgentProfile.status == status_filter)
    if pipeline_name:
        query = query.where(AgentProfile.pipeline_name == pipeline_name)
    query = query.order_by(AgentProfile.updated_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_agent_profile(db: AsyncSession, payload: AgentProfileCreate) -> AgentProfile:
    profile = AgentProfile(**payload.model_dump(exclude_none=True))
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile


async def get_agent_profile_by_id(db: AsyncSession, profile_id: UUID) -> AgentProfile | None:
    return await db.get(AgentProfile, profile_id)


async def update_agent_profile(
    db: AsyncSession,
    profile_id: UUID,
    payload: AgentProfileUpdate,
) -> AgentProfile | None:
    profile = await db.get(AgentProfile, profile_id)
    if profile is None:
        return None
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await db.commit()
    await db.refresh(profile)
    return profile
