from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class AgentProfileCreate(BaseModel):
    name: str
    slug: str
    role: str
    capabilities: str | None = None
    pipeline_name: str | None = None
    status: str = "active"
    notes: str | None = None


class AgentProfileUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    role: str | None = None
    capabilities: str | None = None
    pipeline_name: str | None = None
    status: str | None = None
    notes: str | None = None


class AgentProfileRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    role: str
    capabilities: str | None
    pipeline_name: str | None
    status: str
    notes: str | None
    created_at: datetime
    updated_at: datetime
