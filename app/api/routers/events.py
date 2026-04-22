from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.events_provider import EventsProviderClient
from app.database.session import get_async_session
from app.exception.exceptions import (
    EventNotAvailableError,
    EventNotFoundError,
    ProviderRequestError,
    SeatNotAvailableError,
    TicketNotFoundError,
)
from app.repositories.events import EventRepository
from app.repositories.sync_state import SyncStateRepository
from app.repositories.tickets import TicketRepository
from app.schemas.event_schema import EventListResponse, EventRead
from app.schemas.tickets import TicketCreate, TicketResponse
from app.services.events_service import EventQueryService
from app.services.seats_service import SeatsService
from app.services.sync_service import EventSyncService
from app.services.ticket_service import TicketService

router = APIRouter(prefix="/api", tags=["Events"])


@router.post("/sync/trigger")
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
    service = EventQueryService(repo)

    return await service.get_events(page=page, page_size=page_size, date_from=date_from)


@router.get("/events/{event_id}/", response_model=EventRead)
async def get_event(event_id: UUID, session: AsyncSession = Depends(get_async_session)):
    repo = EventRepository(session)
    service = EventQueryService(repo)
    try:
        return await service.get_event(event_id)
    except EventNotFoundError:
        raise HTTPException(status_code=404, detail="Event not found")


@router.get("/events/{event_id}/seats/")
async def get_event_seats(
    event_id: UUID, session: AsyncSession = Depends(get_async_session)
):
    repo = EventRepository(session)
    client = EventsProviderClient()
    service = SeatsService(client, repo)
    try:
        return await service.get_available_seats(event_id)

    except EventNotFoundError:
        raise HTTPException(status_code=404, detail="Event not found")

    except EventNotAvailableError:
        raise HTTPException(
            status_code=400, detail="Event is not available for registration"
        )

    except ProviderRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tickets", status_code=201, response_model=TicketResponse)
async def create_ticket(
    payload: TicketCreate, session: AsyncSession = Depends(get_async_session)
):
    event_repo = EventRepository(session)
    ticket_repo = TicketRepository(session)
    client = EventsProviderClient()

    service = TicketService(client, event_repo, ticket_repo)

    try:
        return await service.create_ticket(payload)

    except EventNotFoundError:
        raise HTTPException(status_code=404, detail="Event not found")

    except EventNotAvailableError:
        raise HTTPException(
            status_code=400, detail="Event is not available for registration"
        )

    except SeatNotAvailableError:
        raise HTTPException(status_code=400, detail="Seat not available")

    except ProviderRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/tickets/{ticket_id}")
async def delete_ticket(
    ticket_id: str, session: AsyncSession = Depends(get_async_session)
):
    event_repo = EventRepository(session)
    ticket_repo = TicketRepository(session)
    client = EventsProviderClient()

    service = TicketService(client, event_repo, ticket_repo)

    try:
        return await service.delete_ticket(ticket_id)

    except TicketNotFoundError:
        raise HTTPException(status_code=404, detail="Ticket not found")
    except ProviderRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
