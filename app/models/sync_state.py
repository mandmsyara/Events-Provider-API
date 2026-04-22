from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.sql import func

from app.database.base import Base


class SyncState(Base):
    __tablename__ = "sync_state"

    id = Column(Integer, primary_key=True)
    last_sync_time = Column(DateTime(timezone=True), nullable=False)
    last_changed_at = Column(DateTime(timezone=True), nullable=False)
    sync_status = Column(String(255), nullable=False, default="idle")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
