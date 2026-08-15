# Skill: Code Review

## Purpose

Independently challenge an implementation for correctness, scope compliance, architectural consistency, and maintainability.

## Use When

Use after required validation and with fresh, minimum-sufficient context.

## Input

Use:

- task and acceptance criteria,
- relevant diff or changed code,
- validation evidence,
- applicable contracts and architecture constraints.

Do not require full implementation history by default.

## Procedure

1. Verify that the change actually addresses the task and nothing materially beyond it.
2. Look for correctness defects, missed edge cases, and regression risks.
3. Check contract, domain, and architecture compliance.
4. Evaluate tests for meaningful behavioral coverage.
5. Distinguish blocking from non-blocking findings.
6. Classify findings so they can be routed correctly.
7. Produce a verdict based on evidence, not implementation confidence.

## Output

Produce a `ReviewReport`:

```yaml
blocking_findings:
non_blocking_findings:
architecture_findings:
testing_findings:
scope_findings:
verdict: PASS | PASS_WITH_NOTES | CHANGES_REQUIRED | BLOCKED
```

## Boundaries

Do not:

- implement the fix,
- broaden review into unrelated code,
- invent new requirements,
- reject valid local implementation choices solely by preference,
- treat passing tests as proof of complete correctness.

Use `PASS_WITH_NOTES` only when findings are explicitly non-blocking and can be
routed as follow-up work without delaying the current task.

> Review to falsify, not to confirm.
