# Skill: Plan Wave

## Purpose

Turn the current milestone state into the smallest useful next wave of executable work.

Plan only as far as current evidence justifies.

Prefer waves made of vertical tracer bullets: thin end-to-end slices that can be
integrated early and produce fast feedback.

## Use When

Use when:

- a milestone is active,
- the next execution wave must be selected,
- dependencies and current progress are known well enough to choose near-term work.

## Input

Use:

- milestone outcome and scope,
- current milestone state,
- relevant dependencies,
- known blockers and architecture constraints,
- candidate work already derived from approved sources.

## Procedure

1. Identify the smallest set of work that meaningfully advances the milestone.
2. Respect task, decision, technical, and external dependencies.
3. Prefer vertical slices that cross the necessary layers for one narrow behavior.
4. Prefer work that can integrate early and produce executable feedback.
5. Prefer work that can execute now or become ready with minimal preparation.
6. Avoid serializing independent work without a real dependency.
7. Detail only the current wave enough for execution.
8. Leave later work broad unless current decisions depend on it.
9. Route each selected item to the appropriate downstream workflow.

## Output

Produce a concise `WavePlan` containing:

```yaml
goal:
selected_work:
dependencies:
parallelizable:
integration_points:
feedback_expected:
blocked:
routing:
assumptions:
```

Omit empty sections.

## Boundaries

Do not:

- change milestone scope or outcome,
- invent new product behavior,
- create speculative detailed plans for distant work,
- split waves by technical layer when useful vertical slices are possible,
- perform task implementation,
- hide blockers or unresolved decisions.

> Plan broadly, slice vertically, integrate early.
