# Skill: To Spec

## Purpose

Transform approved product requirements into an implementation-facing specification using existing project architecture and contracts.

## Input

Use:

- relevant PRD requirements,
- relevant architecture/domain documentation,
- applicable ADRs and contracts,
- relevant existing code and test patterns.

Inspect only the context needed for the change.

## Procedure

1. Identify the approved product behavior being implemented.
2. Map it onto existing system responsibilities, contracts, and domain vocabulary.
3. Identify affected components, interactions, dependencies, and edge cases.
4. Define the smallest sufficient technical behavior.
5. Define task-specific testing seams and reuse existing seams where practical.
6. Record implementation decisions that follow from existing architecture.
7. Escalate unresolved architecture, domain, or product decisions.
8. Verify traceability back to approved product requirements.

## Output

### Context
Short reference to the product problem and requirements.

### Technical Behavior
What the system must do.

### Implementation Decisions
- affected responsibilities/modules
- relevant interfaces/contracts
- data/schema implications
- interactions and dependencies
- technical constraints

### Testing Decisions
- behavior to verify
- preferred test seam
- relevant existing test patterns

### Out of Scope

### Assumptions / Unresolved

## Boundaries

Do not:

- duplicate the PRD,
- invent product behavior,
- create new architecture decisions silently,
- include implementation-level file paths or code,
- over-specify internal details that the Engineer can decide locally,
- create tickets; that belongs to `to-ticket`.