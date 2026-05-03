from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.idempotency import Idempotency


class IdempotencyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_key(self, key: str):
        stmt = select(Idempotency).where(Idempotency.idempotency_key == key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(self, data: dict):
        idempotency = Idempotency(**data)
        self.session.add(idempotency)
        await self.session.flush()
        return idempotency
