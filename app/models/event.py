import uuid

from sqlalchemy import UUID, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.base import Base


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    event_time = Column(DateTime(timezone=True), nullable=False)
    registration_deadline = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(50), default="published")
    number_of_visitors = Column(Integer, default=0)
    changed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True))
    status_changed_at = Column(DateTime(timezone=True))

    place_id = Column(UUID(as_uuid=True), ForeignKey("places.id"), nullable=False)

    place = relationship("Place", back_populates="events")
