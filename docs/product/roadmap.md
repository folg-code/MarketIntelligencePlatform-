# Product Roadmap

## Purpose

Track project-specific product direction, sequencing, and milestone intent.

This document should describe durable or semi-durable roadmap truth. Current
execution state belongs in `planning/current.md`.

## Roadmap Summary

Ship the MVP as two milestones, each a vertical slice rather than a
horizontal layer build-out, then evaluate before committing to any post-MVP
work:

1. **Milestone 1 — MVP Tracer-Bullet Pipeline**: prove the full pipeline
   shape end-to-end (one source, one narrative, one instrument) before
   investing in breadth.
2. **Milestone 2 — MVP Full Pipeline**: extend the proven pipeline to the
   full PRD scope (all MVP sources/instruments, alert feed, Morning Brief,
   human overrides).

Post-MVP work is intentionally deferred and only sequenced in outline until
Milestone 2 is validated against real usage.

## Milestones

| # | Name | Outcome | Status |
|---|---|---|---|
| 1 | MVP Tracer-Bullet Pipeline | End-to-end pipeline (ingest -> extract -> narrative -> EvidencePack -> instrument impact -> dashboard) working for one source and one narrative, validating architecture decisions ADR-001/002/003 | PROPOSED |
| 2 | MVP Full Pipeline | Full PRD scope: all MVP sources/instruments, alert feed, human overrides, Morning Brief | NOT STARTED |

Detailed scope for the active milestone lives in `planning/milestones/`.

## Priorities

1. Validate the riskiest architecture assumption first: local LLM (Ollama)
   extraction quality and pipeline timing within the 5-minute cycle
   (`ADR-002-local-llm-via-ollama.md`). This drives Milestone 1's tracer-bullet
   shape.
2. Prove the domain model (`canonical_key` identity, `EvidencePack`,
   `NarrativeInstrumentImpact`, LLM decision-boundary validation layer) is
   implementable as specified before building breadth on top of it.
3. Only after Milestone 1 validates the pipeline shape, expand to full MVP
   scope (Milestone 2).
4. Do not sequence post-MVP work (see Deferred Work) until Milestone 2 is
   validated against real usage — priorities may change based on what is
   actually useful to the target trader.

## Dependencies

- Milestone 1 depends on `ADR-001-llm-decision-boundaries.md`,
  `ADR-002-local-llm-via-ollama.md`, and
  `ADR-003-mvp-technical-stack-persistence-scheduler-deployment-dashboard.md`
  (all Accepted).
- Milestone 1 depends on local environment availability: Ollama with a
  working model, and a reachable PostgreSQL instance.
- Milestone 2 depends on Milestone 1's pipeline shape being validated
  (`READY FOR VALIDATION` / accepted outcome), not merely started.

## Deferred Work

Explicit MVP non-goals (see `docs/product/PRD.md` Scope Excluded and
`docs/product/MVP_Vision_Architecture_Decisions.md` §18) are not on this
roadmap yet. Candidate post-MVP milestones, in the order suggested by the
source vision document (§20), to be re-prioritized after Milestone 2 based on
real usage rather than assumed now:

1. **Social Intelligence** — X/Reddit adapters, social source quality and
   velocity, social sentiment as an input signal (not a primary concept).
2. **Narrative Governance** — merge/split UI, relation editing,
   `canonical_key` editing, stronger audit workflows.
3. **Narrative Episodes** — automatic reactivation/peak detection, episode
   comparison (schema placeholder `NarrativeEpisode` already anticipated in
   the domain model, but inactive in MVP).
4. **Market Data Confirmation** — OHLCV/rates integration, market-derived
   evidence, market-pricing language permissioning.
5. **Research Platform** — sentiment/impact vs. returns, narrative episodes
   vs. volatility, mention velocity vs. market behavior.
6. **Delivery Channels** — Telegram, email, webhooks.
7. **Advanced Infrastructure** — distributed processing or Kafka, only if
   real throughput/decoupling requirements justify it (explicitly not
   assumed needed).

## Decisions

- MVP is split into two milestones (tracer-bullet, then full scope) rather
  than one large milestone, to surface architecture and domain-model risk
  early (see Priorities).
- Architecture decisions for the MVP technical stack are resolved and
  recorded in `docs/architecture/decisions/` (ADR-001, ADR-002, ADR-003) and
  do not block milestone entry.

## Unresolved Questions

- Exact selection of the two-or-three MVP news/RSS sources beyond
  Fed/FOMC, BLS, and SEC (per PRD Requirements) is not yet finalized. Low
  impact on Milestone 1 (which needs only one source); must be resolved
  before Milestone 2 scoping.

## References

- `docs/product/PRD.md`
- `docs/product/MVP_Vision_Architecture_Decisions.md`
- `docs/architecture/decisions/`
- `planning/milestones/`
