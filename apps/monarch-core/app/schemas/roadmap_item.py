from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RoadmapItemCreate(BaseModel):
    project_id: UUID
    title: str
    description: str | None = None
    phase: str = "backlog"
    status: str = "planned"
    priority: str = "medium"
    order_index: int = 0
    due_at: datetime | None = None


class RoadmapItemUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    phase: str | None = None
    status: str | None = None
    priority: str | None = None
    order_index: int | None = None
    due_at: datetime | None = None


class RoadmapItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    title: str
    description: str | None
    phase: str
    status: str
    priority: str
    order_index: int
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime
