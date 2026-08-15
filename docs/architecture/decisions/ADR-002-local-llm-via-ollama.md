# ADR-002: Local LLM via Ollama for Event Extraction and Narrative Candidate Generation

## Status

Accepted

## Context

The pipeline requires an LLM for event extraction (producing `extracted_facts`
and `source_claims` from Documents) and for narrative candidate generation.
The PRD's "Unresolved Questions" left the LLM provider/model choice open,
resolved via a `grill-me` discovery session with the product owner.

The MVP deployment target is a single local machine (see
`ADR-003-mvp-technical-stack-persistence-scheduler-deployment-dashboard.md`), which directly
constrains this choice: a cloud LLM API is not required to satisfy the MVP
and introduces cost and data-locality trade-offs that a local deployment does
not need to accept.

## Decision

Event extraction and narrative candidate generation use a local LLM served
via Ollama, running on the same machine as the rest of the platform. No
cloud LLM API is used for these pipeline stages in the MVP.

Drivers for this decision:

- zero per-call API cost, which matters for a 5-minute processing cycle that
  repeatedly re-runs extraction/candidate generation,
- data never leaves the machine, consistent with the local-single-machine
  deployment model and avoiding third-party data handling for source
  documents,
- operational consistency with the local-single-machine deployment target
  (no additional external network dependency for the core pipeline).

## Consequences

- Extraction/candidate-generation quality is expected to be weaker and/or
  slower than a frontier cloud API. This is an accepted MVP trade-off, not a
  permanent ceiling.
- This decision must be revisited if local-model quality proves insufficient
  in later milestones (e.g. too many missed events, unreliable narrative
  candidates that the validation layer cannot compensate for). Any change of
  provider is an architecture change and requires a superseding ADR.
- The LLM decision-boundary governance rule (`ADR-001`) still applies in
  full and is unaffected by this provider choice: local LLM output remains a
  candidate/proposal subject to the same validation layer.
- Local model/hardware capacity constrains acceptable model size and
  therefore extraction latency within the 5-minute processing cycle; this is
  a constraint on scheduler/pipeline design (see
  `docs/architecture/overview.md` Constraints), not a reason to introduce a
  distributed task queue.
- If deployment later moves beyond a single local machine (post-MVP), the
  provider decision should be re-evaluated alongside the deployment-target
  decision rather than assumed to carry over unchanged.

## References

- `docs/product/PRD.md` (Unresolved Questions; Decisions)
- `docs/architecture/decisions/ADR-001-llm-decision-boundaries.md`
- `docs/architecture/decisions/ADR-003-mvp-technical-stack-persistence-scheduler-deployment-dashboard.md`
- `docs/architecture/ai-and-evidence.md`
