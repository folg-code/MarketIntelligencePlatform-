"""Unit tests for `EvidencePackService` against a fake session double.

Deliberately avoids a live database: `FakeAsyncSession` below only
implements the two `AsyncSession` operations the service actually calls
(`scalar` for the existing-`EvidencePack` lookup, `add` for staging a new
row), mirroring `tests/narrative_engine/test_service.py`'s
`FakeAsyncSession`. Real `select`/session wiring is exercised by the
migration verification described in `ImplementationReport.checks_run`.

`FakeAsyncSession.scalar` asserts the comparison filters on
`EvidencePack.narrative_id` specifically (table + column identity, not
just that *some* literal value is bound) and uses equality, applying the
Wave 1 Ticket 4 review finding proactively rather than repeating that gap.
"""

from __future__ import annotations

import operator

import pytest

from market_intel.evidence.service import EvidencePackService, EvidenceTraceabilityError
from market_intel.persistence.models import Event, EvidencePack, Narrative, NarrativeEvent


class FakeAsyncSession:
    """Minimal `AsyncSession` double covering only what the service calls."""

    def __init__(self, *, existing: EvidencePack | None = None) -> None:
        self._existing = existing
        self.added: list[object] = []

    async def scalar(self, statement: object) -> EvidencePack | None:
        whereclause = statement.whereclause  # type: ignore[attr-defined]
        left = whereclause.left
        assert left.table is EvidencePack.__table__ and left.name == "narrative_id", (
            "expected the lookup to filter on EvidencePack.narrative_id, got "
            f"{left.table.name}.{left.name}"
        )
        assert whereclause.operator is operator.eq, (
            f"expected an equality comparison, got {whereclause.operator!r}"
        )
        narrative_id = whereclause.right.value
        if self._existing is not None and self._existing.narrative_id == narrative_id:
            return self._existing
        return None

    def add(self, instance: object) -> None:
        self.added.append(instance)


def _persisted_narrative(narrative_id: int, *document_ids: int) -> Narrative:
    """A `Narrative` standing in for one already flushed/committed (has an id)."""
    narrative = Narrative(canonical_key="unused-for-service-tests")
    narrative.id = narrative_id
    narrative.narrative_events = [
        NarrativeEvent(event=Event(document_id=document_id, title="unused"))
        for document_id in document_ids
    ]
    return narrative


async def test_creates_a_new_evidence_pack_when_none_exists_yet() -> None:
    session = FakeAsyncSession()
    service = EvidencePackService(session)  # type: ignore[arg-type]
    narrative = _persisted_narrative(1, 10, 20)

    pack = await service.build_or_update(narrative)

    assert pack.narrative is narrative
    assert pack.independent_source_count == 2
    assert session.added == [pack]


async def test_updates_the_existing_evidence_pack_instead_of_creating_a_new_one() -> None:
    existing_pack = EvidencePack(narrative_id=1, independent_source_count=1)
    session = FakeAsyncSession(existing=existing_pack)
    service = EvidencePackService(session)  # type: ignore[arg-type]
    narrative = _persisted_narrative(1, 10, 20, 30)

    pack = await service.build_or_update(narrative)

    assert pack is existing_pack
    assert pack.independent_source_count == 3
    assert session.added == []


async def test_growing_narrative_events_tracing_to_the_same_document_keeps_count_at_one() -> None:
    existing_pack = EvidencePack(narrative_id=1, independent_source_count=1)
    session = FakeAsyncSession(existing=existing_pack)
    service = EvidencePackService(session)  # type: ignore[arg-type]
    narrative = _persisted_narrative(1, 10, 10, 10)

    pack = await service.build_or_update(narrative)

    assert pack.independent_source_count == 1


async def test_refuses_to_build_an_evidence_pack_with_zero_traceable_documents() -> None:
    session = FakeAsyncSession()
    service = EvidencePackService(session)  # type: ignore[arg-type]
    narrative = _persisted_narrative(1)

    with pytest.raises(EvidenceTraceabilityError):
        await service.build_or_update(narrative)

    assert session.added == []
