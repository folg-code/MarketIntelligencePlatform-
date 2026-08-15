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

All implementation reports share this base shape:

```yaml
summary:
files_changed:
tests_added:
tests_run:
checks_run:
assumptions:
deviations:
problems_discovered:
unresolved:
```

Variants may add fields when useful:

```yaml
bug:
  root_cause:
refactor:
  structural_changes:
  behavior_checks:
```

Bug fixes may omit `root_cause:` when the fix is evidence-based but the exact
cause remains uncertain.

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
