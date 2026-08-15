# Skill: Validate Milestone Outcome

## Purpose

Validate whether the implemented milestone satisfies its approved outcome as an integrated system result.

Do not simply repeat task-level validation.

## Use When

Use after milestone development reaches `READY FOR VALIDATION`.

## Input

Use:

- milestone outcome and acceptance expectations,
- milestone-relevant task outcomes and evidence,
- relevant architecture decisions,
- required integration and Human QA expectations.

Promote only milestone-relevant evidence.

## Procedure

1. Identify the critical capabilities and flows that define milestone success.
2. Reuse valid task-level evidence where sufficient.
3. Execute milestone-level integration or system checks required to validate the outcome.
4. Verify that required capabilities work together coherently.
5. Identify localized defects separately from milestone-level plan or architecture failures.
6. Record missing or conflicting evidence explicitly.
7. Determine whether the milestone outcome is supported by the available evidence.

## Output

Produce a `MilestoneValidationReport`:

```yaml
outcome_checked:
capabilities:
integration_checks:
evidence_reused:
new_evidence:
failures:
missing_evidence:
localized_findings:
milestone_level_findings:
verdict: PASS | FAIL | BLOCKED
```

## Boundaries

Do not:

- rerun all task validation without need,
- mark task completion as milestone proof,
- hide deferred or missing evidence,
- redefine milestone outcome,
- implement fixes inside validation.

> Validate the integrated outcome, not the task list.
