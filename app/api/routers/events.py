from fastapi import APIRouter, Depends, HTTPException, status
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session
from app.services.events_api import EventsProviderClient
from app.repositories.events import EventRepository
from app.services.sync_service import EventSyncService
from app.schemas.event_schema import EventRead


router = APIRouter(prefix="/api/events", tags=["Events"])


@router.post("/sync/trigger/")
async def sync_events(session: AsyncSession = Depends(get_async_session)):
    client = EventsProviderClient()
    repo = EventRepository(session)
    service = EventSyncService(client, repo)

    await service.sync_all()

    return {"status": "ok"}


@router.get("/", response_model=list[EventRead])
async def get_events(
    limit: int = 10, offset: int = 0, session: AsyncSession = Depends(get_async_session)
):
    repo = EventRepository(session)
    events = await repo.get_all_events(limit=limit, offset=offset)
    return events


@router.get("/{event_id}/", response_model=EventRead)
async def get_event(event_id: UUID, session: AsyncSession = Depends(get_async_session)):
    repo = EventRepository(session)
    event = await repo.get_events_by_id(event_id)

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event
