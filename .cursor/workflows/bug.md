# Workflow: Bug

## Purpose

Route a reported defect from evidence to verified fix while preserving
unrelated behavior.

Use `.cursor/policy/workflow-rules.md` for shared stage definitions, handoffs,
blocking rules, and invariants.

## Entry Conditions

Use when:

- observed behavior is described well enough to investigate,
- expected behavior can be derived from requirements, contracts, or accepted
  system behavior,
- the affected area can be bounded,
- no blocking product decision remains unresolved.

If expected behavior is unclear or the report is a new requirement, reroute to
clarification or the appropriate planning workflow.

## Roles

- Orchestrator: routing, gates, context selection, handoffs, escalation.
- Tester: reproduction, regression expectations, and validation when required.
- Engineer: production fix inside approved scope and boundaries.
- Architect: architecture routing when the defect or fix changes boundaries or
  contracts.
- Reviewer: independent review with fresh minimum-sufficient context.

## Flow

```text
READY
-> PREPARATION
-> DEFECT CONFIRMATION
-> ARCHITECTURE GATE
-> REGRESSION TEST GATE
-> IMPLEMENTATION
-> VALIDATION
-> REVIEW
-> DOCUMENTATION GATE
-> DONE
```

## Stage Rules

### READY

Continue only when the report is ready to investigate as a defect. Reroute
feature/change requests away from this workflow.

### PREPARATION

Prepare the minimum sufficient TaskPacket.

### DEFECT CONFIRMATION

Confirm the defect before implementation. If evidence or expected behavior is
insufficient, clarify or block.

### ARCHITECTURE GATE

Classify impact as `NONE`, `LOCAL`, `CROSS_MODULE`, `ARCHITECTURAL`, or
`UNKNOWN`.

A bug must not justify an unreviewed architecture change. Route architecture
impact through the mapped architecture path.

### REGRESSION TEST GATE

Establish regression expectations before implementation when required.

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

Replan or reroute when investigation shows unclear expected behavior, feature
scope rather than a defect, broader fix scope, architecture or contract impact,
protected domain impact, dependency changes, or milestone assumption changes.
