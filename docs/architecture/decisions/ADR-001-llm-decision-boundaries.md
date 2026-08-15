# ADR-001: LLM Decision Boundaries

## Status

Accepted

## Context

The Market Intelligence Platform uses an LLM as an analytical component in
the pipeline (event extraction, narrative candidate generation). The PRD
states plainly: "LLMs are analytical components, not sources of truth" and
requires that every material narrative conclusion be evidence-backed and
auditable, that syndicated articles never count as independent
confirmations, and that instrument relevance/impact always be an explicit,
auditable relation rather than an inference from keywords alone.

Without an explicit boundary, LLM output could silently become authoritative
(e.g. an LLM-proposed narrative merge or a "confirmed" validity status could
be persisted without human or rule-based validation), which would violate the
evidence and auditability guarantees the product promises the user and would
make system conclusions non-reproducible and hard to trust.

This decision is independent of which LLM or provider is used (see
`ADR-002-local-llm-via-ollama.md` for the provider choice); it defines the
governance boundary that applies regardless of provider.

## Decision

LLM output is treated as a candidate/proposal, never as a final decision, for
any of the following outcomes:

- setting `validity_status = confirmed` on a narrative,
- merging or splitting narratives,
- changing a `user_locked` field or override,
- creating or upgrading a high-impact `NarrativeInstrumentImpact` without
  accompanying evidence,
- any durable identity change (e.g. altering a narrative's `canonical_key`).

Each of these outcomes must pass through an explicit validation layer before
it is finalized:

- deterministic/rule-based validation (e.g. evidence-count thresholds,
  independent-source checks, `user_locked` checks) and/or
- explicit human confirmation via the override/correction controls defined in
  the PRD.

The LLM may freely produce: extracted facts, source claims, narrative
candidate proposals, draft instrument-impact assessments, and draft evidence
summaries — provided these remain marked as unconfirmed/candidate state until
they pass validation.

`user_locked` overrides always take precedence over LLM output: once a field
is user-locked, no LLM-driven pipeline step may silently change it.

## Consequences

- Every pipeline stage that consumes LLM output must carry a validity/status
  field (e.g. candidate vs. confirmed) so downstream consumers (EvidencePack
  builder, instrument impact assessor, API layer, dashboard) can distinguish
  proposed from validated state.
- The validation layer is a required, explicit component (not implicit
  application logic) so its rules can be reviewed and tested independently of
  prompt/model changes.
- Changing LLM provider or model (see `ADR-002-local-llm-via-ollama.md`) does
  not require revisiting this ADR, since the boundary is provider-agnostic.
- Any future change that would let LLM output bypass this validation layer for
  the listed outcomes is an architecture change and requires a new or
  superseding ADR, not an incidental implementation decision.

## References

- `docs/product/PRD.md` (Constraints; Decisions; Requirements)
- `docs/architecture/ai-and-evidence.md`
- `docs/architecture/domain-model.md` (Protected Semantics)
- `docs/architecture/decisions/ADR-002-local-llm-via-ollama.md`
