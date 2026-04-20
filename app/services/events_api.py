import httpx
from app.schemas.event_schema import ExternalEventResponse
from app.core.config import EXTERNAL_API_KEY, EXTERNAL_API_URL


class EventsProviderClient:
    def __init__(self):
        self.base_url = EXTERNAL_API_URL
        self.headers = {"x-api-key": EXTERNAL_API_KEY}

    async def fetch_page(self, url: str | None = None) -> ExternalEventResponse:
        target_url = url or f"{self.base_url}/api/events/"

        async with httpx.AsyncClient() as client:
            response = await client.get(
                target_url, headers=self.headers, timeout=20.0, follow_redirects=True
            )
            response.raise_for_status()
            return ExternalEventResponse(**response.json())
