from datetime import date
from sqlalchemy import select, func
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

        stmt = stmt.on_conflict_do_update(
            index_elements=["id"],
            set_={k: v for k, v in event_data.items() if k != "id"},
        )

        await self.session.execute(stmt)

    async def get_all_events(
        self, page: int = 1, page_size: int = 20, date_from: date | None = None
    ):
        stmt = select(Event).options(joinedload(Event.place))
        if date_from:
            stmt = stmt.where(Event.event_time >= date_from)

        stmt = stmt.limit(page_size).offset((page - 1) * page_size)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def count_events(self, date_from: date | None = None) -> int:
        stmt = select(func.count()).select_from(Event)

        if date_from:
            stmt = stmt.where(Event.event_time >= date_from)

        results = await self.session.execute(stmt)
        return results.scalar_one()

    async def get_events_by_id(self, event_id: uuid.UUID):
        stmt = (
            select(Event).where(Event.id == event_id).options(joinedload(Event.place))
        )
        result = await self.session.execute(stmt)

        return result.scalar_one_or_none()
