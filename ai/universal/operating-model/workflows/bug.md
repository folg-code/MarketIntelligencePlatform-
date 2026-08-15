# Workflow: Bug

## Purpose

Define the lifecycle for diagnosing and fixing a confirmed software defect.

This workflow defines **when work moves, who owns each stage, which gates apply, and when escalation is required**.

Detailed debugging, testing, and implementation procedures belong to skills, policies, and shared contracts.

---

## Entry Conditions

A bug may enter this workflow when:

- the reported behavior is sufficiently clear to investigate,
- expected behavior can be derived from requirements, contracts, or accepted system behavior,
- the affected area can be identified well enough to begin diagnosis,
- no known blocking product decision remains unresolved.

If expected behavior is unclear or the report may represent a new requirement rather than a defect, return the task to the appropriate clarification or planning process.

---

## Roles

### Orchestrator
Owns workflow state, routing, context selection, gates, handoffs, and escalation.

### Architect
Participates when the defect reveals an architecture issue or fixing it would require architectural change.

### Tester
Owns reproduction, regression expectations, and independent validation when required by testing policy.

### Engineer
Owns the production fix within approved scope and boundaries.

### Reviewer
Performs independent review using fresh, minimum-sufficient context.

---

## Workflow

```text
READY
  ↓
PREPARATION
  ↓
DEFECT CONFIRMATION
  ↓
ARCHITECTURE GATE
  ↓
REGRESSION TEST GATE
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

Confirm that the task is sufficiently defined to investigate as a bug.

At minimum:

- observed behavior is described,
- expected behavior can be identified,
- affected scope is bounded enough to begin,
- blocking dependencies are resolved,
- no blocking product decision remains open.

**Transitions:**

- ready → `PREPARATION`
- expected behavior unclear → clarification
- request is a feature/change rather than a defect → appropriate planning workflow
- not otherwise ready → planning / clarification

---

## 2. PREPARATION

**Owner:** Orchestrator

Prepare the minimum sufficient delegation context according to the Task Packet contract and context-routing policy.

Include only bug-relevant context, expected behavior, constraints, write scope, and required evidence.

**Transition:** → `DEFECT CONFIRMATION`

---

## 3. DEFECT CONFIRMATION

**Owner:** Tester or Engineer according to debugging/testing policy

Establish sufficient evidence that the reported behavior represents a real defect.

Prefer direct reproduction when practical. When direct reproduction is not practical, sufficient evidence may come from sources such as logs, traces, failing tests, production evidence, or deterministic analysis.

The evidence should isolate the failure sufficiently to distinguish the defect from configuration, environment, data, or requirement ambiguity.

**Required handoff:** defect evidence or the applicable validation report.

**Transitions:**

- defect sufficiently evidenced → `ARCHITECTURE GATE`
- insufficient evidence to confirm the defect → clarification / `BLOCKED`
- expected behavior is ambiguous → clarification
- root cause reveals architecture concern → architecture routing
- report does not represent a defect → close or reroute according to task policy

---

## 4. ARCHITECTURE GATE

**Owner:** Orchestrator

Assess whether the defect or its likely fix affects architecture boundaries.

Use the project's architecture-impact classification:

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

A bug must not be used as justification for an unreviewed architectural change.

---

## 5. REGRESSION TEST GATE

**Owner:** Orchestrator coordinates Tester

Select the testing mode according to project testing policy.

For defects that can be expressed as an automated regression test, establish the failing expectation before production implementation when required or preferred by policy.

The regression test should demonstrate the defect rather than encode the intended implementation.

**Transitions:**

- regression expectation established → `IMPLEMENTATION`
- automated regression test not appropriate → continue according to testing policy
- testing exposes requirement or architecture ambiguity → appropriate routing
- defect evidence is insufficient → `DEFECT CONFIRMATION`

---

## 6. IMPLEMENTATION

**Owner:** Engineer

Implement the smallest sufficient production change that corrects the confirmed defect within approved boundaries.

Avoid unrelated refactoring or speculative cleanup.

If the fix requires a scope change, architecture change, contract change, dependency change, or unresolved product decision, stop the affected work and report it to the Orchestrator.

**Required handoff:** `ImplementationReport`

**Transitions:**

- fix complete → `VALIDATION`
- defect not actually resolved → remain in `IMPLEMENTATION`
- root cause invalidates previous assumptions → replanning / fresh context
- architecture issue → architecture routing
- requirement ambiguity → clarification
- unresolved dependency → `BLOCKED`

---

## 7. VALIDATION

**Owner:** Tester or role selected by testing policy

Validate that:

- the original defect is no longer reproducible,
- applicable regression tests pass,
- relevant existing behavior remains intact,
- required quality gates pass.

Only executed checks may be reported as verified.

**Required handoff:** `ValidationReport`

**Transitions:**

- pass → `REVIEW`
- defect persists → `IMPLEMENTATION`
- regression introduced → `IMPLEMENTATION`
- architecture concern → architecture routing
- missing required evidence → remain in `VALIDATION` or `BLOCKED`

---

## 8. REVIEW

**Owner:** Reviewer

Perform independent review using fresh, minimum-sufficient context.

The Reviewer should receive:

- bug task and expected behavior,
- defect or regression evidence,
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
- architecture concern → architecture routing

Repeated failure to fix the same defect class should trigger reassessment rather than an unlimited fix loop.

---

## 9. DOCUMENTATION GATE

**Owner:** Orchestrator

Determine whether the accepted fix changes durable project knowledge.

Documentation should be updated when the defect exposed incorrect or incomplete:

- contracts,
- architecture knowledge,
- operational assumptions,
- testing expectations.

Do not create documentation solely because a bug was fixed.

**Transitions:**

- documentation current → `DONE`
- update required → update and verify consistency → `DONE`

---

## 10. DONE

**Owner:** Orchestrator

Verify the applicable Definition of Done using available evidence.

At minimum:

- the defect was reproduced or otherwise sufficiently evidenced,
- expected behavior is satisfied,
- required regression/validation evidence exists and passes,
- blocking review findings are resolved,
- required architecture procedures were followed,
- required documentation is current,
- no unresolved blocker remains.

Only then mark the bug task `DONE`.

---

## BLOCKED

A bug is `BLOCKED` when progress requires information, access, a dependency, evidence, or a decision that cannot be resolved within current authority.

Record the blocker using the shared task/blocker contract.

Independent investigation may continue when it does not depend on the blocker.

---

## Replanning and Escalation

Local debugging and implementation adjustments that preserve expected behavior, scope, contracts, and approved boundaries do not require replanning.

Escalate or replan when investigation shows that:

- expected behavior is not actually defined,
- the report represents a feature/change rather than a defect,
- the fix requires broader scope,
- architecture or module boundaries must change,
- public contracts or domain semantics are affected,
- dependencies or milestone assumptions change.

The Orchestrator selects the appropriate replanning level.

Milestone- or roadmap-level replanning does not occur inside this workflow.

---

## Handoffs

Use structured artifacts rather than full agent histories.

Typical handoffs include:

```text
TaskPacket
DefectEvidence
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

1. A bug fix targets defined expected behavior, not newly invented behavior.
2. The defect is reproduced or otherwise sufficiently evidenced before the fix is accepted.
3. Regression expectations are established before implementation when required by testing policy.
4. The fix remains as small and local as reasonably possible.
5. Decisions outside delegated authority are escalated rather than hidden inside the fix.
6. Validation confirms both defect resolution and required regression checks.
7. Production implementation and independent review remain separated when review is required.
8. Detailed procedures remain owned by skills, policies, and contracts.

---

## Exit

A successful bug exits this workflow as a `DONE` task with the required fix, regression/validation evidence, review outcome, and any necessary durable documentation.

> The Bug Workflow defines **when a defect moves from report to verified fix, who owns each stage, which gates apply, and when to escalate**.
