# Skill: Implement Feature

## Purpose

Implement the smallest production change that satisfies an approved feature task within established boundaries.

## Use When

Use when:

- the feature task is ready,
- required behavior and acceptance criteria are explicit,
- testing prerequisites defined by policy are satisfied.

## Input

Use:

- TaskPacket,
- relevant code,
- required contracts and documentation,
- applicable testing expectations.

Load only context needed for the change.

## Procedure

1. Inspect the relevant implementation area and existing patterns.
2. Implement the smallest sufficient change satisfying the acceptance criteria.
3. Preserve existing architecture, contracts, and unrelated behavior.
4. Add or update implementation-local tests when assigned by testing policy.
5. Run required local checks that are available.
6. Stop and report if completion requires scope, architecture, contract, domain, or dependency changes outside authority.


Local checks support implementation feedback and do not replace independent validation when required by the workflow.

## Output

Produce an `ImplementationReport` containing:

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

Report only checks actually executed.

## Boundaries

Do not:

- redefine requirements,
- expand task scope,
- introduce significant dependencies without approval,
- perform unrelated refactoring,
- silently change public contracts, domain semantics, or architecture.

> Implement the approved behavior, not a broader solution.
