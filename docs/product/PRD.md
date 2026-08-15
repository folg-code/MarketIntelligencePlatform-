# Product Requirements Document

## Purpose

Describe the project-specific product truth that should guide planning,
architecture, implementation, validation, and review.

This document should contain durable product requirements, not temporary task
notes or implementation plans.

## Product Summary

Market Intelligence Platform is an evidence-backed market narrative
intelligence system. It detects material market narratives, explains why they
matter, and estimates narrative-specific impact on selected instruments (NQ,
BTC, GOLD). It is explicitly not a sentiment-analysis system, a prediction
engine, or an automated trading signal generator.

## Problem

The MVP should prove one thing: can the system detect a material narrative
for NQ, BTC, or GOLD from reliable sources and present a short, auditable
intelligence view faster than manual source reading?

The first value moments are:

- "I can see what is really moving the market today."
- "I can see which narratives are emerging before they become obvious."

## Users

The target user is a discretionary/research trader. The MVP should support:

- morning market preparation,
- intraday alertness,
- narrative awareness,
- fast review of material source-driven changes,
- auditability of system conclusions.

## Desired Outcome

A discretionary/research trader can open the dashboard and answer, within a
few minutes:

- what important things happened,
- which narratives are active,
- what may matter for NQ, BTC, and GOLD,
- what changed recently,
- what evidence supports the system's view.

The user should be able to understand why the system reached a conclusion
without rereading every source document.

## Scope

### Included

Core user flow (MVP):

1. The user opens the dashboard.
2. The dashboard shows the current market brief.
3. The user reviews active narratives.
4. The user checks NQ, BTC, and GOLD narrative exposure.
5. The user reviews material changes and alerts.
6. The user opens a narrative to inspect evidence, events, uncertainty, and
   instrument impact.
7. The user can correct the system by watching, muting, renaming, marking
   invalid/irrelevant, or rejecting event assignments.

Minimum product capabilities:

- automatic source ingestion,
- event extraction,
- narrative grouping,
- EvidencePack generation,
- instrument impact assessment,
- current brief,
- active narratives view,
- alert feed,
- human correction.

### Excluded

Explicit MVP non-goals:

- X sentiment, Reddit sentiment, generic `sentiment_score`,
- market prediction, automated trading signals,
- Kafka,
- custom ML models,
- automatic narrative merge/split, merge/split UI,
- full Claim/Fact graph,
- automated `NarrativeEpisode` lifecycle,
- market-data confirmation,
- sentiment research,
- backtesting,
- Telegram/email/webhook alerts,
- complex multi-cadence scheduling,
- low-latency event-driven official-source processing,
- dashboard scope creep: candlestick charts, orderflow, heatmaps, complex
  settings UI, full economic calendar UI.

## Requirements

- Automatic ingestion from MVP sources (Federal Reserve/FOMC, BLS, SEC, and
  two or three selected news/RSS sources) covering NQ, BTC, and GOLD.
- Event extraction from documents, preserving extracted facts and source
  claims separately from model inference.
- Narrative grouping using semantic identity (`canonical_key`), not
  cluster-hash identity.
- Every material narrative must have an EvidencePack with source
  traceability and independent-source counting (syndicated repeats of one
  originating report must not count as multiple independent confirmations).
- Every material instrument association must be an explicit, auditable
  `NarrativeInstrumentImpact` relation — instrument relevance must never be
  inferred solely from entity or keyword presence.
- A Morning Market Brief with sections: Macro/Cross-Market, NQ, BTC, GOLD,
  Watch Today. Instrument Impact sections show only narratives material to
  NQ, BTC, or GOLD. Top Market Narratives are ranked by importance, not only
  by directional impact.
- An in-app alert feed (`Alert -> PostgreSQL -> FastAPI -> Dashboard`) with
  initial alert types: `emerging_narrative`, `confirmed_narrative`,
  `narrative_acceleration`, `high_impact_event_added_to_narrative`,
  `conflicting_information`, `unconfirmed_social_hype`.
- Human override controls: watch, mute, rename display title, mark
  irrelevant, mark invalid, reject event assignment, restore/undo override.
  Every correction creates an audit entry.
- One simple processing cycle (every 5 minutes): ingest, extract events,
  update narrative candidates, rebuild affected EvidencePacks, recalculate
  narrative state, evaluate alert rules. The Morning Brief is a separate job
  (on demand or on configurable schedule). No multiple staggered scheduler
  cadences in MVP.

## Constraints

Required quality gates:

- every material narrative has traceable evidence,
- every directional impact has rationale and evidence,
- unsupported market-language claims are prohibited (e.g. "markets are
  pricing in..." requires market data; otherwise use commentary-framed
  language),
- the user can navigate from briefing to source document,
- manually rejected mappings do not silently return,
- syndicated articles do not count as independent evidence,
- the user can understand the system's conclusion without rereading every
  source.

## Decisions

- Instrument impact direction replaces generic sentiment as the MVP's main
  directional concept (see `docs/architecture/domain-model.md`).
- LLMs are analytical components, not sources of truth; see
  `docs/architecture/ai-and-evidence.md` for decision boundaries.

## Assumptions

- MVP tracks exactly three instruments: NQ, BTC, GOLD.
- Only in-app alerts are required for MVP; no external delivery channels.

## Unresolved Questions

The following technical/architecture choices are not yet decided and are
planned to be resolved via a `grill-me` discovery session (see
`docs/product/roadmap.md` Priorities):

- LLM provider and model selection for event extraction and narrative
  candidate generation,
- persistence/data-access layer (ORM or direct SQL) on top of PostgreSQL,
- scheduler mechanism for the 5-minute processing cycle,
- dashboard frontend approach.

## References

- `docs/MVP_Vision_Architecture_Decisions.md` (source vision document)
- `docs/product/roadmap.md`
- `docs/architecture/domain-model.md`
- `docs/architecture/ai-and-evidence.md`
