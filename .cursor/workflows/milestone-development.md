# Workflow: Milestone Development

## Purpose

Route an approved milestone through rolling-wave planning and coordinated
execution until it is ready for milestone validation.

Use `.cursor/policy/workflow-rules.md` for shared context, blocking, handoff,
and invariant rules.

## Entry Conditions

Use when:

- milestone outcome, scope, and boundaries are approved,
- major known dependencies are identified,
- blocking product decisions required to begin are resolved,
- relevant product and architecture context is available,
- current or near-term work can be made executable.

The milestone does not need a fully detailed implementation plan before entry.

## Roles

- Orchestrator: milestone state, rolling-wave planning, dependency-aware
  routing, progress integration, readiness decisions, replanning.
- Architect: architecture decisions, cross-module constraints, or architecture
  changes affecting milestone execution.
- Human: milestone outcome, scope, priority, roadmap, and protected product or
  domain decisions.
- Downstream roles: execute tasks through feature, bug, refactor, or
  architecture-change workflows.

## Flow

```text
READY
-> MILESTONE BASELINE
-> WAVE PLANNING
-> EXECUTION DISPATCH
-> PROGRESS INTEGRATION
-> WAVE REVIEW
-> MILESTONE READINESS GATE
   -> CONTINUE -> WAVE PLANNING
   -> REPLAN -> REPLANNING
   -> READY FOR VALIDATION -> MILESTONE VALIDATION
```

Independent tasks may run concurrently when dependencies and approved
boundaries allow.

## Stage Rules

### READY

Confirm milestone outcome, scope boundaries, dependencies, authority, and enough
context to plan the first wave.

### MILESTONE BASELINE

Establish outcome, approved scope and exclusions, known dependencies, accepted
architecture constraints, completed work, unresolved risks, decisions, and
current execution state.

Keep the baseline sufficient for the next wave, not a full project history.

### WAVE PLANNING

Plan the smallest useful next wave. A wave is a coordination boundary; tasks
are execution units.

Select work that contributes directly to the milestone outcome, is executable,
respects dependencies, and stays within current authority. Detail the current
wave enough to execute; keep later waves broad.

Typical downstream routes:

```text
feature
bug
refactor
architecture-change
```

Prefer vertical tracer bullets that integrate early and produce executable
evidence. Horizontal enabling work is allowed only when needed before a useful
vertical slice.

### EXECUTION DISPATCH

Dispatch ready tasks into downstream workflows. Do not serialize independent
tasks without a real dependency, and do not block the whole wave because one
task is blocked while other approved work can proceed.

### PROGRESS INTEGRATION

Promote only milestone-relevant outcomes:

- completed or blocked tasks,
- dependency changes,
- architecture decisions,
- scope-relevant discoveries,
- evidence that milestone assumptions may be wrong.

Local implementation details remain in task-level reports.

### WAVE REVIEW

Review delivered work, remaining planned work, confirmed or invalidated
assumptions, new dependencies, technical debt, architecture/scope changes, and
whether the next planned work still makes sense.

### MILESTONE READINESS GATE

Choose exactly one:

- `CONTINUE`: milestone outcome is not yet satisfied, remaining work is in
  scope, assumptions remain valid, and another safe wave can be planned.
- `REPLAN`: dependencies, assumptions, architecture, or remaining work changed
  materially.
- `READY FOR VALIDATION`: required milestone capabilities appear complete, no
  blocker prevents evaluation, and remaining items are non-blocking.

### REPLANNING

Orchestrator may adjust sequencing, wave composition, task decomposition,
dependencies, downstream workflow routing, and technical follow-up work inside
approved milestone scope.

Escalate to Human when replanning affects milestone outcome, scope, product
behavior, roadmap assumptions, or protected domain decisions.

### BLOCKED

The milestone is blocked only when no safe approved milestone work can progress.
A blocked task does not automatically block the milestone.

## Exit

Exit to milestone-validation workflow when the milestone is `READY FOR
VALIDATION`. Do not mark the milestone complete inside this workflow.
