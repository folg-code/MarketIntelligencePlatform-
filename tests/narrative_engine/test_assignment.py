"""Unit tests for the pure narrative-assignment decision.

No database session involved: `matching_narrative` is supplied directly by
the test, mirroring how `market_intel.narrative_engine.service` would pass
in whatever it already looked up.
"""

from __future__ import annotations

from market_intel.narrative_engine.assignment import assign_event
from market_intel.narrative_engine.canonical_key import compute_canonical_key
from market_intel.persistence.models import (
    Event,
    Narrative,
    NarrativeLifecycleStatus,
    NarrativeValidityStatus,
)


def _event(**overrides: object) -> Event:
    defaults: dict[str, object] = {
        "type": "rate_decision",
        "entities": ["Federal Reserve"],
        "topics": ["monetary_policy"],
    }
    defaults.update(overrides)
    return Event(title="unused for key derivation", **defaults)


def test_no_matching_narrative_creates_a_new_candidate_narrative_with_its_first_event() -> None:
    event = _event()
    canonical_key = compute_canonical_key(event)

    result = assign_event(event, canonical_key=canonical_key, matching_narrative=None)

    assert result.created_narrative is True
    assert result.narrative.canonical_key == canonical_key
    assert result.narrative.validity_status is NarrativeValidityStatus.CANDIDATE
    assert result.narrative.lifecycle_status is NarrativeLifecycleStatus.EMERGING
    assert result.narrative_event.narrative is result.narrative
    assert result.narrative_event.event is event


def test_matching_narrative_appends_a_narrative_event_instead_of_creating_a_new_narrative() -> None:
    existing_narrative = Narrative(
        canonical_key="existing-key",
        validity_status=NarrativeValidityStatus.CANDIDATE,
        lifecycle_status=NarrativeLifecycleStatus.EMERGING,
    )
    event = _event()

    result = assign_event(
        event, canonical_key="existing-key", matching_narrative=existing_narrative
    )

    assert result.created_narrative is False
    assert result.narrative is existing_narrative
    assert result.narrative_event.narrative is existing_narrative
    assert result.narrative_event.event is event
    # Assignment never sets validity_status to anything other than candidate.
    assert result.narrative.validity_status is NarrativeValidityStatus.CANDIDATE
