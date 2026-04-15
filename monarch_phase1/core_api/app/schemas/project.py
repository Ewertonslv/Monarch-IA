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
