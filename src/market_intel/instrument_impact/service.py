"""Async orchestrator persisting a deterministic instrument-impact assessment.

This is the only piece of `instrument_impact` that touches persistence; it
contains no LLM/HTTP client usage, consistent with
`docs/architecture/overview.md` (business/domain logic does not call
external APIs or the LLM directly).
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from market_intel.instrument_impact.assessment import assess_impact
from market_intel.persistence.models import (
    Event,
    ImpactConfirmationState,
    Instrument,
    Narrative,
    NarrativeInstrumentImpact,
)


class InstrumentImpactService:
    """Assesses and persists `NarrativeInstrumentImpact` rows for a `Narrative`."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def assess_and_create(
        self, narrative: Narrative, events: list[Event], *, instrument: Instrument = Instrument.NQ
    ) -> NarrativeInstrumentImpact:
        """Assess `instrument`'s impact from `events` and stage a new impact row.

        `events` should be `narrative`'s already-assigned `Event`s. The new
        `NarrativeInstrumentImpact` always starts `confirmation_state =
        UNCONFIRMED` (`docs/architecture/domain-model.md` Terminology); no
        code path here sets anything else. The new object is added to the
        session but not committed; the caller owns the transaction boundary.
        No `EvidencePack` is required to exist first — that gate applies to
        confirming a conclusion, not to creating an unconfirmed draft.
        """
        assessment = assess_impact(events, instrument=instrument)
        impact = NarrativeInstrumentImpact(
            narrative=narrative,
            instrument=assessment.instrument,
            direction=assessment.direction,
            relevance=assessment.relevance,
            horizon=assessment.horizon,
            rationale=assessment.rationale,
            confirmation_state=ImpactConfirmationState.UNCONFIRMED,
        )
        self._session.add(impact)
        return impact
