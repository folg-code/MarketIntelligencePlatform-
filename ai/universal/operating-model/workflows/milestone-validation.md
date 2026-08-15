# Workflow: Milestone Validation

## Purpose

Define the lifecycle for validating whether an implemented milestone satisfies its approved outcome and is ready to be closed.

This workflow defines **what is evaluated at milestone level, which evidence is required, who owns validation decisions, and when the milestone should pass, reopen development, or trigger replanning**.

Detailed test execution, review procedures, and evidence formats belong to skills, policies, downstream workflows, and shared contracts.

---

## Entry Conditions

A milestone may enter this workflow when:

- milestone development has reached `READY FOR VALIDATION`,
- required downstream work is complete or explicitly classified as non-blocking for milestone validation,
- milestone outcome and scope are still defined,
- required implementation and validation evidence is available,
- no known blocker prevents milestone-level evaluation.

This workflow validates the milestone outcome as an integrated result.

It does not repeat task-level implementation workflows.

---

## Roles

### Orchestrator
Owns validation workflow state, evidence aggregation, routing, gates, and final milestone disposition.

### Tester
Owns milestone-level behavioral and integration validation where required by testing policy.

### Architect
Participates when validation reveals architecture inconsistency or unresolved architectural acceptance criteria.

### Reviewer
Participates when milestone-level review is required by project policy.

### Human
Owns milestone acceptance when Human QA, product judgment, or protected scope decisions are required.

---

## Workflow

```text
READY
  ↓
VALIDATION BASELINE
  ↓
EVIDENCE ASSESSMENT
  ↓
MILESTONE VALIDATION
  ↓
MILESTONE REVIEW
  ↓
HUMAN QA GATE
  ↓
MILESTONE DECISION
       ├── PASS        → DONE
       ├── REOPEN      → MILESTONE DEVELOPMENT
       └── REPLAN      → PLANNING AUTHORITY
```

Any stage may transition to `BLOCKED` when required evidence, access, dependency, or authority is unavailable.

---

## 1. READY

**Owner:** Orchestrator

Confirm that the milestone is ready for milestone-level validation.

At minimum:

- milestone outcome is still authoritative,
- required capabilities are implemented,
- blocking downstream tasks are complete,
- non-complete tasks have been explicitly classified as non-blocking,
- required evidence can be located,
- no unresolved blocker prevents evaluation.

**Transitions:**

- ready → `VALIDATION BASELINE`
- missing required implementation work → milestone-development workflow
- milestone scope/outcome no longer valid → replanning
- evidence unavailable → `BLOCKED`

---

## 2. VALIDATION BASELINE

**Owner:** Orchestrator

Establish the minimum sufficient validation baseline for the milestone.

Identify:

- milestone outcome,
- milestone-level acceptance expectations,
- required capabilities,
- relevant architecture decisions,
- required integration behavior,
- required Human QA,
- known accepted limitations,
- non-blocking deferred work.

The baseline should define what must be true for the milestone to pass without reproducing all task-level acceptance criteria.

**Transition:** → `EVIDENCE ASSESSMENT`

---

## 3. EVIDENCE ASSESSMENT

**Owner:** Orchestrator

Aggregate and assess milestone-relevant evidence from downstream work.

Typical evidence may include:

- task outcomes,
- validation reports,
- review verdicts,
- integration-test results,
- runtime evidence,
- migration results,
- architecture decisions,
- Human QA requirements.

Only evidence relevant to milestone acceptance should be promoted into milestone context.

Do not treat task completion alone as proof that the milestone outcome is satisfied.

**Transitions:**

- evidence sufficient for validation → `MILESTONE VALIDATION`
- missing task-level evidence → downstream validation / milestone development
- conflicting evidence → clarification or targeted revalidation
- unresolved blocker → `BLOCKED`

---

## 4. MILESTONE VALIDATION

**Owner:** Tester or role selected by testing policy

Validate the milestone against its approved outcome and milestone-level acceptance expectations.

Focus on integrated behavior and outcome rather than repeating isolated task tests.

Validation should determine whether:

- required milestone capabilities work together,
- critical user or system flows succeed,
- required integrations behave correctly,
- milestone-level regressions are absent,
- required quality gates pass.

Only executed checks may be reported as verified.

**Required handoff:** `MilestoneValidationReport`

**Transitions:**

- validation passes → `MILESTONE REVIEW`
- localized defect → bug workflow, then return to milestone validation
- missing implementation → milestone-development workflow
- architecture inconsistency → architecture routing
- milestone assumption invalidated → replanning
- required evidence unavailable → `BLOCKED`

After downstream remediation, repeat only the validation scope potentially affected by the change unless the remediation invalidates broader milestone evidence.

---

## 5. MILESTONE REVIEW

**Owner:** Reviewer when required by policy; otherwise Orchestrator evaluates available review evidence

Evaluate the delivered milestone as a coherent system change.

Review should focus on milestone-level concerns such as:

- cross-task consistency,
- architecture coherence,
- contract compatibility,
- integration effects,
- accumulated scope drift,
- unresolved technical concerns that may affect milestone acceptance.

Do not repeat line-by-line task reviews that were already completed.

**Required handoff when performed:** `MilestoneReviewReport`

**Transitions:**

- no blocking concerns → `HUMAN QA GATE`
- localized implementation finding → appropriate downstream workflow
- architecture concern → architecture routing
- milestone-level concern → reopen development or replan as appropriate

---

## 6. HUMAN QA GATE

**Owner:** Orchestrator coordinates Human when required

Determine whether Human QA or product acceptance is required by milestone policy or task characteristics.

Typical triggers may include:

- user-visible workflows,
- manual-only acceptance expectations,
- UX behavior,
- critical business flows,
- external side effects,
- irreversible or high-impact migration effects.

If Human QA is not required, continue directly to milestone decision.

**Transitions:**

- Human QA not required → `MILESTONE DECISION`
- Human QA pass → `MILESTONE DECISION`
- localized issue → downstream workflow
- milestone outcome not accepted → reopen or replan
- Human unavailable when required → `BLOCKED`

---

## 7. MILESTONE DECISION

**Owner:** Orchestrator coordinates required authority

Evaluate all milestone-level evidence and choose exactly one disposition: `PASS`, `REOPEN DEVELOPMENT`, or `REPLAN`.

Do not introduce conditional or partial pass states. Non-blocking deferred work may coexist with `PASS` when it is explicitly recorded.

### PASS

Use when:

- milestone outcome is satisfied,
- required validation passes,
- required reviews are acceptable,
- required Human QA passes,
- no unresolved blocker prevents closure,
- remaining deferred work is explicitly non-blocking.

**Transition:** → `DONE`

### REOPEN DEVELOPMENT

Use when:

- milestone outcome remains valid,
- remaining problems are within approved milestone scope,
- additional implementation or fixes are required,
- no higher-level replanning is necessary.

**Transition:** → milestone-development workflow

### REPLAN

Use when validation shows that:

- milestone assumptions were invalid,
- milestone scope or outcome requires reconsideration,
- architecture materially changes the remaining path,
- required work exceeds approved milestone boundaries,
- product or roadmap decisions are required.

**Transition:** → appropriate planning authority

---

## DONE

**Owner:** Orchestrator

Mark the milestone complete only when the `PASS` disposition is justified by available evidence.

At minimum:

- milestone outcome is satisfied,
- required validation evidence exists and passes,
- blocking review findings are resolved,
- required Human QA is complete,
- required architecture decisions are reflected in project truth,
- accepted limitations and deferred work are explicit,
- no unresolved milestone blocker remains.

`DONE` closes the milestone.

Follow-up work that is explicitly non-blocking should continue as separate tasks or later milestone work.

---

## BLOCKED

Milestone validation is `BLOCKED` when the milestone cannot be evaluated because required evidence, access, dependency, or authority is unavailable.

Do not mark a milestone as failed merely because validation is blocked.

Resolve the blocker or return to the appropriate upstream workflow.

---

## Reopening and Replanning Rules

Validation findings should be routed according to their actual impact.

```text
localized implementation defect
→ bug / task workflow

missing milestone-scope implementation
→ milestone development

architecture inconsistency
→ architecture-change workflow

milestone plan invalidated
→ milestone replanning

product / scope / roadmap issue
→ Human / planning authority
```

Do not reopen the entire milestone for a local non-blocking issue.

Do not classify milestone-level failure as a local bug when the evidence shows that the approved plan or assumptions are wrong.

---

## Evidence Rules

Milestone validation should use the highest-quality available evidence.

Prefer:

```text
system / integration execution evidence
        >
task-level primary evidence
        >
structured validation and review reports
        >
narrative claims
```

Only milestone-relevant evidence should be aggregated.

The validation context should remain smaller than the full execution history of the milestone.

---

## Handoffs

Use structured artifacts rather than full task or agent histories.

Typical milestone-level inputs and outputs include:

```text
MilestoneDefinition
MilestoneReadinessDecision
TaskOutcome
EvidenceRef
MilestoneValidationReport
MilestoneReviewReport
HumanQAResult
MilestoneDecision
DeferredWorkRef
```

Exact schemas belong to shared contracts.

---

## Workflow Invariants

1. Milestone validation evaluates the integrated milestone outcome, not merely task completion.
2. Task-level evidence is reused rather than unnecessarily recreated.
3. Only milestone-relevant evidence is promoted into milestone validation context.
4. Local findings are routed locally unless they materially affect milestone acceptance.
5. Milestone closure requires evidence, not agent declarations.
6. Validation may reopen development without changing milestone scope.
7. Invalidated milestone assumptions trigger replanning rather than repeated local fixes.
8. `PASS` is distinct from having zero remaining non-blocking work.
9. `MILESTONE DECISION` produces exactly one disposition: `PASS`, `REOPEN DEVELOPMENT`, or `REPLAN`.
10. After remediation, revalidation is limited to affected scope unless broader milestone evidence was invalidated.
11. Detailed validation procedures remain owned by skills, policies, and contracts.

---

## Exit

A successful milestone-validation workflow exits with the milestone marked `DONE`.

If the milestone cannot be accepted, it exits toward either milestone development or the appropriate replanning authority.

> The Milestone Validation Workflow defines **how an implemented milestone is evaluated as an integrated outcome, when it can be closed, when development should reopen, and when validation evidence requires replanning**.
