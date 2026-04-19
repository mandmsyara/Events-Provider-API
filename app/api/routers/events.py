from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_async_session
from app.services.events_api import EventsProviderClient
from app.repositories.events import EventRepository
from app.services.sync_service import EventSyncService

from app.core.config import EXTERNAL_API_URL


router = APIRouter(prefix="/events", tags=["Events"])


@router.post("/sync/")
async def sync_events(session: AsyncSession = Depends(get_async_session)):
    client = EventsProviderClient()
    repo = EventRepository(session)
    service = EventSyncService(client, repo)

    await service.sync_all()

    return {"status": "ok"}
