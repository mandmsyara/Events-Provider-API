from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.models.event import Event
from app.models.place import Place


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
