# ADR-003: MVP Technical Stack — Persistence, Scheduler, Deployment Target, Dashboard

## Status

Accepted

## Context

The PRD's "Unresolved Questions" left four related infrastructure choices
open, resolved via a `grill-me` discovery session with the product owner:
deployment target, persistence/data-access layer, scheduler mechanism for the
5-minute processing cycle, and dashboard frontend approach. These four are
grouped into one ADR because they are all "how the MVP is built and run"
choices that share a single driving constraint (run simply, on one machine,
with minimal moving parts) rather than four independent architectural
concerns. The LLM provider choice is deliberately kept separate (see
`ADR-002-local-llm-via-ollama.md`) since it concerns pipeline quality/cost
trade-offs rather than infrastructure shape.

The PRD explicitly excludes Kafka, custom ML infrastructure, and complex
multi-cadence scheduling from MVP scope, and requires only in-app alerts (no
external delivery channels) — all consistent with a deliberately small
infrastructure footprint.

## Decision

### Deployment target (MVP)

The platform runs locally on a single machine (not cloud/VPS) for the MVP.
This is treated as an accepted assumption/constraint for MVP, not a final
post-MVP decision — it should be re-evaluated if/when the product moves past
MVP validation.

### Persistence / data-access layer

PostgreSQL is the system of record. Data access uses SQLAlchemy with an
async engine, and schema migrations are managed with Alembic. No direct
raw-SQL-only access layer and no alternative ORM.

### Scheduler

The 5-minute processing cycle (ingest -> extract events -> update narrative
candidates -> rebuild affected EvidencePacks -> recalculate narrative state
-> evaluate alert rules) is driven by APScheduler running in-process, either
inside the FastAPI app or a dedicated worker process. The Morning Brief job
(on demand or on a separate configurable schedule) also runs via APScheduler.
Explicitly excluded: Kafka, any distributed task queue, and multi-cadence
scheduling beyond the one 5-minute cycle plus the separate brief job.

### Dashboard frontend

The dashboard is server-rendered via FastAPI with Jinja2 templates and htmx
for partial updates/interactivity. Explicitly not a React (or other) single
page application and not Streamlit.

## Consequences

- Single-machine deployment means the platform has no built-in horizontal
  scaling or high availability in MVP; the 5-minute cycle, LLM inference
  (`ADR-002`), PostgreSQL, and the web/dashboard process all compete for the
  same local resources. Pipeline stage timing must stay compatible with the
  5-minute cadence on that hardware.
- Async SQLAlchemy + Alembic means all persistence code in the pipeline and
  API layer must be written against an async session/engine; migrations are
  the only accepted path for persisted schema changes (see
  `docs/architecture/overview.md` Key Technical Decisions).
- In-process APScheduler means there is no separate scheduling service to
  operate, but also no built-in cross-process job coordination; if the
  worker process and the FastAPI app both run, job placement (which process
  owns which scheduled job) must be explicit and non-overlapping to avoid
  duplicate cycle runs.
- Because there is no distributed task queue, any future requirement for
  multiple independent cadences or horizontally scaled processing is a
  post-MVP architecture change, not an incremental extension of APScheduler.
- Jinja2 + htmx keeps the dashboard server-rendered and avoids a separate
  frontend build/deploy pipeline; richer client-side interactivity (e.g. the
  explicitly excluded candlestick charts, orderflow, heatmaps) would require
  revisiting this decision.
- If deployment target changes post-MVP (e.g. to a VPS or cloud), this ADR
  should be superseded rather than silently reinterpreted, since local
  single-machine assumptions (in-process scheduler, local LLM data locality)
  are threaded through ADR-002 and this ADR together.

## References

- `docs/product/PRD.md` (Unresolved Questions; Requirements; Scope Excluded)
- `docs/architecture/decisions/ADR-002-local-llm-via-ollama.md`
- `docs/architecture/overview.md`
