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
Tracer Slice. Ticket 5 (EvidencePack builder) not yet dispatched.

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
  uses equality, not just that some literal value was bound. Verified the
  fix by (a) confirming a deliberately-wrong-column query now raises
  instead of silently passing, (b) full suite still 48/48, ruff clean —
  this machine's local `.venv` can run `pytest`/`ruff` directly, unlike the
  subagent sandboxes used for review/validation so far. **Ticket 4: DONE.**

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
  or `EvidencePackService.build_or_update()`'s real `select(...)`
  executes correctly against a live Postgres session (only the schema
  was proven live, via migration verification; both services' query
  logic is proven only against a fake session double, each of which now
  at least asserts the correct column/operator is used). Track as
  follow-up once an integration-DB test fixture exists. Ticket 4 review
  finding, broadened at Ticket 5 review to explicitly cover
  `EvidencePackService` too.
- `docs/architecture/domain-model.md`/`ai-and-evidence.md` state the
  Protected Semantics rule that syndicated repeats of one originating
  report must count as one independent source, not many — but Ticket
  5's `compute_independent_source_count` only implements the trivial
  case (the same `document_id` referenced twice counts once); true
  cross-Document syndication detection (two distinct Documents
  republishing one wire story) is unimplemented and untested, per the
  architect's explicit "no syndication-detection logic needed yet"
  scoping for the single-source MVP milestone. Not a defect for this
  ticket, but flagged so a future reader doesn't mistake the Protected
  Semantics line for an already-complete guarantee. Ticket 5 review
  finding; revisit once a second source is added (Milestone 2+).

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

## Process Change: contribution-policy + documentation-gate enforcement + parallelization

Per explicit user instruction (2026-08-15): `contribution-policy.md` was
defined but never wired into any workflow stage's `required_policies`, and
`DOCUMENTATION_GATE` was being skipped (tickets 1-4 went straight from
REVIEW to DONE without an explicit documentation check). Fixed:

- `.cursor/policy/execution-map.md` — `contribution-policy` added to
  `IMPLEMENTATION`, `REVIEW`, and `DONE` stage policies for `feature`,
  `bug`, and `refactor` workflows, and to `lightweight`.
- `.cursor/policy/workflow-rules.md` — new "Parallel Execution" section:
  dispatch independent stages/tickets concurrently when no blocking
  dependency exists AND `write_scope` doesn't overlap; pipeline instead of
  parallelize when `write_scope` overlaps (e.g. a shared file or linear
  migration chain); read-only stages (architecture assessment,
  independent validation, review) default to parallel whenever the units
  are independent.
- `DOCUMENTATION_GATE` will now be run and explicitly logged (even when
  the answer is "no durable truth changed") before any ticket is marked
  DONE, instead of being implicitly skipped.
- One-time exception, by explicit user decision: tickets 1-4 and the
  `.cursor/`/`docs/` framework work were never branched/PR'd per ticket
  (all still sat uncommitted on `main` — only 2 commits existed in the
  entire history before this). Rather than backfill per-ticket
  branches/PRs retroactively, this was squashed into one collective
  commit (`8e7a229`) pushed directly to `main` (no PR — nothing to PR
  against once already on the target branch; a PR would have required a
  history-rewriting reset that was correctly flagged as unsafe to
  auto-run). **Starting with Ticket 5**, every ticket gets its own branch
  (`feat/wave1-ticketN-<slug>`), Conventional Commit-style commits, and a
  real PR pushed to `origin` (`folg-code/MarketIntelligencePlatform-`).
- `planning/waves/wave-01-foundation-and-tracer-slice.md` Parallelizable
  Work section corrected: tickets 5 and 6 were wrongly documented as
  sequential — both consume ticket 4's output but not each other's, so
  their `ARCHITECTURE_GATE`/`VALIDATION`/`REVIEW` stages run in parallel;
  `IMPLEMENTATION` is pipelined (not concurrent) because both touch the
  shared `persistence/models.py` and the linear Alembic migration chain
  (resolved via `alembic merge` for the resulting two heads).

## Next Actions

- Wave 1 / Ticket 5 — EvidencePack builder. ARCHITECTURE_GATE **APPROVE**
  (impact CROSS_MODULE, architect): `EvidencePack` is a separate table
  (`narrative_id` FK unique+not-null, `independent_source_count`,
  timestamps), created together with its `Narrative` and rebuilt/grown as
  `NarrativeEvent`s are added — architect clarified this directly in
  `docs/architecture/domain-model.md` (Relationships) since it resolved an
  ambiguity in already-accepted text. Stays a fully separate component
  from `narrative_engine` (ticket 8/scheduler sequences the two, ticket 5
  does not touch ticket 4's files). "Real, not hardcoded" means genuine
  `COUNT(DISTINCT document_id)` over reachable Documents — no
  syndication-detection logic needed yet (single-source milestone; that's
  speculative extensibility for now). Source traceability is derived via
  the existing `Narrative -> NarrativeEvent -> Event -> Document` chain,
  no redundant join table. No ADR. Dispatching to engineer for
  IMPLEMENTATION now (does not wait on Ticket 6's gate, per the
  pipelining rule).
  **IMPLEMENTATION done (commit `037639a`)**: `EvidencePack` model,
  migration, pure `COUNT(DISTINCT document_id)` aggregation, thin async
  service refusing zero-traceable-Document packs, 9 new tests (57/57
  full suite passing at the time), migration verified live against a
  disposable Postgres 16 container. Validation was deferred while
  Ticket 6 (independent, parallel) went through an unusually long
  7-round fix/validate cycle (see Ticket 6's own branch/PR #1 for that
  full history) — no changes to this ticket's implementation since.
  Dispatching first VALIDATION pass now that Ticket 6 is closed out.
  **VALIDATION: PASS, first attempt, no findings.** Tester independently
  verified the single most important correctness property with a
  throwaway script against the real code path (not just trusting test
  names): two `Event`s sharing one `document_id` correctly dedup to an
  independent-source count of 1 (not 2); two `Event`s on distinct
  Documents correctly count as 2. Also independently exercised the
  zero-traceable-Document refusal (rigged a fake session's `add()` to
  raise, confirmed it's never called before the guard fires), confirmed
  no LLM/HTTP import anywhere in the aggregation module, confirmed no
  `narrative_engine` files touched, confirmed migration chain is a
  single clean head. 57/57 tests, ruff clean. Proceeding to REVIEW.
  **REVIEW: PASS_WITH_NOTES.** Confirmed diff scope clean (only Ticket
  5's own files across 3 commits), `narrative_id` FK genuinely
  unique+not-null (literal 1--1, not optional), `narrative_engine`
  boundary held (zero overlap, grepped directly), aggregation is
  genuine `COUNT(DISTINCT document_id)` via a pure function with no
  DB/LLM/HTTP dependency, 9 tests are behaviorally meaningful (dedup,
  growth, refusal, create-vs-update). Confirmed no Ticket 6 content
  leaked onto this branch. Non-blocking notes actioned: (1) reviewer's
  sandbox couldn't independently run pytest/ruff — orchestrator
  independently re-ran, 57/57 pass, ruff clean, closing that gap; (2)
  syndication-detection scope gap and (3) live-Postgres integration-test
  gap both added to Tracked Technical Debt above; (4) this branch's
  `planning/current.md` chore commit bundling Ticket 6 notes is a known,
  already-anticipated merge-reconciliation item (both tickets' final
  planning-log content will need manual reconciliation on `main`, not a
  blocker for either individual PR).
  **DOCUMENTATION_GATE: run explicitly, logged (not skipped).** Two
  small tracked-debt additions made (above); no `domain-model.md`/
  `ai-and-evidence.md` edit needed beyond the architect's earlier
  literal-1--1 clarification (already committed) — both docs already
  state the governing policy at the correct level of abstraction. Gate:
  PASS.
  **Ticket 5: DONE.** Pushed to `origin/feat/wave1-ticket5-evidence-
  pack`; PR opened: https://github.com/folg-code/MarketIntelligencePlatform-/pull/2.
- Wave 1 / Ticket 6 — Instrument impact assessor. ARCHITECTURE_GATE
  **APPROVE** (impact CROSS_MODULE, architect): stays fully deterministic/
  rule-based per `overview.md`'s already-accepted boundary (no new LLM
  call from this component; ADR-001's permission for LLM-drafted impact
  stays available for a later ticket, most plausibly by extending event
  extraction, not by giving this component its own LLM boundary).
  Deterministic logic must be a genuine documented rule procedure over
  Event/Narrative content, not bare keyword/entity-presence matching
  (reviewer must check this explicitly). Concrete `direction` enum
  (`strongly_bearish`..`strongly_bullish`, `mixed`, `uncertain`) and
  `horizon` enum (`intraday`/`multi_day`/`unknown`) promoted from
  `docs/product/MVP_Vision_Architecture_Decisions.md` §7 into
  `domain-model.md` as canonical domain truth. `NarrativeInstrumentImpact`
  needs its own `unconfirmed`/(future `confirmed`) status enum, separate
  from `Narrative.validity_status`, and **must** set
  `values_callable=lambda e: [m.value for m in e]` (the ticket-4 enum bug
  must not repeat here). `instrument` is a closed 3-value enum (NQ/BTC/
  GOLD), not a growing entity. `relevance` type is a genuine local choice
  (no doc settles it). No EvidencePack required first (unconfirmed impact
  isn't yet a "material conclusion").
  **Process note:** this architect's doc edit to `domain-model.md`
  (Terminology: direction/horizon enums, confirmation-state field) landed
  in the same shared working tree while Ticket 5's branch was already
  checked out, and got swept into Ticket 5's doc commit — caught and
  fixed by amending that commit back down to only Ticket 5's content; the
  Ticket 6 content is sitting uncommitted for now (safe, additive, no
  conflict with Ticket 5's in-progress code) and will be committed to
  Ticket 6's own branch once Ticket 5's implementation lands (git
  surgery — stash/checkout — is deferred until the Ticket 5 engineer
  subagent, which is actively writing files right now, finishes, to
  avoid disturbing its in-progress work). Real lesson for future parallel
  ARCHITECTURE_GATE dispatches touching shared docs: either serialize doc
  edits specifically, or accept this kind of cleanup step as the cost of
  parallelizing analysis stages in one working tree.

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
