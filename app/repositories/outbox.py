from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.outbox import Outbox
from app.core.enums import OutboxStatus


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict):
        outbox = Outbox(**data)
        self.session.add(outbox)
        await self.session.flush()
        return outbox

    async def get_pending(self, limit: int = 10):
        stmt = (
            select(Outbox)
            .where(Outbox.outbox_status == OutboxStatus.PENDING)
            .order_by(Outbox.created_at)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_by_id(self, outbox_id):
        stmt = select(Outbox).where(Outbox.id == outbox_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def mark_as_sent(self, outbox_id):
        outbox = await self.get_by_id(outbox_id=outbox_id)
        if outbox is None:
            return None

        outbox.outbox_status = OutboxStatus.SENT
        await self.session.flush()
        return outbox
