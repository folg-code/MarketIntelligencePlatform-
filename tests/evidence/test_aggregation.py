"""Unit tests for the pure evidence-aggregation functions.

No database session involved: `Narrative.narrative_events` is populated
directly by the test, mirroring how `market_intel.evidence.service` would
pass in a `Narrative` whose events are already eager-loaded.
"""

from __future__ import annotations

from market_intel.evidence.aggregation import (
    collect_traceable_document_ids,
    compute_independent_source_count,
)
from market_intel.persistence.models import Event, Narrative, NarrativeEvent


def _narrative_with_document_ids(*document_ids: int) -> Narrative:
    narrative = Narrative(canonical_key="unused-for-aggregation")
    narrative.narrative_events = [
        NarrativeEvent(event=Event(document_id=document_id, title="unused"))
        for document_id in document_ids
    ]
    return narrative


def test_one_narrative_event_tracing_to_one_document_counts_as_one_source() -> None:
    narrative = _narrative_with_document_ids(1)

    assert collect_traceable_document_ids(narrative) == frozenset({1})
    assert compute_independent_source_count(narrative) == 1


def test_multiple_narrative_events_tracing_to_the_same_document_count_once() -> None:
    narrative = _narrative_with_document_ids(1, 1, 1)

    assert collect_traceable_document_ids(narrative) == frozenset({1})
    assert compute_independent_source_count(narrative) == 1


def test_narrative_events_tracing_to_n_distinct_documents_count_n() -> None:
    narrative = _narrative_with_document_ids(1, 2, 3)

    assert collect_traceable_document_ids(narrative) == frozenset({1, 2, 3})
    assert compute_independent_source_count(narrative) == 3


def test_mixed_shared_and_distinct_documents_count_only_distinct_ones() -> None:
    narrative = _narrative_with_document_ids(1, 1, 2, 3, 3, 3)

    assert compute_independent_source_count(narrative) == 3


def test_narrative_with_no_narrative_events_has_zero_traceable_documents() -> None:
    narrative = _narrative_with_document_ids()

    assert collect_traceable_document_ids(narrative) == frozenset()
    assert compute_independent_source_count(narrative) == 0
