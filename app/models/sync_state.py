from datetime import datetime

from sqlalchemy import DateTime, Enum, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.enums import SyncStatus
from app.database.base import Base


class SyncState(Base):
    __tablename__ = "sync_state"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    last_sync_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    last_changed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sync_status: Mapped[SyncStatus] = mapped_column(
        Enum(SyncStatus), nullable=False, default=SyncStatus.IDLE
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
