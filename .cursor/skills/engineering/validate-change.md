# Skill: Validate Change

## Purpose

Independently verify that an implemented task satisfies its acceptance expectations and required quality gates.

## Use When

Use after implementation when feature, bug, refactor, or similar task-level validation is required.

## Input

Use:

- task and acceptance criteria,
- relevant implementation result,
- required test and quality policy,
- relevant contracts and behavior expectations.

## Procedure

1. Map each required acceptance expectation to available validation evidence.
2. Execute the required relevant tests and checks.
3. Validate externally observable behavior at the appropriate seam.
4. Check for relevant regressions and contract violations.
5. Distinguish verified, inferred, assumed, and not checked.
6. Report missing evidence rather than treating it as success.

## Output

Produce a `ValidationReport`:

```yaml
acceptance_criteria_checked:
tests_executed:
quality_checks:
results:
failures:
missing_evidence:
regressions:
verdict: PASS | FAIL | BLOCKED
```

## Boundaries

Do not:

- modify production code,
- redefine acceptance criteria,
- accept narrative claims as executed evidence,
- repeat unrelated validation,
- hide missing coverage.

> Validation proves claims with evidence.
