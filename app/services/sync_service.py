import asyncio
import logging
from datetime import datetime

from app.repositories.events import EventRepository
from app.services.events_api import EventsProviderClient
from app.repositories.sync_state import SyncStateRepository

logger = logging.getLogger(__name__)


class EventSyncService:
    _is_running = False

    def __init__(
        self,
        client: EventsProviderClient,
        repo: EventRepository,
        sync_state_repo: SyncStateRepository,
    ):
        self.client = client
        self.repo = repo
        self.sync_state_repo = sync_state_repo

    async def sync_all(self) -> bool:
        if EventSyncService._is_running:
            logger.info("Sync already running, skip new request")
            return False

        EventSyncService._is_running = True
        try:
            state = await self.sync_state_repo.get_or_create()

            changed_at = (
                state.last_changed_at.date().isoformat()
                if state.last_changed_at
                else "2000-01-01"
            )

            logger.info("Sync started with changed_at=%s", changed_at)

            await self.sync_state_repo.mark_running()
            await self.repo.session.commit()

            page = await self.client.fetch_page(changed_at=changed_at)

            max_changed_at: datetime | None = state.last_changed_at

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

                        if event_schema.changed_at and (
                            max_changed_at is None
                            or event_schema.changed_at > max_changed_at
                        ):
                            max_changed_at = event_schema.changed_at

                    await self.repo.session.commit()

                except Exception:
                    await self.repo.session.rollback()
                    raise

                if not page.next:
                    break

                page = await self.client.fetch_page(url=page.next)

            await self.sync_state_repo.mark_succes(max_changed_at)
            await self.repo.session.commit()

            logger.info("Sync finished succefully, last_changed_at=%s", max_changed_at)

            return True
        except Exception:
            logger.exception("Sync failed")
            await self.repo.session.rollback()
            await self.sync_state_repo.mark_failed()
            await self.repo.session.commit()
            raise

        finally:
            EventSyncService._is_running = False
