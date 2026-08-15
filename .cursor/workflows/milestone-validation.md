# Workflow: Milestone Validation

## Purpose

Evaluate whether an implemented milestone satisfies its approved outcome and
can be closed.

Use `.cursor/policy/workflow-rules.md` for shared context, blocking, handoff,
and invariant rules.

## Entry Conditions

Use when:

- milestone development reached `READY FOR VALIDATION`,
- required downstream work is complete or explicitly non-blocking,
- milestone outcome and scope are still authoritative,
- required implementation and validation evidence is available,
- no blocker prevents milestone-level evaluation.

This workflow validates the integrated milestone outcome. It does not repeat
task-level implementation workflows.

## Roles

- Orchestrator: validation state, evidence aggregation, gates, final
  disposition, escalation.
- Tester: milestone-level behavioral and integration validation when required.
- Architect: architecture inconsistency or architectural acceptance criteria.
- Reviewer: milestone-level review when required.
- Human: product acceptance, Human QA, protected scope decisions.

## Flow

```text
READY
-> VALIDATION BASELINE
-> EVIDENCE ASSESSMENT
-> MILESTONE VALIDATION
-> MILESTONE REVIEW
-> HUMAN QA GATE
-> MILESTONE DECISION
   -> PASS -> DONE
   -> REOPEN -> MILESTONE DEVELOPMENT
   -> REPLAN -> PLANNING AUTHORITY
```

## Stage Rules

### READY

Confirm the milestone outcome is authoritative, required capabilities are
implemented, blocking downstream tasks are complete, incomplete tasks are
classified, evidence can be located, and no blocker prevents evaluation.

### VALIDATION BASELINE

Define the minimum milestone-level baseline:

- milestone outcome and acceptance expectations,
- required capabilities and integration behavior,
- relevant architecture decisions,
- required Human QA,
- accepted limitations and non-blocking deferred work.

Do not reproduce all task-level acceptance criteria.

### EVIDENCE ASSESSMENT

Aggregate only milestone-relevant evidence: task outcomes, validation reports,
review verdicts, integration tests, runtime evidence, migration results,
architecture decisions, and Human QA requirements.

Task completion alone is not proof that the milestone outcome is satisfied.

### MILESTONE VALIDATION

Validate integrated behavior and outcome: required capabilities working
together, critical flows, integrations, milestone-level regressions, and quality
gates. Required handoff: `MilestoneValidationReport`.

After remediation, repeat only affected validation unless broader evidence was
invalidated.

### MILESTONE REVIEW

When required, review the delivered milestone as a coherent system change:
cross-task consistency, architecture coherence, contract compatibility,
integration effects, scope drift, and unresolved technical concerns.

Do not repeat line-by-line task reviews that were already completed.

### HUMAN QA GATE

Run Human QA when required by policy or task characteristics such as
user-visible workflows, manual-only acceptance, UX behavior, critical business
flows, external side effects, or high-impact migration effects.

### MILESTONE DECISION

Choose exactly one disposition:

- `PASS`: outcome is satisfied, required validation and reviews pass, Human QA
  passes when required, blockers are resolved, and deferred work is
  non-blocking.
- `REOPEN DEVELOPMENT`: outcome remains valid and remaining problems are inside
  approved milestone scope.
- `REPLAN`: assumptions, scope, outcome, architecture path, product decisions,
  or roadmap assumptions require reconsideration.

Do not create partial pass states.

### DONE

Close only when the `PASS` disposition is justified by evidence, accepted
limitations and deferred work are explicit, project truth is current, and no
milestone blocker remains.

## Evidence Rules

Prefer evidence in this order:

```text
system / integration execution evidence
> task-level primary evidence
> structured validation and review reports
> narrative claims
```

Keep validation context smaller than the full milestone execution history.

## Exit

Exit as `DONE`, return to milestone development, or route to the appropriate
planning authority.
