from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models.event import Event
from app.models.place import Place
import uuid


class EventRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def upsert_place(self, place_data: dict):
        stmt = insert(Place).values(**place_data)

        stmt = stmt.on_conflict_do_update(index_elements=["id"], set_=place_data)

        await self.session.execute(stmt)

    async def upsert_event(self, event_data: dict):
        stmt = insert(Event).values(**event_data)

        stmt = stmt.on_conflict_do_update(index_elements=["id"], set_=event_data)

        await self.session.execute(stmt)

    async def get_all_events(self, limit: int = 100, offset: int = 0):
        stmt = (
            select(Event).options(joinedload(Event.place)).limit(limit).offset(offset)
        )

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def get_events_by_id(self, event_id: uuid.UUID):
        stmt = (
            select(Event).where(Event.id == event_id).options(joinedload(Event.place))
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
