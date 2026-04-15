from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IdeaCreate(BaseModel):
    title: str
    raw_input: str
    source: str = "manual"
    classification: str | None = None
    business_unit_id: UUID | None = None
    project_id: UUID | None = None
    priority_score: float | None = None


class IdeaUpdate(BaseModel):
    title: str | None = None
    raw_input: str | None = None
    status: str | None = None
    classification: str | None = None
    business_unit_id: UUID | None = None
    project_id: UUID | None = None
    priority_score: float | None = None


class IdeaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    raw_input: str
    source: str
    status: str
    classification: str | None
    business_unit_id: UUID | None
    project_id: UUID | None
    priority_score: float | None
    created_at: datetime
    updated_at: datetime
