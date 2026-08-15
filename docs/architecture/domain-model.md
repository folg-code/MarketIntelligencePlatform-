# Domain Model

## Purpose

Define project-specific domain concepts, relationships, invariants, and
protected semantics.

This document should represent accepted domain truth. Do not use it to invent
product behavior or implementation details.

## Domain Summary

The domain models market narratives as evidence-backed, auditable objects
distinct from raw source content and from the instruments (NQ, BTC, GOLD)
they may affect. A narrative's identity, evidence, and instrument impact are
each explicit, first-class concepts — never inferred implicitly from text
similarity or keyword presence — so that every system conclusion can be
traced back to its supporting documents and can be corrected by a human.

## Core Concepts

- **Document** — a normalized representation of one piece of ingested source
  content (e.g. a Fed release, an SEC filing, a news article), produced by an
  ingestion adapter.
- **Event** — something extracted from a Document by event extraction,
  carrying `extracted_facts` (what the source literally states) kept
  separate from `source_claims` (what the source asserts/frames), and kept
  separate from any model inference about meaning or impact.
- **NarrativeEvent** — the assignment of an Event to a narrative, produced by
  the narrative engine.
- **Narrative** — a market narrative identified by a semantic
  `canonical_key`, not by cluster-hash identity. A narrative accumulates
  NarrativeEvents over time and has lifecycle/dynamics state (e.g.
  emerging/accelerating/confirmed) and a `validity_status`.
- **EvidencePack** — the aggregated evidence for a narrative: source
  traceability plus an independent-source count. Every material narrative
  conclusion requires an EvidencePack.
- **Independent-source counting** — counting distinct originating sources,
  not distinct articles; syndicated repeats of one originating report count
  as one independent source, not many.
- **NarrativeInstrumentImpact** — an explicit, auditable relation between a
  Narrative and an instrument (NQ, BTC, or GOLD) carrying direction,
  relevance, and horizon. This relation is the MVP's directional concept and
  replaces generic sentiment.
- **`user_locked`** — a flag/override state on a narrative or a specific
  field of it indicating a human decision that must not be silently changed
  by automated pipeline processing.
- **Human override / correction** — user actions (watch, mute, rename display
  title, mark irrelevant, mark invalid, reject event assignment,
  restore/undo) that adjust narrative or event-assignment state; every
  correction creates an audit entry.
- **Alert** — a notification derived from narrative/evidence state
  transitions (e.g. `emerging_narrative`, `confirmed_narrative`,
  `narrative_acceleration`, `high_impact_event_added_to_narrative`,
  `conflicting_information`, `unconfirmed_social_hype`), delivered in-app
  only in MVP.
- **Morning Market Brief** — a generated summary (Macro/Cross-Market, NQ,
  BTC, GOLD, Watch Today sections) built from current narrative and
  instrument-impact state.

## Relationships

```text
Document 1 --* Event
Event 0..1 --1 NarrativeEvent
NarrativeEvent * --1 Narrative
Narrative 1 --1 EvidencePack
EvidencePack 1 --* Document (via source traceability)
Narrative * --* NarrativeInstrumentImpact --1 Instrument (NQ | BTC | GOLD)
Narrative 1 --* Alert (0..*)
Narrative / NarrativeEvent 1 --* Human override (0..*, each with an audit entry)
```

A Narrative is identified by its `canonical_key`; NarrativeEvents and
EvidencePacks are always resolved through that identity, never through a
transient cluster hash.

## Invariants

- Narrative identity is always `canonical_key`-based; two narratives with the
  same semantic identity are the same narrative regardless of how their
  events were clustered.
- A narrative cannot carry a material conclusion (e.g. a confirmed
  `validity_status`, a high-impact `NarrativeInstrumentImpact`) without an
  associated EvidencePack.
- An EvidencePack cannot exist without source traceability back to
  Documents.
- Independent-source counts never count syndicated repeats of the same
  originating report as separate independent confirmations.
- A `NarrativeInstrumentImpact` is never inferred solely from entity/keyword
  presence in a Document or Event; it must be an explicit assessment result.
- Once a field is `user_locked`, automated pipeline processing must not
  overwrite it; only an explicit human action can change it again.
- A manually rejected event-assignment or narrative correction must not
  silently reappear on a later processing cycle.
- Any market-pricing claim (e.g. "markets are pricing in...") requires
  supporting market data; without it, only commentary-framed language is
  permitted.

## Protected Semantics

These must never be silently changed by an implementation or refactor
without an explicit architecture decision:

- Narrative identity is semantic (`canonical_key`), never cluster-hash-based.
- No material narrative conclusion without an EvidencePack; no EvidencePack
  without source traceability; no market-pricing claim without market data.
- Syndicated articles must never count as independent confirmations.
- Instrument relevance/impact must always be an explicit, auditable
  `NarrativeInstrumentImpact` relation — never inferred from keywords alone.
- `user_locked` overrides block automatic changes to that decision.
- LLM decision boundaries
  (`docs/architecture/decisions/ADR-001-llm-decision-boundaries.md`): LLM
  output must pass through the validation layer before it can finalize
  `validity_status = confirmed`, merges, splits, `user_locked` changes,
  high-impact instrument impact without evidence, or durable identity
  changes.

## Terminology

- **`canonical_key`** — the stable, semantic identifier for a narrative's
  identity.
- **`extracted_facts`** — literal factual content extracted from a Document,
  kept separate from interpretation.
- **`source_claims`** — what a source asserts or frames, kept separate from
  `extracted_facts` and from model inference.
- **`validity_status`** — a narrative's confirmation state (e.g.
  candidate/unconfirmed vs. confirmed); moving to `confirmed` is a protected
  outcome under `ADR-001`.
- **`user_locked`** — see Core Concepts / Invariants above.
- **Instrument impact direction** — the MVP's directional concept, replacing
  generic sentiment (see `docs/product/PRD.md` Decisions).

## Open Domain Questions

None currently open. The PRD's prior "Unresolved Questions" (LLM provider,
persistence layer, scheduler, dashboard approach) were resolved via
`docs/architecture/decisions/ADR-001-llm-decision-boundaries.md`,
`ADR-002-local-llm-via-ollama.md`, and
`ADR-003-mvp-technical-stack-persistence-scheduler-deployment-dashboard.md`.
Explicitly deferred (not open questions, but out of MVP scope per the PRD):
automatic narrative merge/split, full Claim/Fact graph, automated
`NarrativeEpisode` lifecycle, market-data confirmation.

## References

- `docs/product/PRD.md`
- `docs/architecture/overview.md`
- `docs/architecture/ai-and-evidence.md`
- `docs/architecture/decisions/ADR-001-llm-decision-boundaries.md`
