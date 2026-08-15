"""Unit tests for `InstrumentImpactService` against a fake session double.

Deliberately avoids a live database: `FakeAsyncSession` below only
implements the one `AsyncSession` operation the service actually calls
(`add`, for staging the new row), mirroring
`tests/narrative_engine/test_service.py`'s `FakeAsyncSession`. There is no
`select`/lookup here (unlike the narrative-engine service) since creating a
`NarrativeInstrumentImpact` never requires an existing-row lookup, so this
fake only needs to record what was added and assert its column identity/
linkage, not simulate a query.
"""

from __future__ import annotations

from market_intel.instrument_impact.service import InstrumentImpactService
from market_intel.persistence.models import (
    Event,
    ImpactConfirmationState,
    ImpactDirection,
    Instrument,
    Narrative,
    NarrativeInstrumentImpact,
    NarrativeLifecycleStatus,
    NarrativeValidityStatus,
)


class FakeAsyncSession:
    """Minimal `AsyncSession` double covering only what the service calls."""

    def __init__(self) -> None:
        self.added: list[object] = []

    def add(self, instance: object) -> None:
        self.added.append(instance)


def _narrative() -> Narrative:
    return Narrative(
        canonical_key="fomc-rate-decision",
        validity_status=NarrativeValidityStatus.CANDIDATE,
        lifecycle_status=NarrativeLifecycleStatus.EMERGING,
    )


def _rate_hike_event() -> Event:
    return Event(
        document_id=1,
        title="FOMC statement",
        type="rate_decision",
        extracted_facts=["The Committee raised the target range for the federal funds rate."],
    )


async def test_assess_and_create_stages_an_unconfirmed_impact_linked_to_the_narrative() -> None:
    session = FakeAsyncSession()
    service = InstrumentImpactService(session)  # type: ignore[arg-type]
    narrative = _narrative()
    event = _rate_hike_event()

    impact = await service.assess_and_create(narrative, [event], instrument=Instrument.NQ)

    assert isinstance(impact, NarrativeInstrumentImpact)
    assert session.added == [impact]
    # Column-identity assertion: the staged row must be linked to the actual
    # `Narrative` instance passed in (via the ORM relationship), not merely
    # to *some* narrative.
    assert impact.narrative is narrative
    assert impact.instrument is Instrument.NQ
    assert impact.direction is ImpactDirection.BEARISH
    assert impact.confirmation_state is ImpactConfirmationState.UNCONFIRMED
    assert "raised the target range" in impact.rationale


async def test_assess_and_create_defaults_to_nq_when_no_instrument_is_specified() -> None:
    session = FakeAsyncSession()
    service = InstrumentImpactService(session)  # type: ignore[arg-type]

    impact = await service.assess_and_create(_narrative(), [_rate_hike_event()])

    assert impact.instrument is Instrument.NQ


async def test_assess_and_create_never_sets_a_confirmation_state_other_than_unconfirmed() -> None:
    session = FakeAsyncSession()
    service = InstrumentImpactService(session)  # type: ignore[arg-type]
    no_signal_event = Event(
        document_id=1, title="Quarterly earnings report", type="earnings_report"
    )

    impact = await service.assess_and_create(
        _narrative(), [no_signal_event], instrument=Instrument.NQ
    )

    assert impact.confirmation_state is ImpactConfirmationState.UNCONFIRMED
    assert impact.direction is ImpactDirection.UNCERTAIN
