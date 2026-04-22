import pytest
from unittest.mock import AsyncMock

from app.services.events_paginator import EventsPaginator


class DummyPage:
    def __init__(self, next_url, results=None):
        self.next = next_url
        self.results = results or []


@pytest.mark.asyncio
async def test_events_paginator_iterals_all_pages():
    client = AsyncMock()

    client.fetch_page = AsyncMock(side_effect=[DummyPage("url-2"), DummyPage(None)])

    paginator = EventsPaginator(client=client, changed_at="2000-01-01")

    pages = []

    async for page in paginator:
        pages.append(page)

    assert len(pages) == 2
    assert client.fetch_page.call_count == 2

    client.fetch_page.assert_any_call(changed_at="2000-01-01")
    client.fetch_page.assert_any_call(url="url-2")
