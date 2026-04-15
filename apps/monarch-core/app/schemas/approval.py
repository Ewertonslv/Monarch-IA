from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ApprovalCreate(BaseModel):
    project_id: UUID
    task_id: UUID | None = None
    title: str
    summary: str | None = None
    status: str = "pending"


class ApprovalDecision(BaseModel):
    decided_by: str


class ApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    task_id: UUID | None
    title: str
    summary: str | None
    status: str
    decision: str | None
    decided_by: str | None
    decided_at: datetime | None
    created_at: datetime
