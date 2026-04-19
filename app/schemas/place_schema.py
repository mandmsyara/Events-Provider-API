from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime


class PlaceBase(BaseModel):
    name: str
    city: str
    address: str
    seats_pattern: str | None = None


class PlaceCreate(PlaceBase):
    pass


class PlaceRead(PlaceBase):
    id: UUID
    created_at: datetime
    changed_at: datetime

    model_config = ConfigDict(from_attributes=True)
