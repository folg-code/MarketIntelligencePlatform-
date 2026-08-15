# AGENTS.md

## Purpose

This file is the entry point for AI agents working in this repository.

It is a manifest, not a complete instruction set. Use it to locate the
smallest sufficient working set for the current task.

Do not load the entire repository by default.

## Default Operating Rule

Default to lightweight execution for small, local, reversible tasks.

Use the full workflow model only when the task may affect product behavior,
architecture, public contracts, protected domain semantics, persisted data,
external integrations, milestone outcomes, or other governed decisions.

In short:

```text
code lightly, escalate deliberately
```

## Universal AI Framework

Reusable AI engineering definitions are stored under `.cursor/`, organized
into exactly four folders:

```text
.cursor/
|-- agents/
|-- skills/
|-- workflows/
`-- policy/
```

### Workflows

```text
.cursor/workflows/
|-- index.md
|-- lightweight.md
|-- work-definition.md
|-- feature.md
|-- bug.md
|-- refactor.md
|-- architecture-change.md
|-- milestone-development.md
`-- milestone-validation.md
```

### Agents

```text
.cursor/agents/
|-- orchestrator.md
|-- architect.md
|-- engineer.md
|-- tester.md
`-- reviewer.md
```

Each file is both the role definition (mission, authority, boundaries) and
the Cursor-native subagent configuration invoked via the Task tool.

### Skills

```text
.cursor/skills/
|-- discovery/
|-- planning/
|-- engineering/
`-- review/
```

### Policy

Operating principles, shared contracts, development policy, and
project-specific AI configuration are consolidated under one folder:

```text
.cursor/policy/
|-- operating-principles.md
|-- task-packet.md
|-- reports.md
|-- readiness.md
|-- done.md
|-- evidence.md
|-- blockers.md
|-- execution-map.md
|-- workflow-rules.md
|-- engineering.md
|-- testing.md
|-- documentation.md
|-- contribution-policy.md
|-- context-map.md
`-- overrides.md
```

`context-map.md` defines which documentation should normally be loaded for
different task types.

`overrides.md` contains explicit project-level deviations from the universal
AI framework.

The files under `.cursor/` define how AI-assisted engineering is performed
in this repository. Keep `.cursor/` fully generic and project-agnostic:
agents, skills, workflows, and policy describe reusable process, not this
project's domain, product, or technology choices. Project-specific truth
belongs in `docs/` and `planning/`; `context-map.md` and `overrides.md` only
route to it or record explicit deviations from the universal process.

Use the framework from general to specific:

```text
execution map -> who owns work and which contracts apply
workflow      -> order of stages and transitions
skill         -> how to perform one stage
policy        -> mandatory rules and criteria
```

## Project-Specific Knowledge

Project truth should normally be stored under:

```text
docs/
|-- product/
|   |-- PRD.md
|   `-- roadmap.md
|-- architecture/
|   |-- overview.md
|   |-- domain-model.md
|   |-- ai-and-evidence.md
|   `-- decisions/
|-- development/
|   |-- engineering.md
|   `-- testing.md
```

Create only the project-specific files that are useful for the current
project. Missing project documents are not a reason to load broader universal
context; use `.cursor/policy/context-map.md` to decide what is actually
needed.

Project-specific execution state should normally be stored under:

```text
planning/
|-- current.md
|-- milestones/
`-- waves/
```

## Context Rule

Use the smallest sufficient working set.

Preferred flow:

```text
TASK
  -> CONTEXT MAP
  -> EXECUTION MAP
  -> WORKFLOW OR LIGHTWEIGHT MODE
  -> DELEGATION CONTRACT
  -> AGENT
  -> SKILL
  -> RELEVANT PROJECT DOCS
  -> RELEVANT CODE
```

Do not read all documentation or source code unless the task genuinely requires
it.

## Source of Truth

Use repository documentation as the source of truth.

Project-specific documentation takes precedence over universal framework files.

If authoritative project documents conflict, report the conflict instead of
silently choosing one.

## Default Entry Flow

When starting a task:

1. Read this file.
2. Consult `.cursor/policy/context-map.md`.
3. Consult `.cursor/policy/execution-map.md` when routing or delegating work.
4. Decide whether lightweight execution is sufficient.
5. If not lightweight, select the relevant workflow.
6. Select the relevant agent, skill, and policy set from the execution map.
7. Load only relevant project documentation and code.
8. Execute according to the selected mode, role, and skill.

For detailed rules, use the referenced universal and project-specific
documents.
