# Workflow: Architecture Change

## Purpose

Route a change to architecture, boundaries, responsibilities, contracts, data
model assumptions, or significant dependencies into an accepted documented
decision and derived implementation work.

Use `.cursor/policy/workflow-rules.md` for shared blocking, handoff, context,
and invariant rules.

## Entry Conditions

Use when:

- the architectural problem or need is explicit,
- affected system area and constraints can be identified,
- the change cannot be handled safely as a local implementation decision,
- no blocking product or protected-domain decision remains unresolved.

If the work can be completed inside existing boundaries and contracts, reroute
to feature, bug, or refactor workflow.

## Roles

- Orchestrator: routing, context selection, gates, approvals, downstream work.
- Architect: assessment, proposal, trade-offs, consistency, decision record.
- Human: approval for product behavior, protected domain decisions, roadmap
  assumptions, or authority beyond delegation.

## Flow

```text
READY
-> PREPARATION
-> ARCHITECTURE ASSESSMENT
-> ARCHITECTURE PROPOSAL
-> APPROVAL GATE
-> ARCHITECTURE DECISION
-> DOCUMENTATION
-> IMPLEMENTATION DERIVATION
-> DONE
```

## Stage Rules

### READY

Confirm problem, affected scope, relevant current architecture, dependencies,
and authority. Clarify when the architectural need is not explicit.

### PREPARATION

Prepare the minimum sufficient architecture context:

- relevant architecture docs and ADRs,
- domain contracts and protected semantics,
- affected modules and interfaces,
- constraints and dependencies,
- task-specific decision boundaries.

### ARCHITECTURE ASSESSMENT

Architect determines whether a real architecture change is required, a local
solution is sufficient, product/domain clarification is needed, or dependent
tasks and milestone assumptions are affected.

Required handoff: `ArchitectureAssessment`.

### ARCHITECTURE PROPOSAL

Architect defines the smallest sufficient change, including affected
boundaries, contracts, data model, dependencies, migration or compatibility
concerns, implementation constraints, alternatives, and meaningful trade-offs.

Required handoff: `ArchitectureProposal`.

Do not expand the proposal beyond the approved architectural problem.

### APPROVAL GATE

Orchestrator confirms whether the proposal can be accepted within delegated
authority. Product behavior, protected domain semantics, public contracts,
roadmap assumptions, or high-impact changes require Human approval.

Implementation must not begin before required approval is complete.

### ARCHITECTURE DECISION

Convert the approved proposal into an explicit `ArchitectureDecision` that
records accepted option, governing constraints, affected boundaries/contracts,
and approval scope without duplicating the full proposal.

Architecture may represent accepted domain semantics; it must not originate
protected domain decisions.

### DOCUMENTATION

Persist accepted architecture as durable project truth before downstream
implementation is delegated. Update only affected sources of truth, such as
architecture overview, ADRs, domain-model representation of accepted semantics,
contracts, module responsibilities, or migration constraints.

### IMPLEMENTATION DERIVATION

Orchestrator derives executable downstream tasks with workflow route,
dependency order, write boundaries, testing, migration needs, and review or
Human QA requirements.

Large architecture changes should normally become multiple downstream tasks.

### DONE

Close when an explicit decision exists, required approvals are captured,
durable docs are current, downstream implementation work is derived when
needed, dependencies are explicit, and no unresolved blocker remains.

`DONE` for this workflow does not mean all derived implementation is complete.

## Escalation

Replan when new information changes the architectural problem, approved
boundaries, public contracts, protected domain semantics, persistent data model,
significant dependencies, implementation sequencing, or milestone/roadmap
assumptions.
