"""Fed/FOMC ingestion adapter.

Source: the Federal Reserve Board's official "Press Release - Monetary
Policy" RSS feed (`https://www.federalreserve.gov/feeds/press_monetary.xml`),
one of the RSS feeds published at
https://www.federalreserve.gov/feeds/feeds.htm. It carries FOMC statements,
FOMC/discount-rate meeting minutes, and other monetary-policy press
releases directly from the Federal Reserve Board (Tier 1 / official source
per `docs/product/MVP_Vision_Architecture_Decisions.md` section 5).

This feed provides only title/summary/link/pubDate/category per item, not
full press-release body text; `Document.body` is therefore populated from
the feed's `<description>` and `Document.url` always carries the canonical
link to the full press release for anyone needing the complete text. See
`ImplementationReport.assumptions` for why fetching full body text from the
linked HTML page is out of scope for this ticket.
"""

from __future__ import annotations

from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree

import httpx

from market_intel.ingestion.base import DocumentSourceAdapter
from market_intel.persistence.models import Document, ProcessingStatus

SOURCE_NAME = "federal_reserve"
SOURCE_TYPE = "press_release_rss"
DEFAULT_FEED_URL = "https://www.federalreserve.gov/feeds/press_monetary.xml"
DEFAULT_LANGUAGE = "en"
REQUEST_TIMEOUT_SECONDS = 10.0


class FedFomcFeedAdapter(DocumentSourceAdapter):
    """Fetches and normalizes the Fed/FOMC monetary-policy press-release RSS feed."""

    def __init__(
        self,
        feed_url: str = DEFAULT_FEED_URL,
        http_client: httpx.AsyncClient | None = None,
    ) -> None:
        self._feed_url = feed_url
        self._http_client = http_client

    async def fetch_documents(self) -> list[Document]:
        """Fetch the feed over HTTP and normalize each item into a `Document`."""
        raw_xml = await self._fetch_raw_feed()
        return parse_feed(raw_xml)

    async def _fetch_raw_feed(self) -> str:
        if self._http_client is not None:
            response = await self._http_client.get(self._feed_url)
            response.raise_for_status()
            return response.text

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(self._feed_url)
            response.raise_for_status()
            return response.text


def parse_feed(raw_xml: str) -> list[Document]:
    """Parse raw RSS 2.0 XML from the feed into normalized `Document` instances.

    Pure function (no network access) so parsing/normalization logic can be
    unit-tested against a recorded fixture of the real feed's response.
    """
    root = ElementTree.fromstring(raw_xml)  # noqa: S314 - trusted, official Fed feed
    channel = root.find("channel")
    if channel is None:
        return []

    feed_language = _text(channel.find("language")) or DEFAULT_LANGUAGE
    collected_at = datetime.now(UTC)

    documents = []
    for item in channel.findall("item"):
        document = _document_from_item(item, feed_language=feed_language, collected_at=collected_at)
        if document is not None:
            documents.append(document)
    return documents


def _document_from_item(
    item: ElementTree.Element, *, feed_language: str, collected_at: datetime
) -> Document | None:
    title = _text(item.find("title"))
    url = _text(item.find("link"))
    if not title or not url:
        return None

    description = _text(item.find("description"))
    category = _text(item.find("category"))
    guid = _text(item.find("guid"))
    published_at = _parse_pub_date(_text(item.find("pubDate")))

    raw_metadata: dict[str, str] = {}
    if category:
        raw_metadata["category"] = category
    if guid:
        raw_metadata["guid"] = guid

    return Document(
        source=SOURCE_NAME,
        source_type=SOURCE_TYPE,
        published_at=published_at,
        collected_at=collected_at,
        title=title,
        body=description,
        url=url,
        language=feed_language,
        raw_metadata=raw_metadata,
        processing_status=ProcessingStatus.PENDING,
    )


def _parse_pub_date(raw_pub_date: str | None) -> datetime | None:
    if not raw_pub_date:
        return None
    try:
        return parsedate_to_datetime(raw_pub_date)
    except (TypeError, ValueError):
        return None


def _text(element: ElementTree.Element | None) -> str | None:
    if element is None or element.text is None:
        return None
    stripped = element.text.strip()
    return stripped or None
