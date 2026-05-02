from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum, Index, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.enums import OutboxStatus
from app.database.base import Base


class Outbox(Base):
    __tablename__ = "outbox"

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), nullable=False, primary_key=True, default=uuid4
    )
    event_type: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    outbox_status: Mapped[OutboxStatus] = mapped_column(
        Enum(OutboxStatus, name="outbox_status"),
        nullable=False,
        default=OutboxStatus.PENDING,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    __table_args__ = (Index("ix_outbox_status", "outbox_status"),)
