# Workflow: Milestone Development

## Purpose

Define the lifecycle for developing an approved milestone through rolling-wave planning and coordinated execution.

This workflow defines **how milestone work is planned progressively, how executable work is selected and routed, how dependencies and discoveries affect the plan, and when the milestone should continue, replan, or move to validation**.

Detailed execution procedures belong to downstream workflows, skills, policies, and shared contracts.

---

## Entry Conditions

A milestone may enter this workflow when:

- the milestone outcome is explicit,
- milestone scope and boundaries are sufficiently defined,
- major known dependencies are identified,
- blocking product decisions required to begin are resolved,
- relevant product and architecture context is available,
- the milestone is approved for execution.

The milestone does not need a fully detailed implementation plan before entering this workflow.

Only the current and near-term work needs to be executable.

---

## Roles

### Orchestrator
Owns milestone workflow state, rolling-wave coordination, dependency-aware routing, execution tracking, replanning classification, and milestone readiness gates.

### Architect
Participates when planning or execution reveals architecture decisions, cross-module constraints, or architecture changes that affect milestone execution.

### Human
Owns milestone-level scope, outcome, priority, and other decisions outside delegated authority.

Downstream execution roles operate through their respective task workflows.

---

## Workflow

```text
READY
  ↓
MILESTONE BASELINE
  ↓
WAVE PLANNING
  ↓
EXECUTION DISPATCH
  ↓
PROGRESS INTEGRATION
  ↓
WAVE REVIEW
  ↓
MILESTONE READINESS GATE
       ├── CONTINUE → WAVE PLANNING
       ├── REPLAN   → REPLANNING
       └── READY    → MILESTONE VALIDATION
```

Execution within a wave may proceed concurrently when dependencies and approved boundaries allow it.

---

## 1. READY

**Owner:** Orchestrator

Confirm that the milestone is sufficiently defined to begin progressive execution.

At minimum:

- milestone outcome is explicit,
- scope boundaries are understood,
- major dependencies are known,
- no blocking product decision prevents execution,
- sufficient context exists to plan the first wave.

**Transitions:**

- ready → `MILESTONE BASELINE`
- milestone intent unclear → planning / Human clarification
- blocking architecture decision → architecture routing
- not otherwise ready → `BLOCKED`

---

## 2. MILESTONE BASELINE

**Owner:** Orchestrator

Establish the current milestone execution baseline.

Identify:

- milestone outcome,
- approved scope and exclusions,
- known dependencies,
- accepted architecture constraints,
- already completed work,
- unresolved risks or decisions,
- current execution state.

The baseline should be sufficient to plan the next wave without loading unnecessary project history.

**Transition:** → `WAVE PLANNING`

---

## 3. WAVE PLANNING

**Owner:** Orchestrator

Plan the smallest useful next wave of work.

A Wave is a planning and coordination boundary, not an execution unit. Tasks are execution units and run through their appropriate downstream workflows.

Select work that:

- contributes directly to the milestone outcome,
- is sufficiently understood to become executable,
- respects dependency order,
- can proceed within current product and architecture authority.

Detail the current wave enough for execution.

Keep later waves progressively less detailed.

For selected work:

- formalize tasks where required,
- establish dependencies,
- ensure applicable Definition of Ready,
- select the appropriate downstream workflow.

Typical routing includes:

```text
feature
bug
refactor
architecture-change
```

Do not create detailed implementation plans for distant work unless required by a current dependency or decision.

**Transitions:**

- executable wave prepared → `EXECUTION DISPATCH`
- architecture decision required before execution → architecture-change workflow
- milestone assumption invalidated during planning → `REPLANNING`
- blocking product decision → Human
- insufficient information → `BLOCKED` / clarification

---

## 4. EXECUTION DISPATCH

**Owner:** Orchestrator

Dispatch ready tasks into their appropriate downstream workflows according to dependencies and available authority.

Independent tasks may run concurrently.

Do not block the entire wave because one task is blocked when other approved work can proceed safely.

The milestone workflow does not execute task-level implementation itself.

It delegates execution and tracks resulting task states and structured outcomes.

**Transitions:**

- active downstream work exists → `PROGRESS INTEGRATION`
- no executable work because of blocker → `BLOCKED`
- newly discovered milestone-level issue → `REPLANNING`

---

## 5. PROGRESS INTEGRATION

**Owner:** Orchestrator

Integrate structured outcomes from downstream workflows into the current milestone state.

Track only information that affects milestone execution, such as:

- completed tasks,
- blocked tasks,
- dependency changes,
- newly discovered technical work,
- architecture decisions,
- scope-relevant discoveries,
- evidence that milestone assumptions may be wrong.

Local task implementation details remain owned by task-level workflows and reports.

New technical work outside an existing task may be added when it remains inside approved milestone scope.

Changes to milestone outcome or scope require Human authority.

Route new discoveries according to their actual impact:

```text
task-local
→ downstream task workflow

architecture
→ architecture-change workflow

milestone planning
→ REPLANNING

product / scope
→ Human / product authority
```

Do not promote a local discovery to milestone replanning unless it materially affects milestone execution.

**Transitions:**

- wave work still active → remain in `PROGRESS INTEGRATION`
- wave reaches review point → `WAVE REVIEW`
- milestone assumption materially invalidated → `REPLANNING`
- unresolved external or decision dependency → `BLOCKED` as appropriate

---

## 6. WAVE REVIEW

**Owner:** Orchestrator

Review the completed or sufficiently progressed wave before committing to the next one.

Determine:

- what was actually delivered,
- which planned work remains,
- which assumptions were confirmed or invalidated,
- what new dependencies or technical debt appeared,
- whether architecture or scope changed,
- whether the next planned work still makes sense.

Do not mechanically continue the previous plan when new evidence changes the best execution path.

A Wave Review may occur before all planned tasks are complete when new evidence materially affects the remaining execution plan.

**Transitions:**

- milestone still requires work and plan remains valid → `MILESTONE READINESS GATE`
- execution plan requires adjustment → `REPLANNING`
- blocking decision discovered → appropriate escalation

---

## 7. MILESTONE READINESS GATE

**Owner:** Orchestrator

Evaluate the milestone against its approved outcome and current evidence.

Choose exactly one direction:

### CONTINUE

Use when:

- milestone outcome is not yet satisfied,
- remaining work is still within approved scope,
- the current milestone assumptions remain valid,
- another execution wave can be planned safely.

**Transition:** → `WAVE PLANNING`

### REPLAN

Use when:

- dependency structure materially changed,
- milestone assumptions were invalidated,
- architecture changed the execution path,
- remaining work no longer matches the current plan,
- significant new work is required inside milestone scope.

**Transition:** → `REPLANNING`

### READY FOR VALIDATION

Use when:

- required milestone capabilities appear complete,
- required downstream tasks are complete, or explicitly classified as non-blocking for milestone validation,
- no unresolved blocker prevents milestone evaluation,
- remaining items do not prevent validation of the milestone outcome.

**Transition:** → milestone-validation workflow

The milestone is not marked complete inside this workflow.

---

## REPLANNING

**Owner:** Orchestrator coordinates required authority

Replanning updates the execution model using current evidence.

The Orchestrator may autonomously adjust:

- task sequencing,
- wave composition,
- task decomposition,
- dependency relationships,
- downstream workflow routing,
- technical follow-up work within approved milestone scope.

Local implementation choices remain owned by the applicable downstream workflow and implementation role.

Escalate when replanning affects:

- milestone outcome,
- milestone scope,
- product behavior not already approved,
- roadmap assumptions,
- protected domain decisions,
- significant architecture requiring separate approval.

After replanning:

- executable milestone remains valid → `WAVE PLANNING`
- milestone cannot proceed → `BLOCKED` / Human decision
- milestone should be replaced or cancelled → appropriate planning authority

---

## BLOCKED

A milestone is `BLOCKED` only when no safe, approved milestone work can progress because required information, dependencies, evidence, or decisions are unavailable.

A blocked task does not automatically block the milestone.

The Orchestrator should distinguish:

```text
TASK BLOCKED
→ independent milestone work may continue

WAVE BLOCKED
→ replan or execute another independent wave when possible

MILESTONE BLOCKED
→ no approved useful work can proceed
```

Record blockers using the shared task/dependency contracts.

---

## Dependency Rules

Dependencies determine execution order, not documentation order.

The Orchestrator should maintain enough dependency information to answer:

- what can execute now,
- what is blocked,
- what is blocked by what,
- which work can proceed independently,
- whether a newly discovered dependency changes the current wave or milestone plan.

Do not serialize independent tasks without a real dependency.

Do not begin dependent tasks before their required upstream decision, contract, or implementation is available.

---

## Planning Rules

Milestone planning follows:

> **Plan broadly, slice vertically, integrate early, replan deliberately.**

The current wave should be detailed enough to execute.

The next wave may be reasonably defined.

Later work should remain broad until new evidence makes detailed planning useful.

The milestone workflow should not maintain a speculative task tree several waves ahead.

Prefer vertical tracer bullets over horizontal layer-by-layer plans.

A tracer bullet is a thin end-to-end slice that exercises the real system path
needed for one narrow behavior. It should integrate early, produce executable
evidence, and expose requirement, architecture, and integration feedback before
the milestone accumulates too much unintegrated work.

Horizontal enabling work is allowed only when it is genuinely required before a
useful vertical slice can be delivered. Keep such work small and connect it to
the next planned tracer bullet.

---

## Handoffs

Use structured artifacts rather than full downstream agent histories.

Typical milestone-level inputs and outputs include:

```text
MilestoneDefinition
WavePlan
Task / TaskRef
TaskOutcome
ArchitectureDecision
DependencyUpdate
Blocker
WaveReview
ReplanDecision
MilestoneReadinessDecision
```

Exact schemas belong to shared contracts.

Only milestone-relevant information should be promoted from task-level execution into milestone context.

---

## Workflow Invariants

1. Milestone development uses rolling-wave planning rather than fully detailed upfront planning.
2. A Wave is a planning and coordination boundary; Tasks are the execution units.
3. Tasks should prefer vertical tracer bullets that integrate early and produce feedback.
4. Tasks execute through their appropriate downstream workflows; the milestone workflow does not implement them directly.
5. Dependency constraints are respected without unnecessarily serializing independent work.
6. Task-level blockers do not automatically become milestone-level blockers.
7. New evidence may change the execution plan without silently changing the milestone outcome or scope.
8. Milestone-level scope, outcome, and protected product decisions remain under the appropriate Human authority.
9. `READY FOR VALIDATION` is distinct from milestone completion.
10. Detailed task procedures remain owned by downstream workflows, skills, policies, and contracts.

---

## Exit

A successful milestone-development workflow exits when the milestone is `READY FOR VALIDATION`.

The milestone then enters the milestone-validation workflow, where the delivered system is evaluated against the milestone outcome and acceptance expectations.

> The Milestone Development Workflow defines **how approved milestone scope becomes progressively planned and executed work, when to continue, when to replan, and when enough evidence exists to move to milestone validation**.
