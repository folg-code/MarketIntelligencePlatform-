# Current Project State

## Purpose

Provide the compact operational entry point for current project execution.

This file should help agents start from current state without loading full
history. Keep it short and replace stale operational details as the project
progresses.

## Current Milestone

`planning/milestones/milestone-01-mvp-tracer-bullet.md` — MVP Tracer-Bullet
Pipeline. Status: **APPROVED**.

## Current Wave

`planning/waves/wave-01-foundation-and-tracer-slice.md` — Foundation And
Tracer Slice. Tickets 5 and 6 implemented on their own branches
(`feat/wave1-ticket5-evidence-pack`, `feat/wave1-ticket6-instrument-impact`
— note: this file's content diverges slightly per branch since each
ticket now carries its own operational-note updates per
`contribution-policy`; reconcile at merge time), pending VALIDATION/REVIEW
on each.

## Active Work

- Wave 1 / Ticket 1 — Project skeleton & tooling. **DONE** (engineer ->
  architect retro-gate APPROVE -> reviewer PASS_WITH_NOTES).
- Wave 1 / Ticket 2 — Ingestion adapter: Fed/FOMC. **DONE** (engineer ->
  ARCHITECTURE_GATE LOCAL (orchestrator, confirmed by reviewer) -> reviewer
  PASS_WITH_NOTES).
- Wave 1 / Ticket 3 — Event extraction via local Ollama. **DONE** (engineer
  -> ARCHITECTURE_GATE LOCAL (pre-classified, confirmed by both engineer and
  reviewer) -> reviewer PASS_WITH_NOTES).
- Wave 1 / Ticket 4 — Narrative candidate assignment. ARCHITECTURE_GATE
  **APPROVE** (impact CROSS_MODULE, architect): `canonical_key` derivation is
  a local implementation choice (not an ADR) — must be deterministic,
  computed from normalized semantic Event fields (entities/topics/type),
  documented inline as a provisional single-source MVP convention to be
  revisited at Milestone 2. `Narrative.validity_status` (starting
  `candidate`) is sufficient status; `NarrativeEvent` gets **no** status
  column in this ticket (rejection/override semantics deferred to Milestone
  2 with the override mechanism). No merge/split/lifecycle/validation-layer
  logic in scope. `narrative_engine` must not call the LLM/external APIs
  directly. IMPLEMENTATION done by engineer: new `Narrative`/
  `NarrativeEvent` models, `narrative_engine` module (canonical_key derived
  from normalized type+entities+topics), migration, 9 new tests (48 total
  passing), ruff clean, migration verified against disposable Postgres 16.
  No escalation triggers hit. Tester VALIDATION: **PASS**, all 5 acceptance
  criteria independently verified (tester re-ran pytest/ruff itself, and
  went further than required by independently exercising the full
  migration upgrade/downgrade cycle against a live disposable Postgres 16
  container). Reviewer REVIEW: **PASS_WITH_NOTES**, zero blocking findings;
  confirmed compliant with all architect constraints and Protected
  Semantics. Recommended fixing the tester's `test_service.py` fake-session
  gap immediately (cheap, in-file, no new infra) — orchestrator applied
  this directly: `FakeAsyncSession.scalar` now asserts the comparison
  actually filters on `Narrative.canonical_key` (table+column identity) and
  uses equality, not just that some literal value was bound. **Ticket 4:
  DONE**, merged into the collective bootstrap commit (`8e7a229`).
- Wave 1 / Ticket 5 — EvidencePack builder, on
  `feat/wave1-ticket5-evidence-pack`. ARCHITECTURE_GATE APPROVE (see
  git history on that branch / prior agent transcripts for full detail).
  IMPLEMENTATION done (commit `037639a`): `EvidencePack` model, migration,
  pure aggregation (`COUNT(DISTINCT document_id)`), thin async service
  refusing zero-traceable-Document packs, 9 new tests, 57/57 passing,
  migration verified live. Pending VALIDATION/REVIEW.
- Wave 1 / Ticket 6 — Instrument impact assessor, on
  `feat/wave1-ticket6-instrument-impact` (branched from Ticket 4's
  baseline, independent of Ticket 5). ARCHITECTURE_GATE APPROVE: stays
  deterministic (no LLM call), concrete direction/horizon enums and a
  confirmation-state field added to `domain-model.md`. IMPLEMENTATION done
  (commit `7721602`): `NarrativeInstrumentImpact` model + 4 new enums
  (correctly using `values_callable` this time — verified live that
  persisted values are lowercase), deterministic rule procedure over
  `rate_decision` events -> NQ direction with fact-quoting rationale, 11
  new tests, 59/59 passing, migration verified live (upgrade/downgrade/
  re-upgrade, enum lowercase values confirmed via `psql`). Pending
  VALIDATION/REVIEW.

## Blockers

None currently. (Resolved: Ticket 3 fetches full press-release text from
`Document.url` at extraction time; Ticket 2's ingestion boundary unchanged.)

## Tracked Non-Blocking Technical Debt (from Ticket 1 review)

- No dependency pinning/lockfile in `pyproject.toml` — resolve before CI or
  deployment is introduced.
- No ASGI server dependency (`uvicorn`) — add no later than Wave 1 Ticket 9
  (dashboard), sooner if manual local running is needed earlier.
- `tests/test_smoke.py::test_health_endpoint_smoke` calls the handler
  directly instead of through real ASGI routing — tighten with `TestClient`
  once API testing conventions are established.
- `README.md` is still the generic template — add project-specific
  setup/run instructions before Milestone 1 is considered complete.
- No documented `DATABASE_URL`/credentials for the pre-existing local
  PostgreSQL service (discovered in Ticket 2) — will block real end-to-end
  runs (e.g. Ticket 8 scheduler wiring). Needs resolution before Milestone 1
  acceptance can be demonstrated against a persistent local DB rather than
  a disposable container.
- Open design question for Ticket 3 (event extraction): `Document.body`
  currently holds only the RSS short description, not the full press
  release text (`url` holds the reference to the full page). Decide
  whether event extraction needs full-text fetch, or short
  description + link is sufficient for MVP extraction quality. Promoted to
  a Blocker (see above) since it affects Ticket 3 scope directly.
- Postgres major-version parity between the disposable Docker container
  used for migration verification and the real local instance — not yet
  confirmed (from Ticket 2 review); check once `DATABASE_URL` is
  configured for real.
- Enum-storage convention (`native_enum=False`, VARCHAR + CHECK) used for
  `ProcessingStatus` should be carried forward consistently for future
  enum columns (e.g. `Narrative.validity_status`, `.lifecycle_status`)
  rather than decided ad hoc per model (Ticket 2 review note for Ticket 3+).
- Forward-looking robustness note (Ticket 2 review): `fed_fomc.py`'s feed
  parser uses `ElementTree.fromstring`, which would raise an unhandled
  `ParseError` on a named HTML entity outside CDATA (e.g. `&mdash;`) if the
  live feed ever emits one; not observed in the current fixture, watch once
  running against live content.
- `DEFAULT_OLLAMA_MODEL='llama3.1'` in `llm_client.py` is a placeholder —
  operators must set `OLLAMA_MODEL` to whatever model they actually pulled
  locally; not yet documented anywhere (ties into the general "no local
  setup docs" gap already tracked above).
- Extraction quality against a real local Ollama model has **not** been
  manually sanity-checked yet (no Ollama available in the sandbox that
  built Ticket 3) — do this once on a machine with Ollama installed, before
  treating Milestone 1's core ADR-002 risk as validated.
- `Event` has no validity/status column, even though `ADR-001`'s
  Consequences section says every LLM-consuming pipeline stage needs one.
  Current reasoning (in code comments): `Event` itself is never a protected
  outcome; that distinction belongs on `NarrativeEvent` instead. Sound per
  `domain-model.md`, but flagged by the Ticket 3 reviewer as an implicit
  assumption the architect should confirm explicitly when `NarrativeEvent`
  is designed — i.e. as part of Ticket 4.
- Reviewer sessions in this environment could not independently execute
  `pytest`/`alembic` (Windows sandbox limitation) for Tickets 2 and 3;
  review verdicts relied on direct code/file inspection plus accepting the
  engineer's reported execution evidence rather than re-running it
  independently. Not a code defect, but worth remembering when weighing how
  much independent confirmation REVIEW stages provide here.
- Cosmetic: `Event.entities`/`.topics`/etc. typed as `Mapped[list]` rather
  than `Mapped[list[str]]` (Ticket 3 review note).
- **Systemic, not ticket-local:** `Enum(..., native_enum=False,
  validate_strings=True, length=N)` columns (`ProcessingStatus` from
  ticket 1; `NarrativeValidityStatus`/`NarrativeLifecycleStatus` from
  ticket 4) persist the Python enum member's **name** (e.g. `"CANDIDATE"`)
  rather than its lowercase `.value`, despite the explicit lowercase string
  values and migration literals implying otherwise (SQLAlchemy default
  behavior with no `values_callable` set). ORM round-trips are unaffected
  (symmetric name<->member mapping), so no existing test catches it, but
  any raw SQL/dashboard query/manual inspection will see uppercase names.
  Recommend a single follow-up ticket before Milestone 2 (more enums are
  coming) to add `values_callable=lambda e: [m.value for m in e]` to all
  three enum columns plus a corrective migration (no data migration needed
  — no real rows exist yet). Ticket 4 review finding.
- `canonical_key.py`'s derivation collides (produces the same key) for any
  two `Event`s that both have `type=None` and empty `entities`/`topics` —
  deterministic and documented as a single-source aliasing limitation, but
  the specific empty-fields collision case itself isn't called out in the
  module docstring yet. Accepted as a known MVP limitation (Ticket 4
  review, minor, non-blocking); consider adding an explicit docstring note.
- No integration test yet proves `NarrativeAssignmentService.assign()`'s
  real `select(...)` executes correctly against a live Postgres session
  (only the schema was proven live, via migration verification; the
  service's query logic is proven only against a fake session double,
  which now at least asserts the correct column/operator is used). Track
  as follow-up once an integration-DB test fixture exists — likely needed
  by Ticket 5 (EvidencePack builder) anyway. Ticket 4 review finding.

## Recent Material Discoveries

- Discovery session (`grill-me`) resolved the PRD's 4 open technical
  questions: local deployment, local LLM via Ollama, SQLAlchemy async +
  Alembic, in-process APScheduler, server-rendered (Jinja2 + htmx)
  dashboard — recorded in `docs/architecture/decisions/ADR-001`, `ADR-002`,
  `ADR-003`.
- `docs/architecture/overview.md`, `domain-model.md`, and `ai-and-evidence.md`
  were populated from the PRD and the source vision document
  (`docs/product/MVP_Vision_Architecture_Decisions.md`); they were
  previously empty templates.

## Current Plan

1. ~~Get Milestone 1 approved~~ — done.
2. ~~Dispatch Wave 1 tickets 1-4~~ — done (see Active Work).
3. Dispatch Wave 1 tickets 5-9 in sequence, per
   `planning/waves/wave-01-foundation-and-tracer-slice.md`, through the
   full `feature` workflow stage gates (READY -> PREPARATION ->
   ARCHITECTURE_GATE -> TESTING_GATE -> IMPLEMENTATION -> VALIDATION ->
   REVIEW -> DOCUMENTATION_GATE -> DONE).
4. Run `MILESTONE READINESS GATE` once Wave 1 delivers Milestone 1's
   Acceptance Expectations.

## Next Actions

- Dispatch Wave 1 Ticket 5 (EvidencePack builder — real source traceability
  and independent-source counting, persisted) through the `feature`
  workflow stage gates.

## Replanning Triggers

- Local Ollama extraction quality/latency proves insufficient for the
  tracer-bullet slice (see `ADR-002` Consequences).
- The 5-minute processing cycle does not fit on the target local hardware
  once real LLM inference and persistence are in the loop.
- The domain model needs material adjustment once real persistence/
  extraction code is written.

## References

- `docs/product/PRD.md`
- `docs/product/roadmap.md`
- `docs/architecture/overview.md`
- `planning/milestones/milestone-01-mvp-tracer-bullet.md`
- `planning/waves/wave-01-foundation-and-tracer-slice.md`
