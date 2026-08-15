# Skill: Refactor Safely

## Purpose

Improve internal structure while preserving the approved behavior baseline and existing boundaries.

## Use When

Use when:

- the refactor goal is explicit,
- preserved behavior is sufficiently baselined,
- the change does not intentionally alter product behavior.

## Input

Use:

- TaskPacket,
- BehaviorBaseline,
- relevant code,
- applicable architecture and contracts.

## Procedure

1. Identify the smallest structural change that achieves the refactor goal.
2. Apply the change incrementally where practical.
3. Preserve public contracts, domain semantics, and approved boundaries.
4. Run behavior-preservation tests and required quality checks.
5. Avoid unrelated cleanup or speculative abstractions.
6. Stop and report if completion requires behavior, architecture, contract, dependency, or scope changes.


Local checks support implementation feedback and do not replace independent validation when required by the workflow.

## Output

Produce an `ImplementationReport` containing:

```yaml
summary:
structural_changes:
files_changed:
behavior_checks:
quality_checks:
assumptions:
problems_discovered:
unresolved:
```

## Boundaries

Do not:

- intentionally change externally observable behavior,
- redesign architecture silently,
- expand scope with unrelated cleanup,
- introduce abstractions for hypothetical needs,
- treat failing preservation tests as something to update automatically.

> Improve structure without moving the behavioral boundary.
