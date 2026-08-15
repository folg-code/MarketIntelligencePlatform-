# Architecture Overview

## Purpose

Describe the project-specific system architecture at a level useful for
implementation, review, and future change.

This document should capture accepted architecture, not speculative design
notes.

## System Summary

The Market Intelligence Platform is a single-machine, evidence-backed market
narrative intelligence system. It ingests documents from a small set of
reliable sources, extracts events with an LLM, groups events into narratives
using a semantic identity, builds auditable EvidencePacks, assesses
instrument impact for NQ/BTC/GOLD, and surfaces the result through an in-app
alert feed and a server-rendered dashboard. It is not a sentiment-analysis
system, a prediction engine, or a trading-signal generator.

## Major Components

- **Ingestion adapters** — source-specific fetch/parse/normalize of raw
  source content into `Document` records.
- **Event extraction** — LLM-assisted extraction of `extracted_facts` and
  `source_claims` from Documents.
- **Narrative engine** — assigns extracted events to `NarrativeEvent`s,
  manages narrative lifecycle/dynamics state, using semantic (`canonical_key`)
  identity.
- **EvidencePack builder** — aggregates evidence for a narrative, performs
  independent-source counting, enforces source traceability.
- **Instrument impact assessor** — produces `NarrativeInstrumentImpact`
  relations (direction/relevance/horizon) for NQ, BTC, GOLD.
- **Validation layer** — deterministic/rule-based checks and human
  confirmation gate that LLM output must pass before finalizing protected
  outcomes (see `docs/architecture/decisions/ADR-001-llm-decision-boundaries.md`).
- **Alert evaluator** — evaluates alert rules against narrative/evidence
  state changes and writes alerts.
- **API layer (FastAPI)** — request/response contracts, override enforcement,
  serves the dashboard.
- **Dashboard** — server-rendered (Jinja2 + htmx) views: brief, active
  narratives, NQ/BTC/GOLD exposure, alert feed, narrative detail, override
  controls.
- **Scheduler** — in-process APScheduler jobs driving the 5-minute processing
  cycle and the (separately scheduled/on-demand) Morning Brief job.
- **Persistence** — PostgreSQL, accessed via SQLAlchemy (async engine), with
  Alembic-managed migrations.

## Responsibilities And Boundaries

```text
Ingestion adapters          -> Source-specific fetch/parse/normalize into Document
Event extraction            -> LLM-assisted Event extraction (extracted_facts, source_claims)
Narrative engine             -> NarrativeEvent assignment, lifecycle/dynamics state
EvidencePack builder        -> evidence aggregation, independent-source counting
Instrument impact assessor  -> NarrativeInstrumentImpact (direction/relevance/horizon)
API layer (FastAPI)         -> request/response contracts, override enforcement
```

Business/domain logic (narrative engine, EvidencePack builder, instrument
impact assessor) does not call external APIs or the LLM directly; it consumes
already-normalized Documents and already-extracted facts/claims produced by
the ingestion and event-extraction components. External integrations are
isolated behind those two component boundaries plus the LLM client used by
event extraction and narrative candidate generation.

LLM output crossing into any of the outcomes listed in
`docs/architecture/decisions/ADR-001-llm-decision-boundaries.md` must pass
through the validation layer; no other component may finalize those outcomes
directly from raw LLM output.

## Data Flow

```text
Sources -> Documents -> Event Extraction -> Narrative Candidates
        -> EvidencePack -> Validated Narratives -> Instrument Impact
        -> Brief / Alerts / Dashboard
```

Processing cycle (every 5 minutes, via APScheduler): ingest -> extract events
-> update narrative candidates -> rebuild affected EvidencePacks ->
recalculate narrative state -> evaluate alert rules. The Morning Brief is a
separate job (on demand or on its own configurable schedule), not part of the
5-minute cycle.

## External Integrations

- MVP source ingestion: Federal Reserve/FOMC, BLS, SEC, and two or three
  selected news/RSS sources.
- Local LLM via Ollama for event extraction and narrative candidate
  generation (see
  `docs/architecture/decisions/ADR-002-local-llm-via-ollama.md`). No cloud
  LLM API is used in the MVP pipeline.
- PostgreSQL as the system of record.
- No market-data-confirmation integration, no Telegram/email/webhook alert
  delivery, and no Kafka/distributed task queue in MVP (see PRD Scope
  Excluded).

## Key Technical Decisions

- LLM decision boundaries / validation layer:
  `docs/architecture/decisions/ADR-001-llm-decision-boundaries.md`.
- Local LLM via Ollama:
  `docs/architecture/decisions/ADR-002-local-llm-via-ollama.md`.
- MVP technical stack (deployment target, persistence via SQLAlchemy async +
  Alembic, in-process APScheduler, Jinja2 + htmx dashboard):
  `docs/architecture/decisions/ADR-003-mvp-technical-stack-persistence-scheduler-deployment-dashboard.md`.

## Constraints

- Single local machine for MVP deployment: no built-in horizontal scaling or
  high availability; pipeline stage timing (including local LLM inference)
  must fit within the 5-minute processing cycle on that hardware.
- No Kafka, no distributed task queue, no multi-cadence scheduling beyond the
  5-minute cycle plus the separately scheduled Morning Brief job.
- No custom ML models; event extraction and narrative candidate generation
  rely on the local LLM via Ollama.
- All persistence code must use the async SQLAlchemy engine; Alembic
  migrations are the only accepted path for persisted schema changes.
- Dashboard interactivity is limited to what Jinja2 + htmx server-rendering
  supports; no SPA framework, no candlestick charts/orderflow/heatmaps/full
  economic calendar UI (excluded MVP scope).
- Only in-app alerts in MVP; no external alert delivery channel integrations.

## Risks And Trade-Offs

- Local LLM quality/latency (via Ollama) may be weaker or slower than a
  frontier cloud API; this is an accepted MVP trade-off tracked in
  `ADR-002-local-llm-via-ollama.md` and must be revisited if extraction
  quality proves insufficient.
- Single-machine deployment concentrates all load (ingestion, LLM inference,
  database, web/dashboard) on one host; resource contention is a design
  constraint for pipeline timing, not something to be solved by ad hoc
  scaling.
- In-process scheduling has no built-in cross-process job coordination; if
  the scheduler runs in more than one process, job ownership must be
  explicit to avoid duplicate cycle runs.
- Server-rendered dashboard trades richer client-side interactivity for
  operational simplicity; this is acceptable for MVP scope but constrains
  future dashboard feature requests.

## References

- `docs/product/PRD.md`
- `docs/architecture/domain-model.md`
- `docs/architecture/ai-and-evidence.md`
- `docs/architecture/decisions/ADR-001-llm-decision-boundaries.md`
- `docs/architecture/decisions/ADR-002-local-llm-via-ollama.md`
- `docs/architecture/decisions/ADR-003-mvp-technical-stack-persistence-scheduler-deployment-dashboard.md`
