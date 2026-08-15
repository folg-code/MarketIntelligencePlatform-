"""ORM models for persisted domain records.

Kept as a single module while the schema is small (see
`docs/architecture/domain-model.md`); split into per-concept modules if this
grows unwieldy as later tickets add `NarrativeInstrumentImpact`, etc.
"""

from __future__ import annotations

import enum
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from market_intel.persistence.db import Base


class ProcessingStatus(enum.StrEnum):
    """Lifecycle status of a `Document` through the processing pipeline.

    Only `PENDING` is used by ingestion (this ticket). Later tickets (event
    extraction and beyond) are expected to add further values as they start
    transitioning documents out of `PENDING`.
    """

    PENDING = "pending"


class Document(Base):
    """A normalized representation of one piece of ingested source content.

    Produced by an ingestion adapter (see `src/market_intel/ingestion/`).
    Raw source data is treated as immutable once stored: callers should
    insert new `Document` rows and must not mutate an existing row's
    source-derived fields (`title`, `body`, `url`, `raw_metadata`, ...)
    after it has been persisted.

    Fields follow `docs/architecture/domain-model.md` (Core Concepts ->
    Document) and `docs/product/MVP_Vision_Architecture_Decisions.md`
    (section 5, Document); no fields beyond that documented set are added
    here.
    """

    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)

    source: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(100), nullable=False)

    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    # Covers the documented "body or content reference" field: adapters may
    # populate this with full body text when the source provides it inline,
    # or with a shorter reference/summary when only that is fetched; `url`
    # always holds the canonical link back to the full source content.
    body: Mapped[str | None] = mapped_column(Text)
    url: Mapped[str] = mapped_column(String(2000), nullable=False, unique=True)
    language: Mapped[str | None] = mapped_column(String(20))

    raw_metadata: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    processing_status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, native_enum=False, validate_strings=True, length=50),
        nullable=False,
        default=ProcessingStatus.PENDING,
    )

    events: Mapped[list[Event]] = relationship(back_populates="document")


class Event(Base):
    """Something extracted from a `Document` by event extraction.

    `extracted_facts` (what the source literally states) is kept
    structurally separate from `source_claims` (what the source asserts or
    frames) and from any model inference about meaning/impact — separate
    columns, not just a prompt convention — per
    `docs/architecture/domain-model.md` (Core Concepts, Invariants).
    Producing an `Event` is a low-risk semantic transformation an LLM may
    perform independently (`docs/architecture/decisions/ADR-001-llm-decision-boundaries.md`);
    the `Event` itself remains a candidate consumed by later pipeline
    stages (narrative assignment, validation layer), not a finalized
    protected outcome, so no validity/status column is added here.

    Fields follow `docs/product/MVP_Vision_Architecture_Decisions.md`
    (section 5, Event), with two judgment calls (see
    `ImplementationReport.assumptions`):
    - `source_ids` is represented as a single `document_id` foreign key
      rather than a list/junction table, since this ticket's extraction is
      one `Document` in, N `Event`s out.
    - `extraction_model` is an obviously-cheap traceability field (which
      model produced this `Event`), not the full LLM-run reproducibility
      model from section 10, which is out of Milestone 1 scope.
    """

    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)

    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), nullable=False, index=True)
    document: Mapped[Document] = relationship(back_populates="events")

    # No documented enum of event types exists yet; kept as free-form,
    # LLM-derived text rather than inventing an enum not backed by product
    # decision (see ImplementationReport.assumptions).
    type: Mapped[str | None] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    # Best-effort; left null when the source text does not state a specific
    # date/time for the event.
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    entities: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    topics: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    extracted_facts: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    source_claims: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    # No documented range/semantics beyond "a confidence value"; modeled as
    # an unconstrained 0-1 float (see ImplementationReport.assumptions).
    confidence: Mapped[float | None] = mapped_column(Float)

    extraction_model: Mapped[str | None] = mapped_column(String(200))

    # `Event 0..1 --1 NarrativeEvent` per domain-model.md Relationships: an
    # Event has at most one NarrativeEvent (enforced by the unique
    # constraint on `NarrativeEvent.event_id` below).
    narrative_event: Mapped[NarrativeEvent | None] = relationship(back_populates="event")


class NarrativeValidityStatus(enum.StrEnum):
    """Confirmation state of a `Narrative` (`domain-model.md` Terminology).

    Only `CANDIDATE` is produced by this ticket (initial candidate
    creation). Moving to `CONFIRMED` is a protected outcome that must pass
    through the validation layer
    (`docs/architecture/decisions/ADR-001-llm-decision-boundaries.md`) and
    is out of this ticket's scope; a later ticket adds that value and the
    logic that sets it.
    """

    CANDIDATE = "candidate"


class NarrativeLifecycleStatus(enum.StrEnum):
    """Lifecycle/dynamics state of a `Narrative` (`domain-model.md` Core Concepts).

    Only `EMERGING` is used by this ticket, as the fixed initial state of
    a newly created candidate `Narrative`; no automated transition logic
    (e.g. emerging -> accelerating -> confirmed) exists yet. Later
    tickets add further values and the transition logic behind them.
    """

    EMERGING = "emerging"


class Narrative(Base):
    """A market narrative identified by a semantic `canonical_key`.

    Per `docs/architecture/domain-model.md` (Invariants, Protected
    Semantics), identity is always `canonical_key`-based, never a
    transient cluster-hash of the events grouped in one processing run;
    see `market_intel.narrative_engine.canonical_key` for the current
    derivation formula. This ticket only creates `Narrative` rows via
    initial candidate creation (`validity_status=candidate`,
    `lifecycle_status=emerging`); no merge/split or automated lifecycle
    transition exists yet.
    """

    __tablename__ = "narratives"

    id: Mapped[int] = mapped_column(primary_key=True)

    canonical_key: Mapped[str] = mapped_column(String(64), nullable=False, unique=True, index=True)

    validity_status: Mapped[NarrativeValidityStatus] = mapped_column(
        Enum(NarrativeValidityStatus, native_enum=False, validate_strings=True, length=50),
        nullable=False,
        default=NarrativeValidityStatus.CANDIDATE,
    )
    lifecycle_status: Mapped[NarrativeLifecycleStatus] = mapped_column(
        Enum(NarrativeLifecycleStatus, native_enum=False, validate_strings=True, length=50),
        nullable=False,
        default=NarrativeLifecycleStatus.EMERGING,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    narrative_events: Mapped[list[NarrativeEvent]] = relationship(back_populates="narrative")

    # `Narrative 1 --1 EvidencePack` per domain-model.md Relationships: this
    # is literal, not conditional (see EvidencePack docstring) — every
    # Narrative is expected to have exactly one EvidencePack, created by
    # `market_intel.evidence.service.EvidencePackService` alongside the
    # Narrative itself.
    evidence_pack: Mapped[EvidencePack | None] = relationship(
        back_populates="narrative", uselist=False
    )


class NarrativeEvent(Base):
    """The assignment of an `Event` to a `Narrative`, produced by the narrative engine.

    No status/validity column here by design: rejection/override
    semantics for an event assignment are deferred to a later ticket
    alongside the general human-override mechanism
    (`docs/architecture/domain-model.md` Core Concepts). `event_id` is
    unique because an `Event` is assigned to at most one `Narrative`
    (domain-model.md Relationships: `Event 0..1 --1 NarrativeEvent`).
    """

    __tablename__ = "narrative_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    narrative_id: Mapped[int] = mapped_column(
        ForeignKey("narratives.id"), nullable=False, index=True
    )
    narrative: Mapped[Narrative] = relationship(back_populates="narrative_events")

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"), nullable=False, unique=True)
    event: Mapped[Event] = relationship(back_populates="narrative_event")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )


class EvidencePack(Base):
    """The aggregated evidence for a `Narrative`: source traceability plus an
    independent-source count (`docs/architecture/domain-model.md` Core
    Concepts).

    `narrative_id` is unique + not-null, enforcing the literal (not
    conditional) `Narrative 1 --1 EvidencePack` relationship
    (domain-model.md Relationships): an `EvidencePack` is created together
    with its `Narrative` and rebuilt/grown as further `NarrativeEvent`s are
    assigned, by `market_intel.evidence.service.EvidencePackService`. No
    redundant join table for traceability — it is derived on demand via the
    existing `Narrative -> NarrativeEvent -> Event -> Document` chain (see
    `market_intel.evidence.aggregation`), not persisted separately.

    Per the Invariants/Protected Semantics in domain-model.md ("An
    EvidencePack cannot exist without source traceability"),
    `EvidencePackService` never persists a row here backed by zero
    traceable Documents; this model itself has no way to express that
    constraint declaratively, so it is enforced at the business-logic layer
    (`EvidencePackService.build_or_update`), not by a DB-level CHECK.
    """

    __tablename__ = "evidence_packs"

    id: Mapped[int] = mapped_column(primary_key=True)

    narrative_id: Mapped[int] = mapped_column(
        ForeignKey("narratives.id"), nullable=False, unique=True, index=True
    )
    narrative: Mapped[Narrative] = relationship(back_populates="evidence_pack")

    independent_source_count: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
