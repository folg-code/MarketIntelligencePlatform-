# Skill: To Ticket

## Purpose

Transform an approved specification or other authoritative work definition into
an executable task or issue.

Create the smallest durable unit of work that can pass Definition of Ready and
enter the appropriate execution workflow.

This skill materializes one selected work item into an executable task. It does
not select the milestone wave; use `plan-wave` for wave selection and sequencing.

Prefer vertical tracer-bullet tasks: thin end-to-end slices that can be
integrated, exercised, and used for feedback.

## Use When

Use when:

- relevant product requirements are approved when applicable,
- the required behavior or technical work is sufficiently defined,
- dependencies and boundaries are understood well enough to define executable work.

Skip when further product, domain, or architecture decisions are still required.

## Input

Use:

- the governing specification or authoritative work definition,
- relevant product requirement references when applicable,
- relevant architecture decisions or contracts,
- only the dependency context needed to define the task.

Do not repeat discovery or redesign the governing work definition.

## Procedure

1. Identify the smallest coherent executable unit of work.
2. Prefer the smallest vertical slice that crosses the necessary layers for one
   narrow behavior.
3. Define the task goal and explicit scope.
4. Derive acceptance criteria from the governing work definition.
5. Record relevant dependencies and governing references.
6. Capture task-specific constraints and exclusions.
7. Classify the task type and required downstream workflow.
8. Identify unresolved blockers.
9. Verify that the ticket does not introduce behavior or decisions absent from
   its governing sources.
10. Determine readiness by applying `.cursor/policy/readiness.md`.

If the work is too large or contains independent outcomes, split it into
multiple tickets with explicit dependencies.

Prefer splitting by user-visible or system-observable behavior rather than by
technical layer.

Avoid planning broad horizontal tasks such as "build all database models",
"build all API endpoints", or "build all UI screens" unless a horizontal
enabling step is genuinely required before any useful vertical slice can be
delivered.

A good tracer-bullet task should usually:

- touch only the layers needed for one narrow behavior,
- integrate early with real project boundaries where practical,
- produce executable evidence,
- expose architecture, integration, and requirement feedback quickly,
- leave the next slice easier to plan.

## Output

Create or update the durable task or issue.

At minimum, represent:

```yaml
task:
  id:
  type:
  goal:

scope:
  included:
  excluded:

acceptance_criteria:

dependencies:
  tasks:
  technical:
  external:
  decisions:

references:
  product:
  specification:
  architecture:

constraints:

blockers:

routing:
  workflow:

feedback:
  integration_point:
  evidence:
  next_learning:

readiness:
  status: READY | NOT_READY
```

Use the project's established issue format when one exists.

The structure above defines required information, not a mandatory presentation
format.

`READY` means the ticket satisfies the project's Definition of Ready; it does
not mean execution has started.

A ticket with unresolved blockers remains `NOT_READY`.

## Boundaries

Do not:

- invent product behavior,
- make new architecture or domain decisions,
- redesign the governing work definition,
- include implementation details that belong to the Engineer,
- create a TaskPacket,
- select or replan a milestone wave,
- hide unresolved blockers,
- combine unrelated outcomes into one ticket,
- split work by technical layer when a vertical slice is possible.

> Convert authoritative work definition into the smallest executable vertical
> unit of work.
