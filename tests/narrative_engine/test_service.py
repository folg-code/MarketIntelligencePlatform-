"""Unit tests for `NarrativeAssignmentService` against a fake session double.

Deliberately avoids a live database: `FakeAsyncSession` below only
implements the two `AsyncSession` operations the service actually calls
(`scalar` for the canonical_key lookup, `add` for staging new rows), reading
the bound `canonical_key` value directly off the `select(...).where(...)`
statement. This keeps the narrative-engine's own orchestration behavior
testable deterministically and independent of a live Postgres instance
(`docs/architecture/ai-and-evidence.md`, Testing Expectations), while the
real `select`/session wiring is exercised by the migration verification
described in `ImplementationReport.checks_run`.

`FakeAsyncSession.scalar` also asserts the comparison filters on
`Narrative.canonical_key` specifically (not just that *some* literal value
is bound), so these tests fail loudly if `service.py` ever filtered on the
wrong column or the wrong operator (Wave 1 Ticket 4 review finding).
"""

from __future__ import annotations

import operator

from market_intel.narrative_engine.service import NarrativeAssignmentService
from market_intel.persistence.models import (
    Event,
    Narrative,
    NarrativeEvent,
    NarrativeValidityStatus,
)


class FakeAsyncSession:
    """Minimal `AsyncSession` double covering only what the service calls."""

    def __init__(self) -> None:
        self._by_key: dict[str, Narrative] = {}
        self.added: list[object] = []

    async def scalar(self, statement: object) -> Narrative | None:
        whereclause = statement.whereclause  # type: ignore[attr-defined]
        left = whereclause.left
        assert left.table is Narrative.__table__ and left.name == "canonical_key", (
            "expected the lookup to filter on Narrative.canonical_key, got "
            f"{left.table.name}.{left.name}"
        )
        assert whereclause.operator is operator.eq, (
            f"expected an equality comparison, got {whereclause.operator!r}"
        )
        canonical_key = whereclause.right.value
        return self._by_key.get(canonical_key)

    def add(self, instance: object) -> None:
        self.added.append(instance)
        if isinstance(instance, Narrative):
            self._by_key[instance.canonical_key] = instance


def _event(**overrides: object) -> Event:
    defaults: dict[str, object] = {
        "title": "unused for key derivation",
        "type": "rate_decision",
        "entities": ["Federal Reserve"],
        "topics": ["monetary_policy"],
    }
    defaults.update(overrides)
    return Event(**defaults)


async def test_two_events_with_the_same_semantic_identity_share_one_narrative() -> None:
    session = FakeAsyncSession()
    service = NarrativeAssignmentService(session)  # type: ignore[arg-type]

    first = await service.assign(_event(title="first"))
    second = await service.assign(_event(title="second"))

    assert first.created_narrative is True
    assert second.created_narrative is False
    assert second.narrative is first.narrative

    added_narratives = [item for item in session.added if isinstance(item, Narrative)]
    added_narrative_events = [item for item in session.added if isinstance(item, NarrativeEvent)]
    assert added_narratives == [first.narrative]
    assert {narrative_event.event.title for narrative_event in added_narrative_events} == {
        "first",
        "second",
    }


async def test_event_with_distinct_semantic_identity_creates_its_own_candidate_narrative() -> None:
    session = FakeAsyncSession()
    service = NarrativeAssignmentService(session)  # type: ignore[arg-type]

    first = await service.assign(_event(type="rate_decision"))
    second = await service.assign(_event(type="earnings_report"))

    assert first.created_narrative is True
    assert second.created_narrative is True
    assert first.narrative is not second.narrative
    assert second.narrative.validity_status is NarrativeValidityStatus.CANDIDATE

    added_narratives = [item for item in session.added if isinstance(item, Narrative)]
    assert len(added_narratives) == 2
