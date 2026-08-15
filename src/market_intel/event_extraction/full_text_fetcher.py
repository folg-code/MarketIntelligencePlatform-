"""Full press-release text fetcher for `Document.url`.

`Document.body` only holds the RSS feed's short description (see
`market_intel.ingestion.fed_fomc`); a one-line description would be too weak
a test of local-LLM extraction quality, so event extraction fetches the full
press-release page here before running the LLM (see
`ImplementationReport.assumptions` for the scope decision behind this).

This lives in `event_extraction`, not `ingestion`, to keep the ingestion /
event-extraction component boundary from `docs/architecture/overview.md`
intact: fetching the full page for a `Document` you already have is within
event extraction's existing external-system boundary, not a new adapter.

Extraction is intentionally simple stdlib `html.parser`-based text
extraction, scoped to the Fed press-release page's `id="article"` content
container when present (falling back to whole-document text otherwise) —
kept lightweight since only one official, simple-structure source exists so
far; see `ImplementationReport` for the trade-offs of this heuristic.
"""

from __future__ import annotations

from html.parser import HTMLParser
from typing import Protocol

import httpx

REQUEST_TIMEOUT_SECONDS = 15.0
DEFAULT_SCOPE_ELEMENT_ID = "article"

_SKIP_TEXT_TAGS = {"script", "style"}
_BLOCK_TAGS = {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6", "br", "tr"}


class FullTextFetcher(Protocol):
    """Adapter interface for fetching a Document's full source text by URL."""

    async def fetch_full_text(self, url: str) -> str: ...


class HttpFullTextFetcher:
    """Fetches a URL over HTTP and reduces the HTML response to plain text."""

    def __init__(self, http_client: httpx.AsyncClient | None = None) -> None:
        self._http_client = http_client

    async def fetch_full_text(self, url: str) -> str:
        raw_html = await self._fetch_raw_html(url)
        return extract_text_from_html(raw_html)

    async def _fetch_raw_html(self, url: str) -> str:
        if self._http_client is not None:
            response = await self._http_client.get(url)
            response.raise_for_status()
            return response.text

        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_SECONDS) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.text


def extract_text_from_html(
    raw_html: str, *, scope_element_id: str = DEFAULT_SCOPE_ELEMENT_ID
) -> str:
    """Reduce an HTML page to plain text.

    Pure function (no network access) so it can be unit-tested against a
    recorded fixture of a real page. Prefers the text within the element
    whose `id` matches `scope_element_id` (the Fed press-release page's main
    content container), to avoid drowning the extracted text in
    navigation/footer boilerplate; falls back to the whole document if no
    such element is found, so this degrades gracefully on a differently
    structured page rather than returning nothing.
    """
    scoped_parser = _TextExtractingHTMLParser(scope_id=scope_element_id)
    scoped_parser.feed(raw_html)
    scoped_parser.close()
    if scoped_parser.scope_found:
        return scoped_parser.get_text()

    whole_document_parser = _TextExtractingHTMLParser(scope_id=None)
    whole_document_parser.feed(raw_html)
    whole_document_parser.close()
    return whole_document_parser.get_text()


class _TextExtractingHTMLParser(HTMLParser):
    """Collects text data, optionally scoped to one element's `id` attribute."""

    def __init__(self, *, scope_id: str | None) -> None:
        super().__init__(convert_charrefs=True)
        self._scope_id = scope_id
        self._in_scope = scope_id is None
        self._scope_found = scope_id is None
        self._scope_enter_depth: int | None = None
        self._div_depth = 0
        self._skip_depth = 0
        self._chunks: list[str] = []

    @property
    def scope_found(self) -> bool:
        return self._scope_found

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP_TEXT_TAGS:
            self._skip_depth += 1

        if tag == "div":
            found_scope_start = (
                self._scope_id is not None
                and not self._in_scope
                and dict(attrs).get("id") == self._scope_id
            )
            if found_scope_start:
                self._scope_enter_depth = self._div_depth
                self._in_scope = True
                self._scope_found = True
            self._div_depth += 1

        if tag in _BLOCK_TAGS:
            self._append_break()

    def handle_endtag(self, tag: str) -> None:
        if tag == "div":
            self._div_depth -= 1
            closed_scope = (
                self._in_scope
                and self._scope_enter_depth is not None
                and self._div_depth <= self._scope_enter_depth
            )
            if closed_scope:
                self._in_scope = False

        if tag in _SKIP_TEXT_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

        if tag in _BLOCK_TAGS:
            self._append_break()

    def handle_data(self, data: str) -> None:
        if not self._in_scope or self._skip_depth > 0:
            return
        stripped = data.strip()
        if stripped:
            self._chunks.append(stripped)

    def _append_break(self) -> None:
        if self._chunks and self._chunks[-1] != "\n":
            self._chunks.append("\n")

    def get_text(self) -> str:
        lines: list[str] = []
        current_line: list[str] = []
        for chunk in self._chunks:
            if chunk == "\n":
                if current_line:
                    lines.append(" ".join(current_line))
                    current_line = []
            else:
                current_line.append(chunk)
        if current_line:
            lines.append(" ".join(current_line))

        non_empty_lines = [line for line in (line.strip() for line in lines) if line]
        return "\n".join(non_empty_lines).strip()
