"""Unit tests for event-extraction parsing and orchestration.

Uses canned/fixture LLM responses (no live Ollama call) per
`docs/architecture/ai-and-evidence.md` (Testing Expectations): event
extraction must be tested deterministically, independent of a live LLM.
"""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from market_intel.event_extraction.extraction import (
    EventExtractionError,
    EventExtractor,
    parse_llm_response,
)
from market_intel.persistence.models import Document, ProcessingStatus


@pytest.fixture
def document() -> Document:
    return Document(
        id=1,
        source="federal_reserve",
        source_type="press_release_rss",
        published_at=datetime(2026, 7, 29, 18, 0, 0, tzinfo=UTC),
        collected_at=datetime(2026, 7, 29, 18, 5, 0, tzinfo=UTC),
        title="Federal Reserve issues FOMC statement",
        body="Federal Reserve issues FOMC statement",
        url="https://www.federalreserve.gov/newsevents/pressreleases/monetary20260729a.htm",
        language="en",
        raw_metadata={},
        processing_status=ProcessingStatus.PENDING,
    )


CANNED_RESPONSE = """{
  "events": [
    {
      "type": "rate_decision",
      "title": "FOMC maintains federal funds rate target range",
      "occurred_at": "2026-07-29T18:00:00+00:00",
      "entities": ["Federal Open Market Committee", "Federal Reserve"],
      "topics": ["monetary_policy", "interest_rates"],
      "extracted_facts": [
        "The Committee maintained the target range at 3-1/2 to 3-3/4 percent.",
        "Hammack, Kashkari, and Logan voted against the action."
      ],
      "source_claims": [
        "The Committee judges economic activity to be expanding at a solid pace."
      ],
      "confidence": 0.9
    }
  ]
}"""


def test_parse_llm_response_keeps_facts_and_claims_in_separate_fields(document: Document) -> None:
    events = parse_llm_response(CANNED_RESPONSE, document=document, model_name="llama3.1")

    assert len(events) == 1
    event = events[0]
    assert event.extracted_facts == [
        "The Committee maintained the target range at 3-1/2 to 3-3/4 percent.",
        "Hammack, Kashkari, and Logan voted against the action.",
    ]
    assert event.source_claims == [
        "The Committee judges economic activity to be expanding at a solid pace."
    ]
    assert not (set(event.extracted_facts) & set(event.source_claims))


def test_parse_llm_response_maps_documented_fields(document: Document) -> None:
    events = parse_llm_response(CANNED_RESPONSE, document=document, model_name="llama3.1")
    event = events[0]

    assert event.document is document
    assert event.type == "rate_decision"
    assert event.title == "FOMC maintains federal funds rate target range"
    assert event.occurred_at == datetime(2026, 7, 29, 18, 0, 0, tzinfo=UTC)
    assert event.entities == ["Federal Open Market Committee", "Federal Reserve"]
    assert event.topics == ["monetary_policy", "interest_rates"]
    assert event.confidence == 0.9
    assert event.extraction_model == "llama3.1"


def test_parse_llm_response_handles_multiple_events(document: Document) -> None:
    raw_response = """{"events": [
        {"title": "Event one", "extracted_facts": ["fact one"], "source_claims": []},
        {"title": "Event two", "extracted_facts": ["fact two"], "source_claims": []}
    ]}"""

    events = parse_llm_response(raw_response, document=document, model_name="llama3.1")

    assert [event.title for event in events] == ["Event one", "Event two"]


def test_parse_llm_response_returns_empty_list_for_no_events(document: Document) -> None:
    events = parse_llm_response('{"events": []}', document=document, model_name="llama3.1")

    assert events == []


def test_parse_llm_response_skips_candidates_missing_a_title(document: Document) -> None:
    raw_response = """{"events": [
        {"extracted_facts": ["fact without a title"]},
        {"title": "Valid event", "extracted_facts": ["fact"]}
    ]}"""

    events = parse_llm_response(raw_response, document=document, model_name="llama3.1")

    assert [event.title for event in events] == ["Valid event"]


def test_parse_llm_response_defaults_missing_optional_fields(document: Document) -> None:
    events = parse_llm_response(
        '{"events": [{"title": "Bare event"}]}', document=document, model_name="llama3.1"
    )
    event = events[0]

    assert event.type is None
    assert event.occurred_at is None
    assert event.entities == []
    assert event.topics == []
    assert event.extracted_facts == []
    assert event.source_claims == []
    assert event.confidence is None


def test_parse_llm_response_ignores_unparsable_occurred_at(document: Document) -> None:
    raw_response = '{"events": [{"title": "Event", "occurred_at": "not-a-date"}]}'

    events = parse_llm_response(raw_response, document=document, model_name="llama3.1")

    assert events[0].occurred_at is None


def test_parse_llm_response_strips_markdown_code_fences(document: Document) -> None:
    fenced_response = f"```json\n{CANNED_RESPONSE}\n```"

    events = parse_llm_response(fenced_response, document=document, model_name="llama3.1")

    assert len(events) == 1


def test_parse_llm_response_raises_on_invalid_json(document: Document) -> None:
    with pytest.raises(EventExtractionError):
        parse_llm_response("not json at all", document=document, model_name="llama3.1")


def test_parse_llm_response_raises_when_events_key_is_missing(document: Document) -> None:
    with pytest.raises(EventExtractionError):
        parse_llm_response('{"unexpected": []}', document=document, model_name="llama3.1")


def test_parse_llm_response_raises_when_events_is_not_a_list(document: Document) -> None:
    with pytest.raises(EventExtractionError):
        parse_llm_response('{"events": "not-a-list"}', document=document, model_name="llama3.1")


class FakeFullTextFetcher:
    """Deterministic fake for `FullTextFetcher`, per `ai-and-evidence.md` Testing Expectations."""

    def __init__(self, full_text: str) -> None:
        self.full_text = full_text
        self.requested_urls: list[str] = []

    async def fetch_full_text(self, url: str) -> str:
        self.requested_urls.append(url)
        return self.full_text


class FakeLLMClient:
    """Deterministic fake for `LLMClient`, per `ai-and-evidence.md` Testing Expectations."""

    def __init__(self, response: str, *, model_name: str = "fake-model") -> None:
        self._response = response
        self._model_name = model_name
        self.calls: list[dict] = []

    @property
    def model_name(self) -> str:
        return self._model_name

    async def generate(self, *, system_prompt: str, user_prompt: str) -> str:
        self.calls.append({"system_prompt": system_prompt, "user_prompt": user_prompt})
        return self._response


async def test_event_extractor_fetches_full_text_then_extracts_events(document: Document) -> None:
    fetcher = FakeFullTextFetcher("The Committee decided to maintain the target range.")
    llm_client = FakeLLMClient(CANNED_RESPONSE)
    extractor = EventExtractor(llm_client=llm_client, full_text_fetcher=fetcher)

    events = await extractor.extract(document)

    assert fetcher.requested_urls == [document.url]
    assert len(events) == 1
    assert events[0].extraction_model == "fake-model"
    sent_prompt = llm_client.calls[0]["user_prompt"]
    assert "The Committee decided to maintain the target range." in sent_prompt


async def test_event_extractor_propagates_parse_errors_for_unusable_responses(
    document: Document,
) -> None:
    fetcher = FakeFullTextFetcher("full text")
    llm_client = FakeLLMClient("not valid json")
    extractor = EventExtractor(llm_client=llm_client, full_text_fetcher=fetcher)

    with pytest.raises(EventExtractionError):
        await extractor.extract(document)
