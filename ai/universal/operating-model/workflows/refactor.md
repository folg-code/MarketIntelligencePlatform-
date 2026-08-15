# Workflow: Refactor

## Purpose

Define the lifecycle for improving internal code structure without intentionally changing externally observable behavior.

This workflow defines **when work moves, who owns each stage, which gates apply, and when escalation is required**.

Detailed refactoring, testing, and review procedures belong to skills, policies, and shared contracts.

---

## Entry Conditions

A refactor may enter this workflow when:

- the refactoring goal and target area are clear,
- expected behavior to preserve can be identified,
- the intended change does not introduce new product behavior,
- the affected scope can be bounded,
- blocking dependencies are resolved,
- no known blocking architecture or product decision remains unresolved.

If the requested work changes behavior, public contracts, domain semantics, or system boundaries, reroute it to the appropriate feature, bug, or architecture workflow.

---

## Roles

### Orchestrator
Owns workflow state, routing, context selection, gates, handoffs, and escalation.

### Architect
Participates when the refactor affects module boundaries, responsibilities, contracts, or broader architecture.

### Tester
Owns behavior-preservation validation when required by testing policy.

### Engineer
Owns the refactoring implementation within approved scope and boundaries.

### Reviewer
Performs independent review using fresh, minimum-sufficient context.

---

## Workflow

```text
READY
  ↓
PREPARATION
  ↓
ARCHITECTURE GATE
  ↓
BEHAVIOR BASELINE GATE
  ↓
IMPLEMENTATION
  ↓
VALIDATION
  ↓
REVIEW
  ↓
DOCUMENTATION GATE
  ↓
DONE
```

Any stage may transition to `BLOCKED`, clarification, replanning, or another workflow when current authority is insufficient.

---

## 1. READY

**Owner:** Orchestrator

Confirm that the task is sufficiently defined as a refactor.

At minimum:

- refactoring goal is explicit,
- target scope is bounded,
- behavior to preserve can be identified,
- no intentional product behavior change is included,
- blocking dependencies are resolved.

**Transitions:**

- ready → `PREPARATION`
- intended behavior change discovered → feature / bug workflow as appropriate
- architecture intent unclear → architecture routing
- not otherwise ready → planning / clarification

---

## 2. PREPARATION

**Owner:** Orchestrator

Prepare the minimum sufficient delegation context according to the Task Packet contract and context-routing policy.

Include only refactor-relevant context, preserved behavior, constraints, write scope, and required evidence.

**Transition:** → `ARCHITECTURE GATE`

---

## 3. ARCHITECTURE GATE

**Owner:** Orchestrator

Assess architecture impact:

```text
NONE
LOCAL
CROSS_MODULE
ARCHITECTURAL
UNKNOWN
```

**Routing:**

- `NONE` → `BEHAVIOR BASELINE GATE`
- `LOCAL` → `BEHAVIOR BASELINE GATE` within established boundaries
- `CROSS_MODULE` → Architect when required by architecture policy
- `ARCHITECTURAL` → architecture-change workflow
- `UNKNOWN` → Architect assessment

A refactor must not silently redefine module boundaries, responsibilities, public contracts, or domain semantics.

---

## 4. BEHAVIOR BASELINE GATE

**Owner:** Orchestrator coordinates Tester or the role selected by testing policy

Establish sufficient confidence in the behavior that must remain unchanged.

Use existing tests and other applicable evidence. Add characterization or preservation tests when required by testing policy and when current behavior is insufficiently protected.

The baseline should capture behavior, not the current internal implementation structure.

**Transitions:**

- preservation baseline sufficient → `IMPLEMENTATION`
- expected behavior unclear → clarification
- existing behavior appears defective → Orchestrator assesses dependency:
  - blocking or directly relevant → bug workflow
  - independent → create follow-up bug and continue the refactor
- requested outcome requires behavior change → feature workflow
- insufficient evidence → remain in baseline work or `BLOCKED`

---

## 5. IMPLEMENTATION

**Owner:** Engineer

Perform the smallest sufficient structural change that achieves the refactoring goal while preserving approved behavior and boundaries.

Avoid introducing unrelated cleanup, new abstractions, or speculative redesign outside the task scope.

If implementation reveals that completion requires a behavior change, architecture change, contract change, domain change, dependency change, or broader scope, stop the affected work and report it to the Orchestrator.

**Required handoff:** `ImplementationReport`

**Transitions:**

- implementation complete → `VALIDATION`
- local implementation issue → remain in `IMPLEMENTATION`
- behavior change required → feature / bug routing as appropriate
- architecture issue → architecture routing
- scope expansion required → replanning
- unresolved dependency → `BLOCKED`

---

## 6. VALIDATION

**Owner:** Tester or role selected by testing policy

Validate that:

- preserved behavior remains intact,
- required tests pass,
- no unintended public contract change occurred,
- required quality gates pass.

Only executed checks may be reported as verified.

**Required handoff:** `ValidationReport`

**Transitions:**

- pass → `REVIEW`
- behavior regression → `IMPLEMENTATION`
- architecture concern → architecture routing
- evidence reveals pre-existing defect → bug workflow or follow-up task
- missing required evidence → remain in `VALIDATION` or `BLOCKED`

---

## 7. REVIEW

**Owner:** Reviewer

Perform independent review using fresh, minimum-sufficient context.

The Reviewer should receive:

- refactor task and goal,
- behavior-preservation expectations,
- relevant change or diff,
- validation evidence,
- relevant contracts and architecture constraints.

Full implementation history should not be forwarded by default.

**Required handoff:** `ReviewReport`

**Routing:**

- `PASS` → `DOCUMENTATION GATE`
- `PASS_WITH_NOTES` → Orchestrator classifies notes, then continue or create follow-up work
- `CHANGES_REQUIRED` → finding routing / fix loop
- `BLOCKED` → Orchestrator resolves or escalates blocker
- unintended behavior or contract change → appropriate workflow
- architecture concern → architecture routing

Repeated or systemic findings should trigger reassessment rather than an unlimited fix loop.

---

## 8. DOCUMENTATION GATE

**Owner:** Orchestrator

Determine whether the accepted refactor changes durable project knowledge.

Documentation should be updated when the refactor changes documented:

- internal component responsibilities,
- module interactions,
- architecture structure,
- development constraints.

Do not update product documentation when externally observable behavior has not changed.

**Transitions:**

- documentation current → `DONE`
- update required → update and verify consistency → `DONE`

---

## 9. DONE

**Owner:** Orchestrator

Verify the applicable Definition of Done using available evidence.

At minimum:

- the refactoring goal is satisfied,
- required behavior-preservation evidence exists and passes,
- required quality checks pass,
- blocking review findings are resolved,
- no unauthorized behavior or architecture change was introduced,
- required documentation is current,
- no unresolved blocker remains.

Only then mark the refactor task `DONE`.

---

## BLOCKED

A refactor is `BLOCKED` when progress requires information, a dependency, evidence, or a decision that cannot be resolved within current authority.

Record the blocker using the shared task/blocker contract.

Independent work may continue when it does not depend on the blocker.

---

## Replanning and Escalation

Local implementation adjustments that preserve the refactor goal, behavior, contracts, scope, and approved boundaries do not require replanning.

Escalate or reroute when the work requires:

- changed product behavior,
- bug resolution outside the approved refactor scope,
- broader task scope,
- architecture or module-boundary changes,
- public contract or domain-semantic changes,
- new significant dependencies,
- changed milestone assumptions.

The Orchestrator selects the appropriate replanning or workflow level.

Milestone- or roadmap-level replanning does not occur inside this workflow.

---

## Handoffs

Use structured artifacts rather than full agent histories.

Typical handoffs include:

```text
TaskPacket
BehaviorBaseline / EvidenceRef
ImplementationReport
ValidationReport
ReviewReport
ArchitectureAssessment / ArchitectureProposal
BoundaryBreachReport
```

Exact schemas belong to shared contracts.

Each receiving role gets only the minimum sufficient context for its responsibility.

---

## Workflow Invariants

1. A refactor preserves the externally observable behavior defined by its approved behavior baseline.
2. Behavior to preserve is sufficiently understood before the refactor is accepted.
3. Refactoring does not silently change public contracts, domain semantics, or architecture boundaries.
4. Structural improvement remains within approved task scope.
5. Validation confirms behavior preservation using actual evidence when available.
6. Production implementation and independent review remain separated when review is required.
7. Detailed procedures remain owned by skills, policies, and contracts.

---

## Exit

A successful refactor exits this workflow as a `DONE` task with the required structural improvement, evidence that the approved behavior baseline remains preserved, review outcome, and any necessary durable documentation.

> The Refactor Workflow defines **when structural change moves, who owns each stage, which preservation gates apply, and when to reroute or escalate**.
