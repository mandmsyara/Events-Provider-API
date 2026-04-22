from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.sync_state import SyncState


class SyncStateRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_state(self) -> SyncState | None:
        stmt = select(SyncState).where(SyncState.id == 1)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_or_create(self) -> SyncState:
        state = await self.get_state()
        if state:
            return state

        state = SyncState(id=1, sync_status="idle")
        self.session.add(state)
        await self.session.flush()
        return state

    async def mark_running(self) -> SyncState:
        state = await self.get_or_create()
        state.sync_status = "running"
        await self.session.flush()
        return state

    async def mark_success(self, last_changed_at: datetime | None) -> SyncState:
        state = await self.get_or_create()
        state.sync_status = "succes"
        state.last_sync_time = datetime.now(timezone.utc)

        if last_changed_at is not None:
            state.last_changed_at = last_changed_at
        await self.session.flush()
        return state

    async def mark_failed(self) -> SyncState:
        state = await self.get_or_create()
        state.sync_status = "failed"
        state.last_sync_time = datetime.now(timezone.utc)
        await self.session.flush()
        return state
