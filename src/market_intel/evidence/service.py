"""Async service creating/updating a Narrative's `EvidencePack`.

This is the only piece of `market_intel.evidence` that touches persistence;
it contains no LLM/HTTP client usage, consistent with
`docs/architecture/overview.md` (business/domain logic does not call
external APIs or the LLM directly).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from market_intel.evidence.aggregation import collect_traceable_document_ids
from market_intel.persistence.models import EvidencePack, Narrative


class EvidenceTraceabilityError(ValueError):
    """Raised when an `EvidencePack` would be built with zero traceable Documents.

    Per `docs/architecture/domain-model.md` (Invariants, Protected
    Semantics): "An EvidencePack cannot exist without source traceability."
    In normal pipeline operation this is unreachable — the narrative
    engine's `assign_event` never creates a `Narrative` without also
    creating its first `NarrativeEvent` — but `EvidencePackService` refuses
    to persist a zero-count `EvidencePack` rather than silently producing
    one if it is ever invoked outside that normal sequence.
    """


class EvidencePackService:
    """Builds/rebuilds the `EvidencePack` for a `Narrative`.

    Callers must pass a `Narrative` whose `narrative_events` (and each
    `.event`) are already loaded (e.g. via `selectinload`); this service
    performs no eager-loading of its own, mirroring
    `market_intel.narrative_engine.service.NarrativeAssignmentService`'s
    thin-orchestrator role — it owns only the one query needed to find an
    existing `EvidencePack` row, plus staging the new/updated row.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def build_or_update(self, narrative: Narrative) -> EvidencePack:
        """Create or update `narrative`'s `EvidencePack` with a fresh count.

        Raises:
            EvidenceTraceabilityError: if `narrative` has zero traceable
                Documents (see that class's docstring).

        The new/updated row is added to the session but not committed;
        the caller owns the transaction boundary, mirroring
        `NarrativeAssignmentService.assign`.
        """
        document_ids = collect_traceable_document_ids(narrative)
        if not document_ids:
            raise EvidenceTraceabilityError(
                f"refusing to build an EvidencePack for narrative_id={narrative.id!r} "
                "with zero traceable Documents"
            )
        independent_source_count = len(document_ids)

        existing = await self._session.scalar(
            select(EvidencePack).where(EvidencePack.narrative_id == narrative.id)
        )
        if existing is not None:
            existing.independent_source_count = independent_source_count
            return existing

        evidence_pack = EvidencePack(
            narrative=narrative, independent_source_count=independent_source_count
        )
        self._session.add(evidence_pack)
        return evidence_pack
