from app.clients.events_provider import EventsProviderClient
from app.repositories.events import EventRepository
from app.exception.exceptions import EventNotAvailableError, EventNotFoundError
from app.core.enums import EventStatus


class SeatsService:
    def __init__(self, client: EventsProviderClient, repo: EventRepository):
        self.client = client
        self.repo = repo

    async def get_available_seats(self, event_id):
        event = await self.repo.get_events_by_id(event_id)

        if not event:
            raise EventNotFoundError()

        if event.status != EventStatus.PUBLISHED:
            raise EventNotAvailableError()

        seats = await self.client.get_seats(str(event_id))

        return {
            "event_id": event_id,
            "available_seats": seats,
        }
