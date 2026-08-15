# Skill: Establish Regression Test

## Purpose

Create or identify the smallest automated regression test that demonstrates a confirmed defect and protects the intended behavior.

## Use When

Use when the bug workflow requires an automated regression test before implementation.

## Input

Use:

- confirmed defect evidence,
- authoritative expected behavior,
- relevant existing test patterns and seams.

## Procedure

1. Select the highest stable existing test seam that can express the defect.
2. Reuse existing fixtures and test patterns where practical.
3. Write the smallest test that fails because of the confirmed defect.
4. Verify that the failure represents intended behavior, not implementation detail.
5. Run the test and capture the failing evidence.
6. Report when automation is inappropriate or the expected behavior remains ambiguous.

## Output

Produce regression-test evidence:

```yaml
test:
seam:
expected_failure:
result:
evidence:
unresolved:
```

## Boundaries

Do not:

- change production behavior,
- encode the intended implementation,
- create new test seams without need,
- redefine expected behavior.

> Protect the behavior, not the implementation.
