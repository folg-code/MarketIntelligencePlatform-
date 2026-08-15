"""LLM-assisted event extraction: `Document` (+ fetched full text) -> `Event`s.

Per `docs/architecture/decisions/ADR-001-llm-decision-boundaries.md`,
candidate event extraction is a low-risk semantic transformation the LLM
may perform independently; the `Event`s produced here are candidates for
later pipeline stages (narrative assignment, validation layer) to consume,
not a finalized/protected outcome, so nothing here needs to route through
a validation layer.

`parse_llm_response` (and the module-level constants/functions it calls)
are pure and network-free, so they can be unit-tested deterministically
against canned LLM responses (fixtures/fakes for `LLMClient`), per
`docs/architecture/ai-and-evidence.md` (Testing Expectations).
"""

from __future__ import annotations

import json
from datetime import datetime

from market_intel.event_extraction.full_text_fetcher import FullTextFetcher
from market_intel.event_extraction.llm_client import LLMClient
from market_intel.event_extraction.prompts import SYSTEM_PROMPT, build_user_prompt
from market_intel.persistence.models import Document, Event


class EventExtractionError(Exception):
    """Raised when an LLM response cannot be parsed into candidate events at all."""


def parse_llm_response(raw_response: str, *, document: Document, model_name: str) -> list[Event]:
    """Parse a raw LLM completion into candidate `Event`s for `document`.

    Individual malformed candidate events (e.g. missing a title) are
    skipped rather than failing the whole batch, mirroring
    `market_intel.ingestion.fed_fomc`'s tolerance of partially-malformed
    input; a response that is not JSON at all, or has no "events" list,
    raises `EventExtractionError` since nothing useful can be recovered.
    """
    payload = _parse_json_object(raw_response)

    try:
        candidates = payload["events"]
    except (KeyError, TypeError) as exc:
        raise EventExtractionError(
            f"LLM response missing an 'events' list: {raw_response!r}"
        ) from exc

    if not isinstance(candidates, list):
        raise EventExtractionError(f"LLM response 'events' is not a list: {raw_response!r}")

    events: list[Event] = []
    for candidate in candidates:
        event = _event_from_candidate(candidate, document=document, model_name=model_name)
        if event is not None:
            events.append(event)
    return events


def _parse_json_object(raw_response: str) -> dict:
    text = raw_response.strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("json"):
            text = text[len("json") :]
        text = text.strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise EventExtractionError(f"LLM response is not valid JSON: {raw_response!r}") from exc

    if not isinstance(parsed, dict):
        raise EventExtractionError(f"LLM response is not a JSON object: {raw_response!r}")
    return parsed


def _event_from_candidate(
    candidate: object, *, document: Document, model_name: str
) -> Event | None:
    if not isinstance(candidate, dict):
        return None

    title = candidate.get("title")
    if not title or not isinstance(title, str):
        return None

    return Event(
        document=document,
        type=candidate.get("type"),
        title=title,
        occurred_at=_parse_occurred_at(candidate.get("occurred_at")),
        entities=_string_list(candidate.get("entities")),
        topics=_string_list(candidate.get("topics")),
        extracted_facts=_string_list(candidate.get("extracted_facts")),
        source_claims=_string_list(candidate.get("source_claims")),
        confidence=_parse_confidence(candidate.get("confidence")),
        extraction_model=model_name,
    )


def _parse_occurred_at(raw_value: object) -> datetime | None:
    if not raw_value or not isinstance(raw_value, str):
        return None
    try:
        return datetime.fromisoformat(raw_value)
    except ValueError:
        return None


def _parse_confidence(raw_value: object) -> float | None:
    if isinstance(raw_value, (int, float)) and not isinstance(raw_value, bool):
        return float(raw_value)
    return None


def _string_list(raw_value: object) -> list[str]:
    if not isinstance(raw_value, list):
        return []
    return [item for item in raw_value if isinstance(item, str)]


class EventExtractor:
    """Orchestrates full-text fetch -> LLM prompt -> candidate `Event`s for one `Document`."""

    def __init__(self, *, llm_client: LLMClient, full_text_fetcher: FullTextFetcher) -> None:
        self._llm_client = llm_client
        self._full_text_fetcher = full_text_fetcher

    async def extract(self, document: Document) -> list[Event]:
        """Fetch `document.url`'s full text and extract candidate `Event`s from it."""
        full_text = await self._full_text_fetcher.fetch_full_text(document.url)
        user_prompt = build_user_prompt(document, full_text)
        raw_response = await self._llm_client.generate(
            system_prompt=SYSTEM_PROMPT, user_prompt=user_prompt
        )
        return parse_llm_response(
            raw_response, document=document, model_name=self._llm_client.model_name
        )
