from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.agent_profile import AgentProfileCreate, AgentProfileRead, AgentProfileUpdate
from app.services import agent_profile_service

router = APIRouter()


@router.get("", response_model=list[AgentProfileRead])
async def list_agent_profiles(
    status_filter: str | None = Query(default=None, alias="status"),
    pipeline_name: str | None = None,
    db: AsyncSession = Depends(get_db_session),
) -> list[AgentProfileRead]:
    return await agent_profile_service.list_agent_profiles(
        db,
        status_filter=status_filter,
        pipeline_name=pipeline_name,
    )


@router.post("", response_model=AgentProfileRead, status_code=status.HTTP_201_CREATED)
async def create_agent_profile(
    payload: AgentProfileCreate,
    db: AsyncSession = Depends(get_db_session),
) -> AgentProfileRead:
    return await agent_profile_service.create_agent_profile(db, payload)


@router.get("/{profile_id}", response_model=AgentProfileRead)
async def get_agent_profile(profile_id: UUID, db: AsyncSession = Depends(get_db_session)) -> AgentProfileRead:
    profile = await agent_profile_service.get_agent_profile_by_id(db, profile_id)
    if profile is None:
        raise HTTPException(status_code=404, detail="Agent profile not found")
    return profile


@router.patch("/{profile_id}", response_model=AgentProfileRead)
async def update_agent_profile(
    profile_id: UUID,
    payload: AgentProfileUpdate,
    db: AsyncSession = Depends(get_db_session),
) -> AgentProfileRead:
    profile = await agent_profile_service.update_agent_profile(db, profile_id, payload)
    if profile is None:
        raise HTTPException(status_code=404, detail="Agent profile not found")
    return profile
