# Workflow: Work Definition

## Purpose

Route unclear or not-yet-executable work from discovery into an approved,
execution-ready task.

Use this workflow before feature, bug, refactor, architecture-change, or
milestone execution when the work is not yet ready to delegate.

Use `.cursor/policy/workflow-rules.md` for shared blocking, handoff, context,
and invariant rules.

## Entry Conditions

Use when:

- the request needs clarification before execution,
- product requirements must be created or updated,
- approved requirements need an implementation-facing specification,
- a specification or authoritative work definition must become an executable
  task or issue.

Do not use this workflow to implement production changes.

## Roles

- Orchestrator: owns routing, context selection, stage gates, and escalation.
- Human/product authority: owns product, scope, roadmap, and protected domain
  decisions.
- Architect: supports technical specification when architecture boundaries,
  contracts, or protected semantics may be affected.
- Engineer: supports technical specification only inside established
  architecture and contracts.

## Flow

```text
READY
-> DISCOVERY
-> PRODUCT_REQUIREMENTS
-> TECH_SPEC
-> TICKETING
-> READY_FOR_EXECUTION
```

Skip stages only when their output already exists as authoritative project
truth.

## Stage Rules

### READY

Route to the earliest missing definition stage, or skip to
`READY_FOR_EXECUTION` when authoritative work definition already exists.

### DISCOVERY

Use before downstream definition stages when scope, outcome, assumptions, or
decisions are unclear.

### PRODUCT_REQUIREMENTS

Use when durable product truth must be created or updated before technical
specification or execution.

### TECH_SPEC

Use when approved requirements need an implementation-facing specification.

### TICKETING

Use when an approved specification or authoritative work definition must become
one or more executable tasks.

### READY_FOR_EXECUTION

Route ready tasks into the execution workflow selected by
`.cursor/policy/execution-map.md`. Tasks with unresolved blockers remain not
ready.

## Escalation

Escalate when product behavior, milestone scope, roadmap priority, protected
domain semantics, missing workflow/skill/policy, or approval authority is
unclear.
