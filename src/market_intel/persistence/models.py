"""ORM models for persisted domain records.

Kept as a single module while the schema is small (see
`docs/architecture/domain-model.md`); split into per-concept modules if this
grows unwieldy as later tickets add `EvidencePack`,
`NarrativeInstrumentImpact`, etc.
"""

from __future__ import annotations

import enum
from datetime import UTC, datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text
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
    instrument_impacts: Mapped[list[NarrativeInstrumentImpact]] = relationship(
        back_populates="narrative"
    )


class Instrument(enum.StrEnum):
    """The closed set of instruments the platform assesses impact for.

    Per `docs/architecture/domain-model.md` (Domain Summary, Relationships),
    this is a fixed 3-value enum, not a lookup entity/table: the MVP tracks
    impact for exactly NQ, BTC, and GOLD, and adding a fourth instrument is
    a product/architecture decision, not a data-entry operation.
    """

    NQ = "nq"
    BTC = "btc"
    GOLD = "gold"


class ImpactDirection(enum.StrEnum):
    """Directional assessment of a `NarrativeInstrumentImpact`.

    Exact value set from `docs/architecture/domain-model.md` Terminology
    (`docs/product/MVP_Vision_Architecture_Decisions.md` §7): this replaces
    generic sentiment and is intentionally not collapsed to a 3-value
    bearish/neutral/bullish scale — `mixed` (opposing credible channels) and
    `uncertain` (insufficient evidence) are distinct from `neutral`
    (impact believed limited/non-directional).
    """

    STRONGLY_BEARISH = "strongly_bearish"
    BEARISH = "bearish"
    MIXED = "mixed"
    NEUTRAL = "neutral"
    BULLISH = "bullish"
    STRONGLY_BULLISH = "strongly_bullish"
    UNCERTAIN = "uncertain"


class ImpactHorizon(enum.StrEnum):
    """How long a `NarrativeInstrumentImpact`'s assessed impact stays relevant.

    Exact value set from `docs/architecture/domain-model.md` Terminology
    (`docs/product/MVP_Vision_Architecture_Decisions.md` §7).
    """

    INTRADAY = "intraday"
    MULTI_DAY = "multi_day"
    UNKNOWN = "unknown"


class ImpactConfirmationState(enum.StrEnum):
    """Confirmation state of a `NarrativeInstrumentImpact` itself.

    Distinct from `Narrative.validity_status` (`docs/architecture/domain-model.md`
    Terminology). This ticket only ever produces `UNCONFIRMED` rows; `CONFIRMED`
    is added now as an unused member (a later ticket's validation layer,
    `ADR-001`, is the only code path allowed to move a row out of
    `UNCONFIRMED`) rather than deferring the enum value itself.
    """

    UNCONFIRMED = "unconfirmed"
    CONFIRMED = "confirmed"


class NarrativeInstrumentImpact(Base):
    """An explicit, auditable relation between a `Narrative` and an `Instrument`.

    Per `docs/architecture/domain-model.md` (Invariants, Protected Semantics),
    this relation must always be an explicit assessment result — never
    inferred solely from entity/keyword presence — produced by
    `market_intel.instrument_impact`. This ticket only creates rows with
    `confirmation_state=UNCONFIRMED`; moving a row to `CONFIRMED` is reserved
    for a later ticket's validation layer.
    """

    __tablename__ = "narrative_instrument_impacts"

    id: Mapped[int] = mapped_column(primary_key=True)

    narrative_id: Mapped[int] = mapped_column(
        ForeignKey("narratives.id"), nullable=False, index=True
    )
    narrative: Mapped[Narrative] = relationship(back_populates="instrument_impacts")

    instrument: Mapped[Instrument] = mapped_column(
        Enum(
            Instrument,
            native_enum=False,
            validate_strings=True,
            length=50,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    direction: Mapped[ImpactDirection] = mapped_column(
        Enum(
            ImpactDirection,
            native_enum=False,
            validate_strings=True,
            length=50,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    # Unconstrained 0-1 float, mirroring `Event.confidence`'s convention (no
    # documented range/semantics beyond "a relevance value"; see
    # `ImplementationReport.assumptions`).
    relevance: Mapped[float] = mapped_column(Float, nullable=False)
    horizon: Mapped[ImpactHorizon] = mapped_column(
        Enum(
            ImpactHorizon,
            native_enum=False,
            validate_strings=True,
            length=50,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
    )
    rationale: Mapped[str] = mapped_column(Text, nullable=False)

    confirmation_state: Mapped[ImpactConfirmationState] = mapped_column(
        Enum(
            ImpactConfirmationState,
            native_enum=False,
            validate_strings=True,
            length=50,
            values_callable=lambda enum_cls: [member.value for member in enum_cls],
        ),
        nullable=False,
        default=ImpactConfirmationState.UNCONFIRMED,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
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
