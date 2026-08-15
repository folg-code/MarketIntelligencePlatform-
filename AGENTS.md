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

Reusable AI engineering definitions are stored under:

```text
ai/universal/
```

### Operating Model

```text
ai/universal/operating-model/
|-- operating-principles.md
`-- workflows/
    |-- index.md
    |-- lightweight.md
    |-- feature.md
    |-- bug.md
    |-- refactor.md
    |-- architecture-change.md
    |-- milestone-development.md
    `-- milestone-validation.md
```

### Agents

```text
ai/universal/agents/
|-- orchestrator.md
|-- architect.md
|-- engineer.md
|-- tester.md
`-- reviewer.md
```

### Skills

```text
ai/universal/skills/
|-- discovery/
|-- planning/
|-- engineering/
`-- review/
```

### Shared Contracts

```text
ai/universal/contracts/
|-- task-packet.md
|-- reports.md
|-- readiness.md
|-- done.md
|-- evidence.md
`-- blockers.md
```

Universal files define how AI-assisted engineering is performed.

They should not contain project-specific product, domain, architecture, or
technology assumptions.

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
context; use `ai/project/context-map.md` to decide what is actually needed.

Project-specific execution state should normally be stored under:

```text
planning/
|-- current.md
|-- milestones/
`-- waves/
```

## Project AI Configuration

Project-specific AI configuration is stored under:

```text
ai/project/
|-- context-map.md
`-- overrides.md
```

`context-map.md` defines which documentation should normally be loaded for
different task types.

`overrides.md` contains explicit project-level deviations from the universal AI
framework.

## Context Rule

Use the smallest sufficient working set.

Preferred flow:

```text
TASK
  -> CONTEXT MAP
  -> WORKFLOW OR LIGHTWEIGHT MODE
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
2. Consult `ai/project/context-map.md`.
3. Decide whether lightweight execution is sufficient.
4. If not lightweight, select the relevant workflow.
5. Select the relevant agent and skill.
6. Load only relevant project documentation and code.
7. Execute according to the selected mode, role, and skill.

For detailed rules, use the referenced universal and project-specific
documents.
