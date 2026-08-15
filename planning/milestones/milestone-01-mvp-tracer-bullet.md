# Milestone 1: MVP Tracer-Bullet Pipeline

## Outcome

Prove the full pipeline shape end-to-end for a thin vertical slice — one
ingestion source, one narrative, one instrument — before investing in the
full MVP breadth. This validates, with running code rather than assumption,
the three accepted architecture decisions (`ADR-001`, `ADR-002`, `ADR-003`)
and the domain model (`docs/architecture/domain-model.md`).

## Scope

### Included

- One ingestion adapter (Federal Reserve/FOMC, chosen as the simplest
  Tier 1/official-source structure) producing `Document` records.
- Event extraction via the local LLM through Ollama (`ADR-002`), producing
  `Event`s with `extracted_facts` and `source_claims` kept separate.
- Narrative candidate assignment using semantic `canonical_key` identity
  (not cluster-hash), producing at least one `Narrative` and its
  `NarrativeEvent`s.
- `EvidencePack` construction with source traceability and independent-source
  counting (trivially 1 for a single-source slice, but implemented as a real
  count, not hardcoded).
- `NarrativeInstrumentImpact` assessment for at least one of NQ/BTC/GOLD,
  with explicit direction/relevance/horizon and rationale — never inferred
  from keywords alone.
- The LLM decision-boundary validation layer (`ADR-001`): at least the
  `validity_status = confirmed` transition must pass through deterministic
  validation, not be finalized directly from raw LLM output.
- Persistence via SQLAlchemy (async) + Alembic migrations on PostgreSQL
  (`ADR-003`).
- In-process APScheduler running the 5-minute processing cycle
  (ingest -> extract -> assign -> rebuild EvidencePack -> recalc state)
  (`ADR-003`).
- A minimal server-rendered (FastAPI + Jinja2 + htmx) dashboard page showing
  the one narrative, its EvidencePack (with a link back to the source
  Document), and its instrument impact (`ADR-003`).

### Excluded

- Full source breadth (BLS, SEC, additional news/RSS sources) — Milestone 2.
- Alert feed and alert rule evaluation — Milestone 2.
- Human override controls (watch/mute/rename/mark invalid/reject/restore) —
  Milestone 2.
- Morning Market Brief formatting (Macro/NQ/BTC/GOLD/Watch Today sections) —
  Milestone 2.
- Narrative dynamics metrics (`attention_score`, `strength`, `velocity`,
  `momentum`) — not required to prove the pipeline shape.
- `NarrativeEpisode`, `NarrativeRelation` — explicitly post-MVP schema
  placeholders, not needed for this slice.
- Full LLM run reproducibility metadata model — capture only what is needed
  to demonstrate the validation layer works; the complete audit model is
  Milestone 2 or later.
- Multi-narrative / multi-instrument dashboard polish.

## Acceptance Expectations

- A Fed/FOMC document ingested during a real (or manually triggered)
  5-minute cycle flows automatically through extraction, narrative
  assignment, EvidencePack construction, and instrument impact assessment
  without manual intervention between stages.
- The resulting Narrative has a stable `canonical_key`, an associated
  `EvidencePack` with working source traceability (a link/reference back to
  the originating Document), and at least one `NarrativeInstrumentImpact`
  with non-empty rationale.
- Setting `validity_status = confirmed` (or any other `ADR-001`-protected
  outcome exercised by this slice) is demonstrably gated by the validation
  layer — there is a test proving raw/unvalidated LLM output alone cannot
  finalize it.
- The dashboard page renders the narrative, its evidence, and its instrument
  impact, and a user can navigate from the dashboard to the source document.
- The full cycle (one document in, one displayed narrative out) completes
  within the 5-minute cycle window on the target local machine.

## Dependencies

- `docs/architecture/decisions/ADR-001-llm-decision-boundaries.md` (Accepted)
- `docs/architecture/decisions/ADR-002-local-llm-via-ollama.md` (Accepted)
- `docs/architecture/decisions/ADR-003-mvp-technical-stack-persistence-scheduler-deployment-dashboard.md`
  (Accepted)
- Local environment: Ollama with a working model, reachable PostgreSQL
  instance (set up as part of Wave 1).

## Risks

- Local LLM (Ollama) extraction quality/latency may be insufficient; this is
  an explicit, accepted risk under `ADR-002` and is exactly what this
  milestone is designed to surface early.
- Pipeline stage timing (including local LLM inference) may not fit
  comfortably in the 5-minute cycle on the target hardware.
- The domain model's field/relationship shape (`docs/architecture/domain-model.md`)
  may need adjustment once real persistence and extraction code is written;
  expect Alembic migration churn during this milestone.

## Decisions

None yet beyond the referenced ADRs. Any new architecture decision required
during execution routes through the `architecture-change` workflow, not this
milestone document.

## Status

**APPROVED** — approved by Human/product authority. Wave 1 execution is
dispatched; see `planning/waves/wave-01-foundation-and-tracer-slice.md` and
`planning/current.md`.
