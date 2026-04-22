from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session
from app.repositories.events import EventRepository
from app.repositories.sync_state import SyncStateRepository
from app.repositories.tickets import TicketRepository
from app.schemas.event_schema import EventListResponse, EventRead
from app.schemas.tickets import TicketCreate
from app.services.events_api import EventsProviderClient, SeatsService
from app.services.sync_service import EventSyncService
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/api", tags=["Events"])


@router.post("/sync/trigger/")
async def sync_events(session: AsyncSession = Depends(get_async_session)):
    client = EventsProviderClient()
    repo = EventRepository(session)
    sync_state_repo = SyncStateRepository(session)

    service = EventSyncService(client, repo, sync_state_repo)
    started = await service.sync_all()

    if not started:
        return {"status": "already started"}
    return {"status": "ok"}


@router.get("/events/", response_model=EventListResponse)
async def get_events(
    page: int = 1,
    page_size: int = 20,
    date_from: date | None = None,
    session: AsyncSession = Depends(get_async_session),
):
    repo = EventRepository(session)

    count = await repo.count_events(date_from=date_from)
    events = await repo.get_all_events(
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


@router.get("/events/{event_id}/", response_model=EventRead)
async def get_event(event_id: UUID, session: AsyncSession = Depends(get_async_session)):
    repo = EventRepository(session)
    event = await repo.get_events_by_id(event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.get("/events/{event_id}/seats/")
async def get_event_seats(
    event_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    repo = EventRepository(session)
    client = EventsProviderClient()
    service = SeatsService(client, repo)

    return await service.get_available_seats(event_id)


@router.post("/tickets/", status_code=201)
async def create_ticket(
    payload: TicketCreate, session: AsyncSession = Depends(get_async_session)
):
    event_repo = EventRepository(session)
    ticket_repo = TicketRepository(session)
    client = EventsProviderClient()

    service = TicketService(client, event_repo, ticket_repo)

    return await service.create_ticket(payload)


@router.delete("/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: str, session: AsyncSession = Depends(get_async_session)
):
    event_repo = EventRepository(session)
    ticket_repo = TicketRepository(session)
    client = EventsProviderClient()

    service = TicketService(client, event_repo, ticket_repo)

    return await service.delete_ticket(ticket_id)
