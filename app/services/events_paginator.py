from app.clients.events_provider import EventsProviderClient
from app.schemas.event_schema import ExternalEventResponse


class EventsPaginator:
    def __init__(self, client: EventsProviderClient, changed_at: str | None = None):
        self.client = client
        self.changed_at = changed_at
        self._next_url: str | None = None
        self._started = False
        self._done = False

    def __aiter__(self) -> "EventsPaginator":
        return self

    async def __anext__(self) -> ExternalEventResponse:
        if self._done:
            raise StopAsyncIteration

        if not self._started:
            self._started = True
            page = await self.client.fetch_page(changed_at=self.changed_at)
        else:
            if not self._next_url:
                self._done = True
                raise StopAsyncIteration
            page = await self.client.fetch_page(url=self._next_url)
        self._next_url = page.next

        return page
