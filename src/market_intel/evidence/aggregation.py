"""Pure evidence aggregation: distinct traceable Documents for a Narrative.

Given a `Narrative` whose `narrative_events` (and each `NarrativeEvent.event`)
are already loaded, compute the distinct set of Document ids reachable via
the `Narrative -> NarrativeEvent -> Event -> Document` chain
(`docs/architecture/domain-model.md`, Relationships). Kept free of any
database/session dependency so aggregation itself can be unit tested
deterministically, mirroring the
`narrative_engine.assignment` / `narrative_engine.service` split
(`docs/architecture/ai-and-evidence.md`, Testing Expectations);
`market_intel.evidence.service` is the thin async service that loads a
`Narrative`'s events and calls this module.

Per the delegation contract for this ticket, no syndication-detection logic
lives here: a distinct `document_id` is treated as one independent source
(`docs/architecture/domain-model.md`, Independent-source counting), which is
correct for the current single-source milestone.
"""

from __future__ import annotations

from market_intel.persistence.models import Narrative


def collect_traceable_document_ids(narrative: Narrative) -> frozenset[int]:
    """Return the distinct Document ids reachable from `narrative`'s events.

    Reads `narrative_event.event.document_id` for each of `narrative`'s
    already-loaded `narrative_events`; the caller (see
    `EvidencePackService`) is responsible for ensuring `narrative_events`
    and each `.event` are loaded before calling this function, which
    issues no queries and performs no lazy loading itself.
    """
    return frozenset(
        narrative_event.event.document_id for narrative_event in narrative.narrative_events
    )


def compute_independent_source_count(narrative: Narrative) -> int:
    """Return the independent-source count for `narrative`.

    Equivalent to `COUNT(DISTINCT document_id)` over Documents reachable
    from `narrative`'s `NarrativeEvent`s: multiple `NarrativeEvent`s/`Event`s
    tracing back to the same `Document` count once, not once each, per
    `docs/architecture/domain-model.md` (Independent-source counting).
    """
    return len(collect_traceable_document_ids(narrative))
