import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.enums import EventStatus
from app.database.base import Base


class Event(Base):
    __tablename__ = "events"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    event_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    registration_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus), name="event_status_enum", nullable=False
    )
    number_of_visitors: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    status_changed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    place_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), ForeignKey("places.id"), nullable=False
    )

    place = relationship("Place", back_populates="events")
