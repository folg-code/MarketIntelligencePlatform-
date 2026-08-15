# Skill: Establish Behavior Baseline

## Purpose

Define the externally observable behavior that a refactor must preserve and establish sufficient evidence for it.

## Use When

Use before structural refactoring when preserved behavior must be made explicit.

## Input

Use:

- refactor goal,
- relevant requirements and contracts,
- existing tests,
- relevant runtime or behavioral evidence.

## Procedure

1. Identify the behavior that must remain unchanged.
2. Reuse existing tests and evidence where sufficient.
3. Add characterization or preservation tests only where meaningful behavior is otherwise unprotected.
4. Prefer stable external seams over internal implementation details.
5. Separate known accepted behavior from suspected defects.
6. Report ambiguity or defects that prevent a trustworthy baseline.

## Output

Produce a concise `BehaviorBaseline`:

```yaml
preserved_behavior:
evidence:
tests_added:
known_limitations:
suspected_defects:
unresolved:
```

## Boundaries

Do not:

- redefine product behavior,
- freeze accidental implementation details,
- fix discovered defects inside this skill,
- expand the refactor scope.

> Preserve behavior, not structure.
