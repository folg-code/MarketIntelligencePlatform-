# Skill: Fix Bug

## Purpose

Apply the smallest production change that corrects a confirmed defect while preserving unrelated behavior.

## Use When

Use when:

- the defect is sufficiently evidenced,
- expected behavior is explicit,
- required regression expectations are established according to testing policy.

## Input

Use:

- TaskPacket,
- defect evidence,
- regression expectation when applicable,
- relevant code and contracts.

## Procedure

1. Inspect the narrowest relevant failure path.
2. Identify the smallest plausible correction consistent with expected behavior.
3. Implement the fix without unrelated cleanup.
4. Run the regression test and required relevant checks.
5. Confirm the original failure no longer occurs when practical.
6. Stop and report if the fix requires broader scope, architecture, contract, domain, or dependency changes.


Local checks support implementation feedback and do not replace independent validation when required by the workflow.

## Output

Produce an `ImplementationReport` using `.cursor/policy/reports.md`. Add the
bug variant field `root_cause:` when known.

## Boundaries

Do not:

- change expected behavior,
- perform speculative refactoring,
- fix unrelated problems,
- broaden the patch beyond what the defect requires,
- hide uncertainty about root cause or evidence.

> Fix the defect, not the neighborhood.
