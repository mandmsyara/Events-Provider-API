import httpx

from app.core.config import settings
from app.exception.exceptions import ProviderRequestError


class CapashinoClient:
    def __init__(self):
        self.base_url = settings.capashino_api_url
        self.api_key = settings.capashino_api_key

    async def send_notification(
        self,
        message: str,
        reference_id: str,
        idempotency_key: str,
    ) -> dict:
        async with httpx.AsyncClient(base_url=self.base_url) as client:
            response = await client.post(
                "/api/notifications",
                json={
                    "message": message,
                    "reference_id": reference_id,
                    "idempotency_key": idempotency_key,
                },
                headers={
                    "X-API-Key": self.api_key,
                    "Content-Type": "application/json",
                },
            )

        if response.status_code != 201:
            raise ProviderRequestError(
                f"Capashino error: {response.status_code} {response.text}"
            )

        return response.json()
