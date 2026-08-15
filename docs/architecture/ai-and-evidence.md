# AI And Evidence

## Purpose

Define project-specific rules for AI-assisted work, evidence expectations, and
human review needs.

Use this document for project-specific policy that is more concrete than the
universal AI framework.

## Evidence Expectations

- Every material narrative must have a traceable `EvidencePack` with source
  traceability back to originating Documents.
- Every directional `NarrativeInstrumentImpact` must carry rationale and
  evidence; direction/relevance/horizon must never be inferred from
  entity/keyword presence alone.
- Independent-source counting must count distinct originating sources, not
  distinct articles: syndicated repeats of one originating report count as
  one independent source.
- Unsupported market-language claims are prohibited — a claim like "markets
  are pricing in..." requires backing market data; otherwise the system must
  use commentary-framed language instead.
- The user must always be able to navigate from a briefing item or alert back
  to its source document(s).
- The user must be able to understand a system conclusion (narrative
  validity, instrument impact) without rereading every source document —
  the EvidencePack and rationale must be sufficient on their own.

## Testing Expectations

- Event extraction, narrative assignment, EvidencePack aggregation
  (including independent-source counting and syndication handling), and
  instrument impact assessment are business logic and must be tested with
  deterministic unit/integration tests independent of live LLM calls (e.g.
  via fixtures/fakes for the LLM adapter).
- The validation layer (see Protected Decisions below) must have explicit
  test coverage for each protected outcome it gates (confirmation, merge,
  split, `user_locked` change, high-impact instrument impact without
  evidence, identity change), including the case where validation correctly
  rejects/holds an LLM proposal.
- Human override behavior (watch, mute, rename, mark irrelevant/invalid,
  reject event assignment, restore/undo, and the resulting audit entries)
  must be tested, including that a manually rejected mapping does not
  silently reappear on a later processing cycle.
- Scheduler-driven cycle behavior (5-minute processing cycle; Morning Brief
  job) should be testable without depending on wall-clock timing in unit
  tests (e.g. by testing the cycle's steps directly and testing scheduler
  wiring separately).

## Human Review Or QA Triggers

Human review is required (not optional) before any of the following take
effect, consistent with `ADR-001-llm-decision-boundaries.md`:

- a narrative's `validity_status` moving to `confirmed` based on LLM-derived
  signals that the validation layer's deterministic rules cannot confirm on
  their own,
- a proposed narrative merge or split,
- any change to a `user_locked` field,
- a high-impact `NarrativeInstrumentImpact` proposed without sufficient
  evidence,
- a durable narrative identity change (`canonical_key` change).

Additionally, human review/correction is the accepted mechanism (per PRD) for
correcting the system: watch, mute, rename display title, mark
irrelevant/invalid, reject event assignment, restore/undo — each producing an
audit entry.

## Protected Decisions

The following decisions/outcomes are protected and must never be finalized
directly from raw LLM output without passing through the validation layer
(deterministic rule checks and/or explicit human confirmation):

- `validity_status = confirmed`,
- narrative merges or splits,
- `user_locked` changes,
- high-impact instrument impact without evidence,
- durable identity changes (`canonical_key`).

See `docs/architecture/decisions/ADR-001-llm-decision-boundaries.md` for the
full decision and rationale, and `docs/architecture/domain-model.md`
(Protected Semantics) for how this fits with the other protected domain
invariants.

## Accepted AI Usage

- LLM-assisted event extraction: producing `extracted_facts` and
  `source_claims` from Documents (via local LLM through Ollama — see
  `docs/architecture/decisions/ADR-002-local-llm-via-ollama.md`).
- LLM-assisted narrative candidate generation: proposing narrative
  assignment/grouping and draft instrument-impact assessments, always in
  candidate/unconfirmed state until validated.
- LLM-assisted drafting of evidence summaries or brief narrative text,
  provided the underlying facts/claims/evidence remain independently
  traceable to source Documents.

## Disallowed Or High-Risk AI Usage

- LLM output must never directly finalize any of the "Protected Decisions"
  above without passing through the validation layer.
- LLM output must never override a `user_locked` field.
- LLM output must never be the sole basis for instrument relevance/impact;
  keyword or entity presence alone (LLM-derived or not) must never stand in
  for an explicit `NarrativeInstrumentImpact` assessment.
- LLMs must not be used to generate a generic `sentiment_score`, X/Reddit
  sentiment signals, market predictions, or automated trading signals — these
  are explicit MVP non-goals per the PRD, independent of the validation
  layer.
- LLM-derived text must not state unsupported market-pricing claims (e.g.
  "markets are pricing in...") without accompanying market data.

## References

- `docs/product/PRD.md` (Constraints; Decisions; Scope Excluded)
- `docs/architecture/domain-model.md`
- `docs/architecture/decisions/ADR-001-llm-decision-boundaries.md`
- `docs/architecture/decisions/ADR-002-local-llm-via-ollama.md`
