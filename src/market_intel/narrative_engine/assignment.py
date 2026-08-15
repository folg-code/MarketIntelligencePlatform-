"""Pure narrative-candidate assignment decision.

Given an `Event` and whichever `Narrative` (if any) already carries its
`canonical_key`, decide whether to append a `NarrativeEvent` to that
existing `Narrative` or to create a brand-new one. Kept free of any
database/session/LLM/HTTP dependency so the decision itself can be unit
tested deterministically (`docs/architecture/ai-and-evidence.md`, Testing
Expectations); `market_intel.narrative_engine.service` is the thin async
orchestrator that looks up the matching `Narrative` and calls this module.

Per the delegation contract for this ticket, no code path here ever sets
`validity_status` to anything other than `candidate`, and nothing here
performs a merge/split or an automated lifecycle transition beyond the
initial candidate creation.
"""

from __future__ import annotations

from dataclasses import dataclass

from market_intel.persistence.models import (
    Event,
    Narrative,
    NarrativeEvent,
    NarrativeLifecycleStatus,
    NarrativeValidityStatus,
)


@dataclass(frozen=True)
class AssignmentResult:
    """Outcome of assigning one `Event` to a `Narrative`."""

    narrative: Narrative
    narrative_event: NarrativeEvent
    created_narrative: bool


def assign_event(
    event: Event, *, canonical_key: str, matching_narrative: Narrative | None
) -> AssignmentResult:
    """Assign `event` to `matching_narrative`, or create a new candidate `Narrative`.

    `canonical_key` must be `compute_canonical_key(event)` and
    `matching_narrative` must already be the `Narrative` (if any) whose
    `canonical_key` equals it — both are supplied by the caller (see
    `market_intel.narrative_engine.service`) so this function never
    computes a key or performs a lookup itself, keeping it a pure,
    database-free decision.
    """
    if matching_narrative is not None:
        narrative = matching_narrative
        created_narrative = False
    else:
        narrative = Narrative(
            canonical_key=canonical_key,
            validity_status=NarrativeValidityStatus.CANDIDATE,
            lifecycle_status=NarrativeLifecycleStatus.EMERGING,
        )
        created_narrative = True

    narrative_event = NarrativeEvent(narrative=narrative, event=event)
    return AssignmentResult(
        narrative=narrative, narrative_event=narrative_event, created_narrative=created_narrative
    )
