"""Async orchestrator wiring `Event` -> `canonical_key` lookup -> assignment decision.

This is the only piece of `narrative_engine` that touches persistence; it
contains no LLM/HTTP client usage, consistent with
`docs/architecture/overview.md` (business/domain logic does not call
external APIs or the LLM directly).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from market_intel.narrative_engine.assignment import AssignmentResult, assign_event
from market_intel.narrative_engine.canonical_key import compute_canonical_key
from market_intel.persistence.models import Event, Narrative


class NarrativeAssignmentService:
    """Assigns extracted `Event`s to `Narrative`s via `canonical_key` matching."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def assign(self, event: Event) -> AssignmentResult:
        """Assign `event` to its matching `Narrative`, creating one if none exists yet.

        New objects (a new `Narrative` and/or the `NarrativeEvent`) are
        added to the session but not committed; the caller owns the
        transaction boundary.
        """
        canonical_key = compute_canonical_key(event)
        matching_narrative = await self._session.scalar(
            select(Narrative).where(Narrative.canonical_key == canonical_key)
        )

        result = assign_event(
            event, canonical_key=canonical_key, matching_narrative=matching_narrative
        )
        if result.created_narrative:
            self._session.add(result.narrative)
        self._session.add(result.narrative_event)
        return result
