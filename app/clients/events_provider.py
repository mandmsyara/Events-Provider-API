import httpx

from app.core.config import EXTERNAL_API_KEY, EXTERNAL_API_URL
from app.exception.exceptions import ProviderRequestError, TicketNotFoundError
from app.schemas.event_schema import ExternalEventResponse


class EventsProviderClient:
    def __init__(self):
        self.base_url = EXTERNAL_API_URL
        self.headers = {"x-api-key": EXTERNAL_API_KEY}
        self.client = httpx.AsyncClient(headers=self.headers)

    async def fetch_page(
        self, url: str | None = None, changed_at: str | None = None
    ) -> ExternalEventResponse:

        if url:
            target_url = url
        else:
            changed_at_value = changed_at or "2000-01-01"
            target_url = (
                url or f"{self.base_url}/api/events/?changed_at={changed_at_value}"
            )

        response = await self.client.get(
            target_url, timeout=20.0, follow_redirects=True
        )
        response.raise_for_status()

        return ExternalEventResponse(**response.json())

    async def get_seats(self, event_id: str) -> list[str]:
        url = f"{self.base_url}/api/events/{event_id}/seats/"

        response = await self.client.get(url, timeout=20.0, follow_redirects=True)

        if response.status_code == 404:
            raise ProviderRequestError("Event not found in provider")

        if response.status_code == 500:
            raise ProviderRequestError("Provider error while fetching seats")

        response.raise_for_status()
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
            raise ProviderRequestError("Seat already taken")

        if response.status_code == 404:
            raise ProviderRequestError("Event not found")

        response.raise_for_status()

        return response.json()["ticket_id"]

    async def unregister(self, event_id: str, ticket_id: str):
        url = f"{self.base_url}/api/events/{event_id}/unregister/"

        response = await self.client.request(
            "DELETE", url, json={"ticket_id": ticket_id}, follow_redirects=True
        )

        if response.status_code == 404:
            raise TicketNotFoundError()

        response.raise_for_status()

        return True
