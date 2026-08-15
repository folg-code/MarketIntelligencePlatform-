# Development Policy: Engineering

## Purpose

Define project-wide engineering rules for implementing technical work safely,
minimally, and consistently.

Keep implementation decisions inside approved product, domain, architecture,
and task boundaries.

## Applies To

Applies to all production implementation and refactoring work unless a more
specific approved contract overrides it.

## Principles

- Implement only approved behavior.
- Prefer the smallest sufficient change.
- Prefer existing project patterns over speculative abstractions.
- Keep changes local when practical.
- Preserve unrelated behavior.
- Do not silently expand task scope.
- Treat public contracts, protected domain semantics, and architectural
  boundaries as governed interfaces.
- Introduce dependencies only when justified by the task and project policy.
- Keep configuration explicit and environment-specific values outside source
  code.
- Handle errors deliberately; do not hide failures that affect correctness.
- Preserve compatibility unless an approved change explicitly allows breaking
  it.
- Update durable technical documentation when implementation changes
  authoritative technical truth.

## Local Decisions

Engineers may make implementation-local decisions when they:

- remain inside approved architecture and contracts,
- do not change product behavior or acceptance criteria,
- do not create new protected domain semantics,
- do not create an independent architectural decision,
- do not materially broaden scope.

Local refactoring is allowed when incidental to the delegated task and necessary
for safe implementation.

Independent structural improvement belongs in the refactor workflow.

## Dependencies and Abstractions

- Reuse existing dependencies and abstractions when they remain suitable.
- Add abstraction only when it solves a concrete current problem.
- Avoid speculative extensibility.
- Significant new dependencies require the applicable approval path.
- Do not introduce infrastructure or framework changes as incidental
  implementation details.

## Contracts and Data

Changes affecting public APIs, persisted data, shared schemas, external
integrations, or cross-module contracts must follow the applicable architecture
and migration rules.

Do not silently reinterpret existing contracts.

## Technical Debt and Discoveries

Do not fix unrelated problems inside the current task.

Record or route discovered work according to its actual impact:

- task-local -> current workflow when in scope,
- independent technical debt -> follow-up work,
- defect -> bug workflow,
- architecture -> architecture-change workflow,
- product or protected domain ambiguity -> appropriate authority.

## Completion

Implementation is complete only when:

- delegated behavior is implemented,
- required local checks were actually executed,
- known limitations and discoveries are reported,
- required documentation changes are identified or completed,
- the implementation handoff is accurate.

Local implementation checks do not replace independent validation or review
when required by the workflow.

> Build the approved change, not a broader interpretation of it.
