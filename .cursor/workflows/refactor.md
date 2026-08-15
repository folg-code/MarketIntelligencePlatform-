# Workflow: Refactor

## Purpose

Route behavior-preserving structural improvement from approved goal to verified
completion.

Use `.cursor/policy/workflow-rules.md` for shared stage definitions, handoffs,
blocking rules, and invariants.

## Entry Conditions

Use when:

- the refactoring goal and target area are clear,
- externally observable behavior to preserve can be identified,
- no intentional product behavior change is included,
- affected scope is bounded,
- no blocking architecture or product decision remains unresolved.

If the request changes behavior, public contracts, protected domain semantics,
or system boundaries, reroute to feature, bug, or architecture-change workflow.

## Roles

- Orchestrator: routing, gates, context selection, handoffs, escalation.
- Tester: behavior-preservation baseline and validation when required.
- Engineer: structural implementation inside approved boundaries.
- Architect: module-boundary, responsibility, contract, or architecture impact.
- Reviewer: independent review with fresh minimum-sufficient context.

## Flow

```text
READY
-> PREPARATION
-> ARCHITECTURE GATE
-> BEHAVIOR BASELINE GATE
-> IMPLEMENTATION
-> VALIDATION
-> REVIEW
-> DOCUMENTATION GATE
-> DONE
```

## Stage Rules

### READY

Continue only when the refactor satisfies Definition of Ready.

### PREPARATION

Prepare the minimum sufficient TaskPacket.

### ARCHITECTURE GATE

Classify impact as `NONE`, `LOCAL`, `CROSS_MODULE`, `ARCHITECTURAL`, or
`UNKNOWN`.

Continue for `NONE` or `LOCAL`; route other impacts through the mapped
architecture path.

### BEHAVIOR BASELINE GATE

Establish behavior baseline before implementation when required.

### IMPLEMENTATION

Mapped owner performs implementation. Required handoff:
`ImplementationReport`.

### VALIDATION

Validate before review. Required handoff: `ValidationReport`.

### REVIEW

Review after validation when required. Required handoff: `ReviewReport`.

### DOCUMENTATION GATE

Run documentation gate before `DONE`.

### DONE

Close only when Definition of Done is satisfied.

## Escalation

Reroute or replan when the work requires changed behavior, bug resolution
outside approved scope, broader scope, architecture or module-boundary changes,
public contract or protected domain changes, significant dependencies, or
milestone assumption changes.
