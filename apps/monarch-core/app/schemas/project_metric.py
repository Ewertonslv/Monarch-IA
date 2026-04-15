from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProjectMetricCreate(BaseModel):
    project_id: UUID
    metric_name: str
    metric_value: float
    metric_unit: str | None = None
    captured_at: datetime | None = None


class ProjectMetricRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    project_id: UUID
    metric_name: str
    metric_value: float
    metric_unit: str | None
    captured_at: datetime
    created_at: datetime
