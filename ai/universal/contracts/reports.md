# Contract: Reports

## Purpose

Standardize handoffs while keeping reports short.

Use full reports for standard or high-risk workflows. Use the short report for
lightweight execution.

## Lightweight Report

```yaml
changed:
checks:
evidence:
unresolved:
```

## ImplementationReport

```yaml
summary:
files_changed:
tests_added:
checks_run:
assumptions:
deviations:
problems_discovered:
unresolved:
```

## ValidationReport

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

## ReviewReport

```yaml
blocking_findings:
non_blocking_findings:
architecture_findings:
testing_findings:
scope_findings:
verdict: PASS | PASS_WITH_NOTES | CHANGES_REQUIRED | BLOCKED
```

## Rules

- Report only checks actually executed.
- Separate verified, inferred, assumed, and not checked.
- Omit empty sections when doing so improves clarity.
- Do not paste full logs unless the exact output is required as evidence.
