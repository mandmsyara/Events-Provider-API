from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional

from app.schemas.place_schema import PlaceRead


class EventBase(BaseModel):
    name: str
    event_time: datetime
    registrtion_deadline: datetime
    status: str = "published"
    number_of_visitors: int = 0


class EventCreate(EventBase):
    place_id: UUID


class EventRead(EventBase):
    id: UUID
    changed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    status_changed_at: Optional[datetime] = None

    place: PlaceRead

    model_config = ConfigDict(from_attributes=True)


class EventListResponse(BaseModel):
    next: str | None
    previous: str | None
    results: list[EventRead]
