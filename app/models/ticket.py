
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from app.database.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True)
    event_id = Column(UUID(as_uuid=True), ForeignKey("events.id"), nullable=False)

    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    seat = Column(String(10), nullable=False)
    email = Column(String(255), nullable=False)
