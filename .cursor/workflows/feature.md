# Workflow: Feature

## Purpose

Route an implementation-ready product feature from approved scope to verified
delivery.

Use `.cursor/policy/workflow-rules.md` for shared stage definitions, handoffs,
blocking rules, and invariants.

## Entry Conditions

Use when all are true:

- goal, scope, and acceptance criteria are explicit,
- blocking dependencies are resolved,
- no blocking product, domain, or architecture decision remains unresolved,
- relevant project context can be identified narrowly.

If the request is not implementation-ready, return it to planning or
clarification.

## Roles

- Orchestrator: routing, gates, context selection, handoffs, escalation.
- Architect: architecture assessment when boundaries, contracts, dependencies,
  persisted data, or protected semantics may change.
- Tester: executable expectations and validation when required by testing
  policy.
- Engineer: production implementation inside approved boundaries.
- Reviewer: independent review with fresh minimum-sufficient context.

## Flow

```text
READY
-> PREPARATION
-> ARCHITECTURE GATE
-> TESTING GATE
-> IMPLEMENTATION
-> VALIDATION
-> REVIEW
-> DOCUMENTATION GATE
-> DONE
```

## Stage Rules

### READY

Continue only when the feature satisfies Definition of Ready. Otherwise route
to work-definition, clarification, or the appropriate authority.

### PREPARATION

Prepare the minimum sufficient TaskPacket.

### ARCHITECTURE GATE

Classify architecture impact:

```text
NONE
LOCAL
CROSS_MODULE
ARCHITECTURAL
UNKNOWN
```

Continue for `NONE` or `LOCAL`; route other impacts through the mapped
architecture support or architecture-change workflow.

### TESTING GATE

Select the testing mode and satisfy testing prerequisites before implementation.

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

Replan or reroute when new information affects scope, acceptance criteria,
product behavior, public contracts, protected domain semantics, architecture,
dependencies, or milestone assumptions.
