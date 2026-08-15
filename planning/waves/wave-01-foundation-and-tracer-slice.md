# Wave 1: Foundation And Tracer Slice

## Goal

Stand up the minimal project skeleton and deliver the thinnest possible
end-to-end vertical slice of Milestone 1's pipeline, favoring integration
over completeness at every step.

## Selected Work

1. **Project skeleton & tooling** (horizontal enabling step — required
   before any vertical slice can integrate): `pyproject.toml`, package
   layout matching `docs/architecture/overview.md` component boundaries
   (ingestion / event extraction / narrative engine / evidence / instrument
   impact / validation layer / API / dashboard as separate modules), Ruff
   config, pytest config, async SQLAlchemy engine/session setup, Alembic
   init, minimal FastAPI app skeleton. Routes through `feature` workflow;
   `architect` should confirm module boundaries match `overview.md` before
   `engineer` proceeds.
2. **Ingestion adapter: Fed/FOMC** — fetch/parse/normalize into `Document`,
   with an Alembic migration for the `Document` table. Adapter sits behind
   an interface per project convention (external systems reached through
   adapters, not called directly from business logic).
3. **Event extraction via local Ollama** — LLM client adapter + extraction
   logic producing `Event`s with `extracted_facts`/`source_claims` kept
   separate, persisted via a migration.
4. **Narrative candidate assignment** — minimal `canonical_key`-based
   matching creating/updating a `Narrative` and `NarrativeEvent`, starting in
   `candidate` validity_status.
5. **EvidencePack builder** — real (not hardcoded) source traceability and
   independent-source counting, persisted.
6. **Instrument impact assessor** — minimal `NarrativeInstrumentImpact`
   (direction/relevance/horizon/rationale) for at least one instrument,
   starting unconfirmed.
7. **Validation layer (`ADR-001` minimal slice)** — deterministic checks
   gating `validity_status = confirmed`; include the test that proves raw
   LLM output alone cannot finalize it (`tester` owns this test).
8. **APScheduler wiring** — in-process 5-minute cycle driving steps 2-6 in
   order.
9. **Minimal dashboard page** (Jinja2 + htmx) — one narrative, its
   EvidencePack with a link to the source Document, its instrument impact.

## Integration Points

Each ticket should land integrated into the running pipeline/dashboard, not
sit isolated behind a flag. Ticket 1 is the only exception (pure scaffolding)
and should be small enough to land first without blocking the others long.

## Expected Feedback

- Whether local Ollama extraction is workable at all for this domain
  (directly tests the `ADR-002` assumption).
- Whether the 5-minute cycle is realistic on the target local hardware once
  real LLM inference and persistence are in the loop.
- Whether the domain model as specified (`canonical_key`, `EvidencePack`,
  `NarrativeInstrumentImpact`, validation layer) is cleanly implementable, or
  needs adjustment before Milestone 2 broadens it.

## Dependencies

- Local Ollama installation with a working model, and a reachable
  PostgreSQL instance — both established as part of ticket 1.
- No cross-task dependency outside this wave; ADRs are already Accepted.

## Parallelizable Work

Tickets 1-4 are strictly sequential: each pipeline stage consumes the
previous stage's output (Document -> Event -> Narrative/NarrativeEvent),
and ticket 1's module boundaries must exist before any of them.

Tickets 5 and 6 are **not** sequential relative to each other, correcting
this document's original assumption. Both consume ticket 4's
Narrative/NarrativeEvent output; neither consumes the other's output.
`docs/architecture/domain-model.md`'s invariant ("a narrative cannot carry
a material conclusion... without an EvidencePack") only gates *material*
conclusions (confirmed `validity_status`, high-impact
`NarrativeInstrumentImpact`) — ticket 6 explicitly starts impact
`unconfirmed`, so it has no real dependency on ticket 5. Per
`.cursor/policy/workflow-rules.md` Parallel Execution: their
`ARCHITECTURE_GATE`/`VALIDATION`/`REVIEW` stages should run in parallel;
their `IMPLEMENTATION` stages have a practical (not logical) `write_scope`
overlap — both add ORM models to the shared `persistence/models.py` and a
new Alembic migration to the same linear chain — so implementation is
pipelined (ticket 6's `IMPLEMENTATION` starts as soon as ticket 5's files
are written, not sequentially blocked on ticket 5's full review) rather
than run byte-for-byte concurrently in the same working tree. Two resulting
Alembic heads are resolved with `alembic merge`, a supported pattern for
exactly this case.

Tickets 7 and 8 both depend on 5 and 6 being complete but not on each
other (7 is deterministic validation-layer logic; 8 is scheduler wiring
for steps 2-6 only, explicitly excluding 7's validation layer per this
wave's own scope) — parallelizable once `write_scope` is confirmed
disjoint (7 should not need to touch scheduler code, 8 should not need to
touch validation code). Ticket 9 (dashboard) can start once ticket 6's
output shape is stable, but watch for `write_scope` overlap with ticket 8
on `main.py` (both wire something into the app entrypoint) — verify
disjointness before parallelizing 8 and 9, otherwise pipeline them.

## Blocked Work

None currently. Wave 1 dispatch itself is blocked on Milestone 1 approval
(see `planning/milestones/milestone-01-mvp-tracer-bullet.md` Status).

## Routing

All tickets route through the `feature` workflow (new approved behavior).
`engineer` owns implementation; `architect` supports ticket 1 (module
boundaries) and any cross-module question; `tester` owns validation-layer
test coverage (ticket 7) and end-to-end tracer-bullet evidence for the
milestone's Acceptance Expectations; `reviewer` reviews each ticket before
it is considered done per `.cursor/policy/done.md`.

Starting with ticket 5, each ticket also follows `contribution-policy.md`
end-to-end: its own branch (`feat/wave1-ticketN-<slug>`), Conventional
Commit-style commits, and a real PR pushed to `origin` (see
`planning/current.md` for the one-time exception covering tickets 1-4 and
the `.cursor/`/`docs/` framework work, which predates this being wired into
the workflow and lands as a single collective commit/PR instead).

## Assumptions

- Ollama and at least one usable local model can be installed on the target
  machine as part of ticket 1; if not, this is a Milestone 1 blocker to
  escalate, not a Wave 1 implementation detail to work around.
- A local PostgreSQL instance is available or can be stood up as part of
  ticket 1.

## Review Notes

Not yet reviewed — wave has not been dispatched pending Milestone 1
approval.
