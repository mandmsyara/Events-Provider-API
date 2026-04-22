import logging
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.clients.events_provider import EventsProviderClient
from app.database.session import async_engine
from app.repositories.events import EventRepository
from app.repositories.sync_state import SyncStateRepository
from app.services.sync_service import EventSyncService

logger = logging.getLogger(__name__)

SYNC_INTERVAL_SECONDS = 60 * 60 * 24


async def sync_loop() -> None:
    session_factory = async_sessionmaker(
        bind=async_engine, class_=AsyncSession, expire_on_commit=False
    )

    while True:
        client = None
        try:
            async with session_factory() as session:
                client = EventsProviderClient()
                event_repo = EventRepository(session)
                sync_state_repo = SyncStateRepository(session)
                service = EventSyncService(client, event_repo, sync_state_repo)

                logger.info("Background sync iteration started")

                await service.sync_all()

                logger.info("Background sync iteration finished")

        except Exception:
            logger.exception("Background sync iteration failed")

        finally:
            if client is not None:
                await client.close()

        await asyncio.sleep(SYNC_INTERVAL_SECONDS)
