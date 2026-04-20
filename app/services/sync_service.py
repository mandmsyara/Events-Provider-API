from app.repositories.events import EventRepository
from app.services.events_api import EventsProviderClient


class EventSyncService:
    def __init__(self, client: EventsProviderClient, repo: EventRepository):
        self.client = client
        self.repo = repo

    async def sync_all(self):
        page = await self.client.fetch_page()

        while True:

            try:
                places = {}

                for event_schema in page.results:
                    places[event_schema.place.id] = event_schema.place

                for place in places.values():
                    await self.repo.upsert_place(place.model_dump())

                await self.repo.session.flush()

                for event_schema in page.results:
                    event_dict = event_schema.model_dump(exclude={"place"})
                    event_dict["place_id"] = event_schema.place.id
                    await self.repo.upsert_event(event_dict)

                await self.repo.session.commit()

            except Exception:
                await self.repo.session.rollback()
                raise

            if not page.next:
                break

            page = await self.client.fetch_page(url=page.next)
