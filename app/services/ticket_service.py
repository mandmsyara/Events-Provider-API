import hashlib
import json
import uuid
from uuid import UUID

from app.clients.events_provider import EventsProviderClient
from app.core.enums import EventStatus
from app.exception.exceptions import (
    EventNotAvailableError,
    EventNotFoundError,
    IdempotencyConflictError,
    SeatNotAvailableError,
    TicketNotFoundError,
)
from app.repositories.events import EventRepository
from app.repositories.idempotency import IdempotencyRepository
from app.repositories.outbox import OutboxRepository
from app.repositories.tickets import TicketRepository


def make_request_hash(data) -> str:
    payload = {
        "event_id": str(data.event_id),
        "first_name": data.first_name,
        "last_name": data.last_name,
        "email": data.email,
        "seat": data.seat,
    }

    raw = json.dumps(payload, sort_keys=True)

    return hashlib.sha256(raw.encode()).hexdigest()


class TicketService:
    def __init__(
        self,
        client: EventsProviderClient,
        event_repo: EventRepository,
        ticket_repo: TicketRepository,
        outbox_repo: OutboxRepository,
        idempotency_repo: IdempotencyRepository,
    ):
        self.client = client
        self.event_repo = event_repo
        self.ticket_repo = ticket_repo
        self.outbox_repo = outbox_repo
        self.idempotency_repo = idempotency_repo

    async def create_ticket(self, data):
        request_hash = None

        if data.idempotency_key:
            request_hash = make_request_hash(data)
            saved = await self.idempotency_repo.get_by_key(data.idempotency_key)

            if saved:
                if saved.request_hash != request_hash:
                    raise IdempotencyConflictError()

                return saved.response_payload

        event = await self.event_repo.get_events_by_id(data.event_id)

        if not event:
            raise EventNotFoundError()

        if event.status != EventStatus.PUBLISHED:
            raise EventNotAvailableError()

        seats = await self.client.get_seats(str(data.event_id))

        if data.seat not in seats:
            raise SeatNotAvailableError()

        ticket_id = await self.client.register(
            str(data.event_id),
            data.first_name,
            data.last_name,
            data.email,
            data.seat,
        )

        ticket = await self.ticket_repo.create(
            {
                "id": uuid.UUID(ticket_id),
                "event_id": data.event_id,
                "first_name": data.first_name,
                "last_name": data.last_name,
                "seat": data.seat,
                "email": data.email,
            }
        )
        await self.outbox_repo.create(
            {
                "event_type": "ticket_created",
                "payload": {
                    "ticket_id": str(ticket.id),
                    "event_id": str(event.id),
                    "event_title": event.name,
                    "seat": ticket.seat,
                    "email": ticket.email,
                    "first_name": ticket.first_name,
                    "last_name": ticket.last_name,
                },
            }
        )

        response_payload = {"ticket_id": str(ticket.id)}

        if data.idempotency_key:
            await self.idempotency_repo.create(
                {
                    "idempotency_key": data.idempotency_key,
                    "request_hash": request_hash,
                    "ticket_id": ticket.id,
                    "response_payload": response_payload,
                }
            )

        await self.ticket_repo.session.commit()

        return response_payload

    async def delete_ticket(self, ticket_id: UUID):
        ticket = await self.ticket_repo.get_by_id(ticket_id)

        if not ticket:
            raise TicketNotFoundError()

        await self.client.unregister(str(ticket.event_id), str(ticket.id))

        await self.ticket_repo.delete(ticket)
        await self.ticket_repo.session.commit()

        return {"success": True}
