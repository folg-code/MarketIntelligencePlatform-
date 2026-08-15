# Workflow: Feature

## Purpose

Define the lifecycle for implementing an implementation-ready product feature.

This workflow defines **when work moves, who owns each stage, which gates apply, and when escalation is required**.

Detailed execution procedures belong to skills, policies, and shared contracts.

---

## Entry Conditions

A feature may enter this workflow when:

- goal and scope are clear,
- acceptance criteria exist,
- blocking dependencies are resolved,
- required project context can be identified,
- no blocking product decision remains unresolved.

If these conditions are not met, return the task to the appropriate planning or clarification process.

---

## Roles

### Orchestrator
Owns workflow state, routing, context selection, gates, handoffs, and escalation.

### Architect
Participates when architecture assessment or an architectural decision is required.

### Tester
Owns executable expectations and independent validation when required by testing policy.

### Engineer
Owns production implementation within approved scope and boundaries.

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
TESTING GATE
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

Any stage may transition to `BLOCKED`, clarification, replanning, or architecture routing when current authority is insufficient.

---

## 1. READY

**Owner:** Orchestrator

Confirm that the task satisfies the applicable Definition of Ready.

At minimum:

- goal and scope are explicit,
- acceptance criteria exist,
- blocking dependencies are resolved,
- no blocking product decision remains open.

**Transitions:**

- ready → `PREPARATION`
- not ready → planning / clarification

---

## 2. PREPARATION

**Owner:** Orchestrator

Prepare the minimum sufficient delegation context according to the Task Packet contract and context-routing policy.

Include only task-relevant context, constraints, write scope, and required evidence.

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

- `NONE` → continue
- `LOCAL` → continue within established boundaries
- `CROSS_MODULE` → Architect when required by architecture policy
- `ARCHITECTURAL` → architecture-change workflow
- `UNKNOWN` → Architect assessment

After an accepted architecture decision, return with updated context or a revised task when required.

---

## 4. TESTING GATE

**Owner:** Orchestrator

Select the testing mode according to project testing policy.

If test-first execution is required, route to the appropriate Tester/TDD procedure before production implementation.

**Transitions:**

- testing prerequisites satisfied → `IMPLEMENTATION`
- behavior materially ambiguous → clarification
- testing exposes requirement or architecture issue → appropriate routing

---

## 5. IMPLEMENTATION

**Owner:** Engineer

Implement the smallest sufficient production change that satisfies the task within approved boundaries.

If implementation reveals a blocking ambiguity, boundary breach, required scope change, architecture issue, or unresolved dependency, stop the affected work and report it to the Orchestrator.

**Required handoff:** `ImplementationReport`

**Transitions:**

- implementation complete → `VALIDATION`
- local implementation issue → remain in `IMPLEMENTATION`
- architecture issue → architecture routing
- requirement ambiguity → clarification
- unresolved dependency → `BLOCKED`

---

## 6. VALIDATION

**Owner:** Tester or role selected by testing policy

Validate the implementation against acceptance criteria and required quality gates.

Only executed checks may be reported as verified.

**Required handoff:** `ValidationReport`

**Transitions:**

- pass → `REVIEW`
- implementation defect → `IMPLEMENTATION`
- architecture concern → architecture routing
- requirement ambiguity → clarification
- missing required evidence → remain in `VALIDATION` or `BLOCKED`

---

## 7. REVIEW

**Owner:** Reviewer

Perform independent review using fresh, minimum-sufficient context.

The Reviewer should receive:

- task and acceptance criteria,
- relevant change or diff,
- required validation evidence,
- relevant contracts and architecture constraints.

Full implementation history should not be forwarded by default.

**Required handoff:** `ReviewReport`

**Routing:**

- `PASS` → `DOCUMENTATION GATE`
- `PASS_WITH_NOTES` → Orchestrator classifies notes, then continue or create follow-up work
- `CHANGES_REQUIRED` → finding routing / fix loop
- `BLOCKED` → Orchestrator resolves or escalates blocker
- architecture concern → architecture routing

Repeated or systemic findings should trigger reassessment rather than an unlimited fix loop.

---

## 8. DOCUMENTATION GATE

**Owner:** Orchestrator

Determine whether the accepted implementation changes durable project knowledge.

If documentation must change, route the update to the appropriate owner.

**Transitions:**

- documentation current → `DONE`
- update required → update and verify consistency → `DONE`

---

## 9. DONE

**Owner:** Orchestrator

Verify the applicable Definition of Done using available evidence.

At minimum:

- acceptance criteria are satisfied,
- required validation evidence exists and passes,
- blocking review findings are resolved,
- required architecture procedures were followed,
- required documentation is current,
- no unresolved blocker remains.

Only then mark the feature task `DONE`.

---

## BLOCKED

A feature is `BLOCKED` when progress requires information, a dependency, evidence, or a decision that cannot be resolved within current authority.

Record the blocker using the shared task/blocker contract.

Independent work may continue when it does not depend on the blocker.

---

## Replanning and Escalation

Local implementation adjustments that preserve goal, scope, acceptance criteria, contracts, and approved boundaries do not require replanning.

Escalate or replan when new information affects:

- scope or acceptance criteria,
- product behavior,
- architecture or module boundaries,
- public contracts or domain semantics,
- task dependencies,
- milestone assumptions.

The Orchestrator selects the appropriate replanning level.

Milestone- or roadmap-level replanning does not occur inside this workflow.

---

## Handoffs

Use structured artifacts rather than full agent histories.

Typical handoffs include:

```text
TaskPacket
ImplementationReport
ValidationReport
ReviewReport
ArchitectureAssessment / ArchitectureProposal
BoundaryBreachReport
EvidenceRef
```

Exact schemas belong to shared contracts.

Each receiving role gets only the minimum sufficient context for its responsibility.

---

## Workflow Invariants

1. Required behavior is explicit before production implementation is accepted.
2. Decisions outside delegated authority are escalated rather than invented.
3. Production implementation and independent review remain separated when review is required.
4. Validation claims require actual evidence when primary evidence is available.
5. Work remains within approved task scope and boundaries.
6. Detailed procedures remain owned by skills, policies, and contracts.

---

## Exit

A successful feature exits this workflow as a `DONE` task with the required implementation, evidence, review outcome, and any necessary durable documentation.

> The Feature Workflow defines **when work moves, who owns each stage, which gates apply, and when to escalate**.
