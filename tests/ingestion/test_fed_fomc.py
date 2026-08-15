"""Unit tests for the Fed/FOMC ingestion adapter.

Uses a recorded fixture of the real Fed monetary-policy RSS feed response
(`tests/fixtures/fed_fomc_press_monetary.xml`) rather than any live network
call, per the project's testing policy (deterministic, isolated tests).
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest

from market_intel.ingestion.fed_fomc import (
    DEFAULT_FEED_URL,
    SOURCE_NAME,
    SOURCE_TYPE,
    FedFomcFeedAdapter,
    parse_feed,
)
from market_intel.persistence.models import ProcessingStatus

FIXTURE_PATH = Path(__file__).parent.parent / "fixtures" / "fed_fomc_press_monetary.xml"


@pytest.fixture
def raw_feed_xml() -> str:
    return FIXTURE_PATH.read_text(encoding="utf-8")


def test_parse_feed_returns_one_document_per_item(raw_feed_xml: str) -> None:
    documents = parse_feed(raw_feed_xml)

    assert len(documents) == 15


def test_parse_feed_normalizes_first_item_fields(raw_feed_xml: str) -> None:
    documents = parse_feed(raw_feed_xml)
    first = documents[0]

    assert first.source == SOURCE_NAME
    assert first.source_type == SOURCE_TYPE
    assert first.title == "Federal Reserve issues FOMC statement"
    assert first.body == "Federal Reserve issues FOMC statement"
    assert first.url == "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm"
    assert first.language == "en"
    assert first.processing_status == ProcessingStatus.PENDING
    assert first.published_at == datetime(2026, 7, 29, 18, 0, 0, tzinfo=UTC)


def test_parse_feed_captures_category_and_guid_in_raw_metadata(raw_feed_xml: str) -> None:
    documents = parse_feed(raw_feed_xml)
    first = documents[0]

    assert first.raw_metadata["category"] == "Monetary Policy"
    assert (
        first.raw_metadata["guid"]
        == "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm"
    )


def test_parse_feed_decodes_html_entities_in_titles(raw_feed_xml: str) -> None:
    documents = parse_feed(raw_feed_xml)

    minutes_titles = [d.title for d in documents if "discount rate" in d.title]
    assert any("Board's discount rate" in title for title in minutes_titles)


def test_parse_feed_sets_a_recent_collected_at(raw_feed_xml: str) -> None:
    before = datetime.now(UTC)
    documents = parse_feed(raw_feed_xml)
    after = datetime.now(UTC)

    assert all(before <= document.collected_at <= after for document in documents)


def test_parse_feed_skips_items_missing_title_or_link() -> None:
    raw_xml = """<?xml version="1.0" encoding="utf-8" ?>
    <rss version="2.0">
        <channel>
            <language>en</language>
            <item>
                <title>Only a title, no link</title>
                <description>ignored</description>
            </item>
            <item>
                <link>https://www.federalreserve.gov/only-link.htm</link>
                <description>ignored</description>
            </item>
        </channel>
    </rss>
    """

    assert parse_feed(raw_xml) == []


def test_parse_feed_returns_empty_list_for_missing_channel() -> None:
    assert parse_feed('<?xml version="1.0"?><rss version="2.0"></rss>') == []


async def test_fetch_documents_uses_injected_http_client_and_no_live_network() -> None:
    raw_xml = FIXTURE_PATH.read_text(encoding="utf-8")
    requested_urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested_urls.append(str(request.url))
        return httpx.Response(200, text=raw_xml)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = FedFomcFeedAdapter(http_client=client)
        documents = await adapter.fetch_documents()

    assert requested_urls == [DEFAULT_FEED_URL]
    assert len(documents) == 15


async def test_fetch_documents_raises_on_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="service unavailable")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        adapter = FedFomcFeedAdapter(http_client=client)
        with pytest.raises(httpx.HTTPStatusError):
            await adapter.fetch_documents()
