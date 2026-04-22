from unittest.mock import AsyncMock, patch

import pytest

from app.clients.events_provider import EventsProviderClient


class DummyResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json_data = json_data or {}

    def json(self):
        return self._json_data

    def raise_for_status(self):
        return None


@pytest.mark.asyncio
async def test_fetch_page_returns_external_event_response():
    with patch("app.clients.events_provider.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value = mock_client

        mock_client.get.return_value = DummyResponse(
            200,
            {
                "next": None,
                "previous": None,
                "results": [],
            },
        )

        client = EventsProviderClient()
        page = await client.fetch_page(changed_at="2000-01-01")

        assert page.next is None
        assert page.previous is None
        assert page.results == []


@pytest.mark.asyncio
async def test_get_seats_returns_list_of_seats():
    with patch("app.clients.events_provider.httpx.AsyncClient") as mock_client_cls:
        mock_client = AsyncMock()
        mock_client_cls.return_value = mock_client

        mock_client.get.return_value = DummyResponse(
            200,
            {
                "seats": ["A1", "A2"],
            },
        )

        client = EventsProviderClient()
        seats = await client.get_seats("event-id")

        assert seats == ["A1", "A2"]
