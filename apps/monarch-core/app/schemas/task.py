from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TaskCreate(BaseModel):
    project_id: UUID
    title: str
    description: str | None = None
    task_type: str
    status: str = "todo"
    priority: str = "medium"
    owner_type: str = "agent"
    owner_name: str | None = None
    approval_required: bool = False
    due_at: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    task_type: str | None = None
    status: str | None = None
    priority: str | None = None
    owner_type: str | None = None
    owner_name: str | None = None
    approval_required: bool | None = None
    due_at: datetime | None = None


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    title: str
    description: str | None
    task_type: str
    status: str
    priority: str
    owner_type: str
    owner_name: str | None
    approval_required: bool
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime
