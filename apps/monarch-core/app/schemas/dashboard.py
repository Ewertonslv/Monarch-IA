from pydantic import BaseModel


class ActivityItem(BaseModel):
    id: str
    project_id: str
    task_id: str | None
    agent_name: str
    execution_type: str
    status: str
    output_summary: str | None
    error_message: str | None
    started_at: str | None
    finished_at: str | None
    created_at: str


class DashboardOverview(BaseModel):
    business_units_count: int
    projects_count: int
    active_projects_count: int
    incubating_projects_count: int
    open_ideas_count: int
    high_priority_projects_count: int
    open_tasks_count: int
    pending_approvals_count: int


class PerformanceItem(BaseModel):
    project_id: str
    project_name: str
    business_unit_id: str
    metric_name: str
    latest_value: float
    latest_unit: str | None
    latest_captured_at: str
