from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.dashboard import ActivityItem, DashboardOverview
from app.services.dashboard_service import get_dashboard_activity, get_dashboard_overview

router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
async def dashboard_overview(db: AsyncSession = Depends(get_db_session)) -> DashboardOverview:
    return await get_dashboard_overview(db)


@router.get("/activity", response_model=list[ActivityItem])
async def dashboard_activity(db: AsyncSession = Depends(get_db_session)) -> list[ActivityItem]:
    return await get_dashboard_activity(db)
