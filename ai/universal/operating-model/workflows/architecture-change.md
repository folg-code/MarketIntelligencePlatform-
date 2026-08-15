# Workflow: Architecture Change

## Purpose

Define the lifecycle for introducing an approved change to system architecture, boundaries, responsibilities, contracts, or significant technical dependencies.

This workflow defines **when work moves, who owns each stage, which gates apply, and when escalation is required**.

Detailed architecture analysis, design, migration, implementation, testing, and review procedures belong to skills, policies, and shared contracts.

---

## Entry Conditions

An architecture change may enter this workflow when:

- the problem or architectural need is explicit,
- the affected system area can be identified,
- current constraints and relevant architecture context are available,
- the change cannot be handled safely as a local implementation decision,
- no known blocking product decision remains unresolved.

Typical triggers include changes to:

- module boundaries or responsibilities,
- public or cross-module contracts,
- architecture affected by accepted or required domain semantics,
- persistent data model with architectural impact,
- significant dependencies,
- integration patterns,
- system-wide technical structure.

If the requested work can be completed within existing boundaries and contracts, return it to the appropriate feature, bug, or refactor workflow.

---

## Roles

### Orchestrator
Owns workflow state, routing, context selection, gates, handoffs, and escalation.

### Architect
Owns architecture assessment, proposal, trade-off analysis, and architectural consistency.

### Human
Owns approval when the change exceeds delegated architectural authority or affects product/domain decisions requiring HITL.

---

## Workflow

```text
READY
  ↓
PREPARATION
  ↓
ARCHITECTURE ASSESSMENT
  ↓
ARCHITECTURE PROPOSAL
  ↓
APPROVAL GATE
  ↓
ARCHITECTURE DECISION
  ↓
DOCUMENTATION
  ↓
IMPLEMENTATION DERIVATION
  ↓
DONE
```

Any stage may transition to `BLOCKED`, clarification, replanning, or product/HITL routing when current authority is insufficient.

---

## 1. READY

**Owner:** Orchestrator

Confirm that the task is sufficiently defined for architectural analysis.

At minimum:

- architectural problem or need is explicit,
- affected scope can be identified,
- relevant current architecture is known,
- blocking dependencies are resolved enough for assessment,
- no unresolved product decision blocks the architecture decision.

**Transitions:**

- ready → `PREPARATION`
- architectural need unclear → clarification
- request can be handled locally → appropriate feature / bug / refactor workflow
- product decision required first → Human / product clarification
- not otherwise ready → planning / clarification

---

## 2. PREPARATION

**Owner:** Orchestrator

Prepare the minimum sufficient architecture context according to the Task Packet contract and context-routing policy.

Include only relevant:

- architecture documentation,
- domain contracts,
- ADRs,
- affected modules and interfaces,
- constraints,
- dependencies,
- task-specific decision boundaries.

**Transition:** → `ARCHITECTURE ASSESSMENT`

---

## 3. ARCHITECTURE ASSESSMENT

**Owner:** Architect

Assess the current state, the architectural problem, and the actual scope of change required.

The assessment should determine whether:

- a real architecture change is required,
- a local solution within existing boundaries is sufficient,
- product/domain clarification is needed before design,
- the change affects dependent tasks, modules, or milestone assumptions.

**Required handoff:** `ArchitectureAssessment`

**Transitions:**

- architecture change required → `ARCHITECTURE PROPOSAL`
- local change sufficient → reroute to feature / bug / refactor workflow
- product/domain decision required → Human / clarification
- insufficient information → `BLOCKED` / clarification
- broader planning impact discovered → replanning

---

## 4. ARCHITECTURE PROPOSAL

**Owner:** Architect

Define the smallest sufficient architectural change that resolves the approved problem.

The proposal should make explicit the affected:

- boundaries and responsibilities,
- contracts or interfaces,
- domain semantics when relevant,
- data model when relevant,
- dependencies,
- migration or compatibility concerns,
- implementation constraints,
- alternatives and meaningful trade-offs.

Do not expand the proposal beyond what is required to resolve the architectural problem.

**Required handoff:** `ArchitectureProposal`

**Transition:** → `APPROVAL GATE`

---

## 5. APPROVAL GATE

**Owner:** Orchestrator coordinates required authority

Determine whether the proposal can be accepted within delegated authority.

Approval follows project architecture and HITL policy.

Changes involving significant product behavior, domain semantics, public contracts, roadmap assumptions, or other explicitly protected decisions require Human approval.

**Transitions:**

- approved → `ARCHITECTURE DECISION`
- revision required → `ARCHITECTURE PROPOSAL`
- product/domain decision required → Human / clarification
- rejected → `CANCELLED` or replanning
- unresolved authority/dependency → `BLOCKED`

Implementation must not begin before required approval is complete.

---

## 6. ARCHITECTURE DECISION

**Owner:** Architect records the accepted decision; Orchestrator verifies required approval.

Convert the approved `ArchitectureProposal` into an explicit `ArchitectureDecision`.

The decision should identify the accepted option, governing constraints, affected boundaries/contracts, and required approval without duplicating the full proposal.

Architecture may represent and enforce accepted domain semantics, but must not originate protected domain decisions.

**Required handoff:** `ArchitectureDecision`

**Transitions:**

- decision recorded → `DOCUMENTATION`
- approval scope is ambiguous → `APPROVAL GATE`
- accepted decision cannot be represented consistently → `ARCHITECTURE PROPOSAL`
- unresolved product/domain decision → Human / clarification

---

## 7. DOCUMENTATION

**Owner:** Architect, coordinated by Orchestrator

Persist the accepted architecture as durable project knowledge before implementation work is delegated.

Update only the architectural sources of truth affected by the decision.

Typical updates may include:

- architecture overview,
- domain model representation of already accepted domain semantics,
- ADRs when required,
- architectural contracts,
- module boundaries and responsibilities,
- development constraints,
- migration or compatibility constraints.

Documentation should describe the accepted architecture, not temporary reasoning history.

The repository must contain sufficient durable architectural context for downstream implementation work.

**Transitions:**

- documentation current → `IMPLEMENTATION DERIVATION`
- documentation inconsistency discovered → `ARCHITECTURE DECISION` / `ARCHITECTURE PROPOSAL`
- required source of truth cannot be updated → `BLOCKED`

---

## 8. IMPLEMENTATION DERIVATION

**Owner:** Orchestrator

Translate the accepted `ArchitectureDecision` and updated architecture documentation into the minimum sufficient executable work.

Determine:

- required implementation issues or delegations,
- appropriate downstream workflow for each issue,
- dependency order,
- required testing/validation,
- migration needs,
- write boundaries,
- required review or Human QA.

Large architecture changes should normally be decomposed into multiple implementation issues rather than executed inside this workflow.

Typical downstream routing may include:

```text
feature
bug
refactor
```

Each downstream task receives only the relevant accepted architecture, contracts, constraints, and dependencies.

**Required handoff:** implementation issues / task definitions governed by the accepted `ArchitectureDecision`.

**Transitions:**

- implementation work derived → `DONE`
- accepted architecture proves insufficient during derivation → `ARCHITECTURE PROPOSAL`
- blocking dependency discovered → `BLOCKED`
- milestone/wave assumptions affected → replanning

---

## 9. DONE

**Owner:** Orchestrator

Verify the applicable Definition of Done using available evidence.

At minimum:

- an explicit `ArchitectureDecision` exists,
- required approvals were obtained,
- durable architecture documentation reflects the accepted decision,
- required ADRs are current,
- downstream implementation work has been derived when implementation is required,
- dependencies and routing for derived work are explicit,
- no unresolved blocker remains.

`DONE` means the architectural change has been accepted and integrated into the project's source of truth. It does not imply that all derived implementation work is complete.

---

## BLOCKED

An architecture change is `BLOCKED` when progress requires information, access, a dependency, evidence, or a decision that cannot be resolved within current authority.

Record the blocker using the shared task/blocker contract.

Independent approved work may continue when it does not depend on the blocker.

---

## Replanning and Escalation

Local implementation adjustments within downstream workflows do not require architectural replanning when they remain consistent with the accepted `ArchitectureDecision`.

Escalate or replan when new information changes:

- architectural problem definition,
- approved boundaries or responsibilities,
- public contracts or domain semantics,
- persistent data model assumptions,
- significant dependencies,
- implementation derivation or dependency sequencing across tasks,
- milestone or roadmap assumptions.

The Orchestrator selects the appropriate replanning level.

Milestone- or roadmap-level replanning does not occur inside this workflow.

---

## Handoffs

Use structured artifacts rather than full agent histories.

Typical handoffs include:

```text
TaskPacket
ArchitectureAssessment
ArchitectureProposal
ArchitectureDecision
ADR / ArchitectureDocumentationRef
DerivedImplementationTasks
BoundaryBreachReport
```

Exact schemas belong to shared contracts.

Each receiving role gets only the minimum sufficient context for its responsibility.

---

## Workflow Invariants

1. Architecture changes are explicit, assessed, and approved before downstream implementation begins.
2. An approved proposal becomes an explicit `ArchitectureDecision`.
3. Accepted architecture is persisted in durable project documentation before implementation work is delegated.
4. Product or protected domain decisions outside delegated authority are escalated rather than originated by the Architect.
5. Architecture may represent and enforce accepted domain semantics, but must not silently define protected domain semantics.
6. Architecture proposals remain limited to the problem they are intended to solve.
7. Downstream implementation work must remain governed by the accepted architecture and relevant contracts.
8. Architecture-change workflow derives implementation work; it does not execute that work.
9. Detailed procedures remain owned by skills, policies, and contracts.

---

## Exit

A successful architecture change exits this workflow as a `DONE` task with an accepted `ArchitectureDecision`, updated durable architecture documentation, and derived downstream implementation work where required.

Implementation proceeds through the appropriate feature, bug, refactor, or other execution workflow.

> The Architecture Change Workflow defines **how an architectural problem becomes an accepted, documented decision and executable downstream work, who owns each stage, which gates apply, and when to escalate**.
