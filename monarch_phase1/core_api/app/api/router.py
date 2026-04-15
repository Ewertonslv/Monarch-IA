from fastapi import APIRouter

from app.api.routes import approvals, business_units, dashboard, executions, ideas, project_metrics, projects, tasks

api_router = APIRouter()
api_router.include_router(business_units.router, prefix="/business-units", tags=["business-units"])
api_router.include_router(projects.router, prefix="/projects", tags=["projects"])
api_router.include_router(project_metrics.router, prefix="/project-metrics", tags=["project-metrics"])
api_router.include_router(ideas.router, prefix="/ideas", tags=["ideas"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["tasks"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["approvals"])
api_router.include_router(executions.router, prefix="/executions", tags=["executions"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
