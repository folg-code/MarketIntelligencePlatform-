"""Unit tests for the full-text fetcher.

Uses a recorded fixture of a real Fed press-release page
(`tests/fixtures/fed_fomc_press_release_monetary20260729a.html`) rather than
any live network call, per the project's testing policy (deterministic,
isolated tests) and `docs/architecture/ai-and-evidence.md` (Testing
Expectations).
"""

from __future__ import annotations

from pathlib import Path

import httpx
import pytest

from market_intel.event_extraction.full_text_fetcher import (
    HttpFullTextFetcher,
    extract_text_from_html,
)

FIXTURE_PATH = (
    Path(__file__).parent.parent / "fixtures" / "fed_fomc_press_release_monetary20260729a.html"
)


@pytest.fixture
def raw_press_release_html() -> str:
    return FIXTURE_PATH.read_text(encoding="utf-8")


def test_extract_text_from_html_includes_the_statement_paragraphs(
    raw_press_release_html: str,
) -> None:
    text = extract_text_from_html(raw_press_release_html)

    assert "The Federal Open Market Committee approved the following statement" in text
    assert "maintain the target range for the federal funds rate at 3-1/2 to 3-3/4 percent" in text
    assert "Voting against the monetary policy action were Beth M. Hammack" in text


def test_extract_text_from_html_excludes_navigation_and_footer_boilerplate(
    raw_press_release_html: str,
) -> None:
    text = extract_text_from_html(raw_press_release_html)

    assert "Skip to main content" not in text
    assert "Board of Governors of the Federal Reserve System" not in text
    assert "Freedom of Information (FOIA)" not in text
    assert "Site Map" not in text


def test_extract_text_from_html_excludes_script_and_style_content(
    raw_press_release_html: str,
) -> None:
    text = extract_text_from_html(raw_press_release_html)

    assert "document.ready" not in text
    assert "ekkoLightbox" not in text


def test_extract_text_from_html_decodes_html_entities(raw_press_release_html: str) -> None:
    text = extract_text_from_html(raw_press_release_html)

    assert "9\u2013 3 vote" in text or "9 \u2013 3 vote" in text


def test_extract_text_from_html_falls_back_to_whole_document_without_scope_element() -> None:
    raw_html = """<!doctype html>
    <html><body>
    <script>var x = 1;</script>
    <p>Only paragraph, no id="article" wrapper.</p>
    </body></html>
    """

    text = extract_text_from_html(raw_html)

    assert text == 'Only paragraph, no id="article" wrapper.'


def test_extract_text_from_html_scopes_to_article_element_when_present() -> None:
    raw_html = """<!doctype html>
    <html><body>
    <nav><p>Ignore this navigation text.</p></nav>
    <div id="article"><div class="inner"><p>Keep this article text.</p></div></div>
    <footer><p>Ignore this footer text.</p></footer>
    </body></html>
    """

    text = extract_text_from_html(raw_html)

    assert text == "Keep this article text."


async def test_fetch_full_text_uses_injected_http_client_and_no_live_network(
    raw_press_release_html: str,
) -> None:
    requested_urls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requested_urls.append(str(request.url))
        return httpx.Response(200, text=raw_press_release_html)

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        fetcher = HttpFullTextFetcher(http_client=client)
        text = await fetcher.fetch_full_text(
            "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm"
        )

    assert requested_urls == ["https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm"]
    assert "The Committee decided to maintain the target range" in text


async def test_fetch_full_text_raises_on_http_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, text="service unavailable")

    transport = httpx.MockTransport(handler)
    async with httpx.AsyncClient(transport=transport) as client:
        fetcher = HttpFullTextFetcher(http_client=client)
        with pytest.raises(httpx.HTTPStatusError):
            await fetcher.fetch_full_text("https://www.federalreserve.gov/anything.htm")
