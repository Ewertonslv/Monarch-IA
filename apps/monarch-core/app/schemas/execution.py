from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExecutionCreate(BaseModel):
    project_id: UUID
    task_id: UUID | None = None
    agent_name: str
    execution_type: str
    status: str
    input_payload: str | None = None
    output_summary: str | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


class ExecutionUpdate(BaseModel):
    status: str | None = None
    output_summary: str | None = None
    error_message: str | None = None
    finished_at: datetime | None = None


class ExecutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    task_id: UUID | None
    agent_name: str
    execution_type: str
    status: str
    input_payload: str | None
    output_summary: str | None
    error_message: str | None
    started_at: datetime | None
    finished_at: datetime | None
    created_at: datetime
