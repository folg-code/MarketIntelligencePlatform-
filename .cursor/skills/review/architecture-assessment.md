# Skill: Architecture Assessment

## Purpose

Determine whether a requested or discovered change requires architectural treatment and define the actual architectural scope.

## Use When

Use when architecture impact is `UNKNOWN`, `CROSS_MODULE` by policy, or potentially `ARCHITECTURAL`.

## Input

Use:

- problem or task context,
- relevant architecture documentation,
- affected contracts, modules, and ADRs,
- applicable domain constraints.

## Procedure

1. Identify the current architectural boundary and responsibility involved.
2. Determine whether the problem can be solved safely within existing boundaries.
3. Identify affected contracts, modules, dependencies, and persistent structures.
4. Detect product or domain decisions that must be resolved first.
5. Classify the required change as local or architectural.
6. Define the smallest architecture scope requiring further design.

## Output

Produce an `ArchitectureAssessment`:

```yaml
problem:
current_boundary:
impact:
affected:
architecture_change_required:
constraints:
decisions_required:
routing:
```

## Boundaries

Do not:

- design the full solution,
- invent protected product or domain decisions,
- expand the architecture scope beyond the problem,
- turn local implementation choices into architecture work.

> First decide whether architecture really needs to change.
