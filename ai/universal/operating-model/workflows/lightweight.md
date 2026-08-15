# Workflow: Lightweight Execution

## Purpose

Provide a low-ceremony path for small, local, reversible work.

This workflow prevents routine coding from turning into process maintenance.

## Use When

Use when all are true:

- the task is small and local,
- the likely change is reversible,
- expected behavior is clear,
- affected files can be identified narrowly,
- no governed decision appears to be involved.

## Do Not Use When

Escalate to the relevant full workflow when work may affect:

- product behavior or acceptance criteria,
- architecture boundaries or module responsibilities,
- public or cross-module contracts,
- protected domain semantics,
- persisted data or migrations,
- external integrations,
- significant dependencies,
- milestone scope, outcome, or roadmap assumptions.

## Default Flow

```text
READY
  -> ENGINEER
  -> LOCAL CHECKS
  -> SHORT REPORT
```

## Context

Load only:

- task request,
- directly affected code,
- directly relevant tests,
- one applicable skill or policy when useful.

Avoid loading milestone, architecture, product, or full workflow documentation
unless an escalation trigger appears.

## Output

Produce a short report:

```yaml
changed:
checks:
evidence:
unresolved:
```

Omit empty sections.

## Documentation

Do not update durable documentation unless the task changes durable truth.

Do not update operational planning documents unless the task materially changes
current execution state.

## Invariant

Lightweight execution is not permission to ignore risk. It is permission to keep
low-risk work small.
