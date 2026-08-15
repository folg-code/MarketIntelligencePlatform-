# Contract: Workflow Rules

## Purpose

Define shared workflow behavior once so individual workflow files can stay
small and token-efficient.

## Responsibility Layers

Use this hierarchy from general to specific:

```text
Execution Map -> who owns each workflow stage, which skill/policies apply, and
                 what handoff is required.
Workflow      -> stage order, transition rules, and exit conditions.
Skill         -> how to perform one delegated activity.
Policy        -> mandatory rules, criteria, and contracts.
```

Duplication test:

- Text about `who` belongs in `.cursor/policy/execution-map.md`.
- Text about `when`, `before`, `after`, or transition order belongs in a workflow.
- Text about `how` to execute a stage belongs in a skill.
- Text about `must`, `must not`, criteria, or constraints belongs in policy.

## Context Loading

- Start with `AGENTS.md`, `.cursor/policy/context-map.md`, and the directly
  relevant request, task, or issue.
- Open only the selected workflow and the role, skill, policy, project
  document, code, and test sections needed for the current stage.
- Prefer references, headings, search results, and narrow excerpts over full
  document loads.
- Expand context only when evidence shows the current task requires it.
- Do not forward full agent histories between stages.

## Standard Stages

When a workflow includes these stages, use the shared meaning below.

```text
READY
PREPARATION
ARCHITECTURE GATE
TESTING / BASELINE / REGRESSION GATE
IMPLEMENTATION
VALIDATION
REVIEW
DOCUMENTATION GATE
DONE
BLOCKED
REPLANNING / ESCALATION
```

- `READY`: confirm the task has enough authority, scope, expectations, and
  dependencies to proceed.
- `PREPARATION`: create or verify the minimum sufficient TaskPacket.
- `ARCHITECTURE GATE`: classify impact as `NONE`, `LOCAL`, `CROSS_MODULE`,
  `ARCHITECTURAL`, or `UNKNOWN`; route when authority is insufficient.
- `TESTING / BASELINE / REGRESSION GATE`: establish the evidence mode required
  by testing policy before accepting implementation.
- `IMPLEMENTATION`: make the smallest sufficient production change inside the
  approved scope and boundaries.
- `VALIDATION`: verify required behavior and quality gates with executed or
  accepted evidence.
- `REVIEW`: independently challenge correctness, scope, architecture, tests,
  and maintainability when review is required.
- `DOCUMENTATION GATE`: update durable documentation only when durable truth
  changed.
- `DONE`: close only when the applicable Definition of Done is satisfied.
- `BLOCKED`: record missing information, evidence, dependency, access, or
  authority that prevents useful approved progress.
- `REPLANNING / ESCALATION`: route changes in scope, behavior, architecture,
  contracts, domain semantics, dependencies, or milestone assumptions to the
  owning authority.

## Parallel Execution

Dispatch independent units of work concurrently instead of serially when
both conditions hold:

- no blocking dependency exists between them (neither consumes the other's
  output, per the governing plan/wave), and
- their declared `write_scope` (see `.cursor/policy/task-packet.md`) does
  not overlap for the stage being dispatched.

Read-only stages (`ARCHITECTURE_GATE` assessment, independent `VALIDATION`
checks against already-written code, `REVIEW`) carry no file-write risk and
should default to parallel dispatch whenever the units are independent,
even if their later `IMPLEMENTATION` stages cannot be.

If `write_scope` overlaps (e.g. two tickets both add to the same shared
module or the same linear migration chain), keep the writing stage
sequential even when the logical dependency graph would otherwise allow
parallelism — concurrent agents sharing one working tree can silently
clobber each other's edits. Prefer pipelining instead: start the next
independent unit's `IMPLEMENTATION` as soon as the current one's files are
written, without waiting for its `VALIDATION`/`REVIEW` to finish.

Re-verify `write_scope` disjointness before each parallel dispatch; do not
assume it was already checked for a similar-looking pair of tasks.

## Handoffs

Use structured artifacts instead of narrative histories. Common handoffs:

```text
TaskPacket
EvidenceRef
ImplementationReport
ValidationReport
ReviewReport
ArchitectureAssessment
ArchitectureProposal
ArchitectureDecision
BoundaryBreachReport
Blocker
```

Exact schemas belong to the relevant contract files, especially
`.cursor/policy/task-packet.md`, `.cursor/policy/reports.md`,
`.cursor/policy/evidence.md`, and `.cursor/policy/blockers.md`.

## Invariants

1. Work remains within approved scope and delegated authority.
2. Product behavior, public contracts, protected domain semantics,
   architecture boundaries, persisted data, external integrations, significant
   dependencies, and milestone outcomes are governed surfaces.
3. Claims of validation require executed checks or explicitly accepted existing
   evidence.
4. Local discoveries are routed by actual impact instead of being hidden inside
   the current task.
5. Detailed procedures live in skills, policies, and project source-of-truth
   documents, not in workflow files.
