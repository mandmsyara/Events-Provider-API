from fastapi import HTTPException
import httpx
from app.schemas.event_schema import ExternalEventResponse
from app.core.config import EXTERNAL_API_KEY, EXTERNAL_API_URL
from app.repositories.events import EventRepository


class EventsProviderClient:
    def __init__(self):
        self.base_url = EXTERNAL_API_URL
        self.headers = {"x-api-key": EXTERNAL_API_KEY}
        self.client = httpx.AsyncClient(headers=self.headers)

    async def fetch_page(self, url: str | None = None) -> ExternalEventResponse:
        target_url = url or f"{self.base_url}/api/events/"
        response = await self.client.get(
            target_url, timeout=20.0, follow_redirects=True
        )
        response.raise_for_status()
        return ExternalEventResponse(**response.json())

    async def get_seats(self, event_id: str) -> list[str]:
        url = f"{self.base_url}/api/events/{event_id}/seats/"

        response = await self.client.get(url)

        if response.status_code == 404:
            raise Exception("Event not found in provider!")

        if response.status_code == 500:
            raise Exception("Provider error (event not published)!")

        data = response.json()

        return data.get("seats", [])

    async def register(
        self, event_id: str, first_name: str, last_name: str, email: str, seat: str
    ) -> str:
        url = f"{self.base_url}/api/events/{event_id}/register/"

        payload = {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "seat": seat,
        }

        response = await self.client.post(url, json=payload, follow_redirects=True)

        if response.status_code == 400:
            raise HTTPException(status_code=400, details="Seat already taken")

        if response.status_code == 404:
            raise HTTPException(status_code=404, details="Event not found")

        response.raise_for_status()

        return response.json()["ticket_id"]

    async def unregister(self, event_id: str, ticket_id: str):
        url = f"{self.base_url}/api/events/{event_id}/unregister/"

        response = await self.client.request(
            "DELETE", url, json={"ticket_id": ticket_id}, follow_redirects=True
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, details="Ticket not found")

        response.raise_for_status()

        return True


class SeatsService:
    def __init__(self, client: EventsProviderClient, repo: EventRepository):
        self.client = client
        self.repo = repo

    async def get_available_seats(self, event_id):
        event = await self.repo.get_events_by_id(event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if event.status != "published":
            raise HTTPException(
                status_code=400,
                detail="Event is not available for registration",
            )

        seats = await self.client.get_seats(str(event_id))

        return {
            "event_id": event_id,
            "available_seats": seats,
        }
