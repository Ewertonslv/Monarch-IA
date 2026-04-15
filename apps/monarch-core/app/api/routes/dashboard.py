from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.dashboard import ActivityItem, DashboardOverview, PerformanceItem
from app.services.dashboard_service import get_dashboard_activity, get_dashboard_overview, get_dashboard_performance

router = APIRouter()


@router.get("/overview", response_model=DashboardOverview)
async def dashboard_overview(db: AsyncSession = Depends(get_db_session)) -> DashboardOverview:
    return await get_dashboard_overview(db)


@router.get("/activity", response_model=list[ActivityItem])
async def dashboard_activity(
    db: AsyncSession = Depends(get_db_session),
    limit: int = 20,
    project_id: UUID | None = None,
    agent_name: str | None = None,
    status: str | None = None,
    execution_type: str | None = None,
) -> list[ActivityItem]:
    return await get_dashboard_activity(
        db,
        limit=limit,
        project_id=project_id,
        agent_name=agent_name,
        status_filter=status,
        execution_type=execution_type,
    )


@router.get("/performance", response_model=list[PerformanceItem])
async def dashboard_performance(
    db: AsyncSession = Depends(get_db_session),
    business_unit_id: UUID | None = None,
    metric_name: str | None = None,
    limit: int = 50,
) -> list[PerformanceItem]:
    return await get_dashboard_performance(
        db,
        business_unit_id=business_unit_id,
        metric_name=metric_name,
        limit=limit,
    )
