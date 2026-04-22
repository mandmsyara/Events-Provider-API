from datetime import date
from uuid import UUID

from app.repositories.events import EventRepository
from app.exception.exceptions import EventNotFoundError


class EventQueryService:
    def __init__(self, repo: EventRepository):
        self.repo = repo

    async def get_events(
        self,
        page: int = 1,
        page_size: int = 20,
        date_from: date | None = None,
    ):

        count = await self.repo.count_events(date_from=date_from)
        events = await self.repo.get_all_events(
            page=page, page_size=page_size, date_from=date_from
        )

        next_url = None
        previous_url = None

        if page * page_size < count:
            next_url = f"/api/events/?page={page+1}&page_size={page_size}"
            if date_from:
                next_url += f"&date_from={date_from}"

        if page > 1:
            previous_url = f"/api/events/?page={page - 1}&page_size={page_size}"
            if date_from:
                previous_url += f"&date_from={date_from}"

        return {
            "count": count,
            "next": next_url,
            "previous": previous_url,
            "results": events,
        }

    async def get_event(self, event_id: UUID):
        event = await self.repo.get_events_by_id(event_id)

        if not event:
            raise EventNotFoundError()
        return event
