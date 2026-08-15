# Skill: Architecture Proposal

## Purpose

Propose the smallest sufficient architectural change that resolves an approved architectural problem.

## Use When

Use after an `ArchitectureAssessment` confirms that architecture change is required.

## Input

Use:

- ArchitectureAssessment,
- relevant architecture and domain sources,
- applicable ADRs and contracts,
- approved constraints and product decisions.

## Procedure

1. Restate the architectural problem and governing constraints.
2. Define the smallest viable change to boundaries, responsibilities, contracts, or dependencies.
3. Describe meaningful alternatives only when they affect the decision.
4. Compare important trade-offs.
5. Identify migration, compatibility, data, and downstream implementation implications.
6. Make unresolved protected decisions explicit.
7. Recommend an option without treating it as approved.

## Output

Produce an `ArchitectureProposal`:

```yaml
problem:
proposed_change:
affected_boundaries:
affected_contracts:
dependencies:
migration:
alternatives:
tradeoffs:
risks:
unresolved:
recommendation:
```

## Boundaries

Do not:

- approve the proposal yourself,
- invent product or protected domain decisions,
- include implementation-level code,
- expand beyond the assessed architecture problem,
- begin downstream implementation.

> Propose the smallest architecture change worth approving.
