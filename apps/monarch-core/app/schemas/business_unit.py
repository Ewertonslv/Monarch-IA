from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class BusinessUnitBase(BaseModel):
    name: str
    slug: str
    description: str | None = None
    status: str = "active"


class BusinessUnitCreate(BusinessUnitBase):
    pass


class BusinessUnitUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    description: str | None = None
    status: str | None = None


class BusinessUnitRead(BusinessUnitBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    created_at: datetime
    updated_at: datetime
