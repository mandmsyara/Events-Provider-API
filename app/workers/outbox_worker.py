import asyncio
import logging

from app.clients.capashino import CapashinoClient
from app.core.config import settings
from app.database.session import async_session
from app.repositories.outbox import OutboxRepository

logger = logging.getLogger(__name__)


class OutboxWorker:
    def __init__(self):
        self.client = CapashinoClient()

    async def run(self):
        while True:
            try:
                await self.process_batch()
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("Outbox worker failed")

            await asyncio.sleep(settings.outbox_worker_interval)

    async def process_batch(self):
        async with async_session() as session:
            outbox_repo = OutboxRepository(session)

            events = await outbox_repo.get_pending(limit=settings.outbox_batch_size)

            for event in events:
                try:
                    await self.process_event(event, outbox_repo)
                except Exception:
                    logger.exception("failed to process outbox event %s", event.id)
            await session.commit()

    async def process_event(self, event, outbox_repo: OutboxRepository):
        if event.event_type != "ticket_created":
            logger.warning("Unknown outbox event type: %s", event.event_type)
            return

        payload = event.payload

        ticket_id = payload["ticket_id"]
        event_title = payload["event_title"]
        seat = payload["seat"]

        message = (
            f"Вы успешно зарегистрированы на мероприятие - {event_title}. Место: {seat}"
        )

        await self.client.send_notification(
            message=message,
            reference_id=ticket_id,
            idempotency_key=f"ticket-notification-{ticket_id}",
        )

        await outbox_repo.mark_as_sent(event.id)
