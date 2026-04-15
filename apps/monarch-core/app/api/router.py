from fastapi import APIRouter, Depends

from app.api.deps import require_api_key
from app.api.routes import (
    agent_profiles,
    approvals,
    business_units,
    dashboard,
    executions,
    ideas,
    project_metrics,
    projects,
    roadmap_items,
    tasks,
)

api_router = APIRouter(dependencies=[Depends(require_api_key)])
api_router.include_router(business_units.router, prefix="/business-units", tags=["business-units"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(project_metrics.router, prefix="/project-metrics", tags=["project-metrics"])
api_router.include_router(ideas.router, prefix="/ideas", tags=["ideas"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(executions.router, prefix="/executions", tags=["executions"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(agent_profiles.router, prefix="/agent-profiles", tags=["agent-profiles"])
api_router.include_router(roadmap_items.router, prefix="/roadmap-items", tags=["roadmap-items"])
