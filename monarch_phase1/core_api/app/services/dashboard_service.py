from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.approval import Approval
from app.models.business_unit import BusinessUnit
from app.models.execution import Execution
from app.models.idea import Idea
from app.models.project import Project
from app.models.task import Task
from app.schemas.dashboard import ActivityItem, DashboardOverview


async def _count_rows(db: AsyncSession, statement) -> int:
    result = await db.execute(statement)
    count = result.scalar_one()
    return int(count or 0)


async def get_dashboard_overview(db: AsyncSession) -> DashboardOverview:
    return DashboardOverview(
        business_units_count=await _count_rows(db, select(func.count(BusinessUnit.id))),
        projects_count=await _count_rows(db, select(func.count(Project.id))),
        active_projects_count=await _count_rows(
            db,
            select(func.count(Project.id)).where(Project.status == "active"),
        ),
        incubating_projects_count=await _count_rows(
            db,
            select(func.count(Project.id)).where(Project.status == "incubating"),
        ),
        open_ideas_count=await _count_rows(
            db,
            select(func.count(Idea.id)).where(Idea.status.in_(["new", "reviewing"])),
        ),
        high_priority_projects_count=await _count_rows(
            db,
            select(func.count(Project.id)).where(Project.priority.in_(["high", "critical"])),
        ),
        open_tasks_count=await _count_rows(
            db,
            select(func.count(Task.id)).where(Task.status.in_(["todo", "in_progress", "blocked"])),
        ),
        pending_approvals_count=await _count_rows(
            db,
            select(func.count(Approval.id)).where(Approval.status == "pending"),
        ),
    )


async def get_dashboard_activity(db: AsyncSession, *, limit: int = 20) -> list[ActivityItem]:
    result = await db.execute(select(Execution).order_by(Execution.created_at.desc()).limit(limit))
    items = result.scalars().all()
    return [
        ActivityItem(
            id=str(item.id),
            project_id=str(item.project_id),
            task_id=str(item.task_id) if item.task_id else None,
            agent_name=item.agent_name,
            execution_type=item.execution_type,
            status=item.status,
            output_summary=item.output_summary,
            error_message=item.error_message,
            started_at=item.started_at.isoformat() if item.started_at else None,
            finished_at=item.finished_at.isoformat() if item.finished_at else None,
            created_at=item.created_at.isoformat(),
        )
        for item in items
    ]
