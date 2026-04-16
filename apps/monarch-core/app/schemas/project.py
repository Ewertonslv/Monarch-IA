from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectCreate(BaseModel):
    business_unit_id: UUID
    name: str
    slug: str
    description: str | None = None
    project_type: str
    status: str = "idea"
    priority: str = "medium"
    stage: str = "discovery"
    source_path: str | None = None
    repo_url: str | None = None
    main_goal: str | None = None
    current_focus: str | None = None
    next_action: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None
    priority: str | None = None
    stage: str | None = None
    current_focus: str | None = None
    next_action: str | None = None


class ProjectRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    business_unit_id: UUID
    name: str
    slug: str
    description: str | None
    project_type: str
    status: str
    priority: str
    stage: str
    source_path: str | None
    repo_url: str | None
    main_goal: str | None
    current_focus: str | None
    next_action: str | None
    created_at: datetime
    updated_at: datetime


class ProjectExecutionSummaryRead(BaseModel):
    readiness: int
    stage_label: str
    momentum: str
    roadmap_total: int
    roadmap_done: int
    tasks_total: int
    task_done: int
    task_active: int
    task_blocked: int
    pending_approvals: int
    failed_executions: int
    next_checkpoint: str


class ProjectImplementationSummaryRead(BaseModel):
    implementation_status: str
    canonical_path: str
    deliverable: str
    package_present: bool
    readme_present: bool
    test_suite_present: bool
    module_count: int
    module_labels: list[str]
