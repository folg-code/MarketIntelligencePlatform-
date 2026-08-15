# Context Map

## Purpose

Route tasks to the smallest sufficient context.

This file exists to prevent agents from loading broad documentation, full
workflow histories, or unrelated source code by default.

## General Rule

Start narrow. Expand context only when evidence shows the current task requires
it.

Always load:

- `AGENTS.md`
- this file
- the directly relevant request, task, or issue

Then choose the smallest matching route below.

## Small Local Code Change

Use when the task is small, local, reversible, and does not affect governed
decisions.

Load:

- `ai/universal/operating-model/workflows/lightweight.md`
- `ai/universal/agents/engineer.md`
- one relevant engineering skill, if useful
- directly affected code
- directly relevant tests

Do not load by default:

- milestone workflows
- architecture-change workflow
- full PRD
- roadmap
- unrelated ADRs
- full source tree

Escalate if the work may affect product behavior, architecture boundaries,
public contracts, protected domain semantics, persisted data, external
integrations, or milestone outcomes.

## Feature

Load:

- `ai/universal/operating-model/workflows/feature.md`
- `ai/universal/agents/engineer.md`
- `ai/universal/skills/engineering/implement-feature.md`
- relevant `ai/universal/contracts/` files
- relevant specification, ticket, or PRD sections
- directly affected code and tests

Add Architect, Tester, or Reviewer context only when the workflow stage requires
that role.

## Bug

Load:

- `ai/universal/operating-model/workflows/bug.md`
- `ai/universal/agents/tester.md` when confirmation or regression evidence is required
- `ai/universal/agents/engineer.md` when implementing the fix
- relevant bug skills from `ai/universal/skills/engineering/`
- relevant contracts and expected behavior sources
- narrow failure path code and tests

Do not load unrelated product or milestone history unless the expected behavior
cannot be established.

## Refactor

Load:

- `ai/universal/operating-model/workflows/refactor.md`
- `ai/universal/agents/engineer.md`
- `ai/universal/skills/engineering/refactor-safely.md`
- `ai/universal/skills/engineering/establish-behavior-baseline.md` when behavior is not already protected
- relevant contracts, affected code, and preservation tests

Escalate if the refactor changes behavior, contracts, domain semantics, or
architecture boundaries.

## Architecture Change

Load:

- `ai/universal/operating-model/workflows/architecture-change.md`
- `ai/universal/agents/architect.md`
- `ai/universal/skills/review/architecture-assessment.md`
- `ai/universal/skills/review/architecture-proposal.md` only after assessment confirms architecture change
- relevant architecture docs, ADRs, contracts, and affected module interfaces

Do not load implementation details beyond what is needed to understand
boundaries and contracts.

## Milestone Planning Or Validation

Load:

- the relevant milestone workflow
- `ai/universal/agents/orchestrator.md`
- `ai/universal/skills/planning/plan-wave.md` or `ai/universal/skills/review/validate-milestone-outcome.md`
- `planning/current.md` when present
- milestone-relevant task outcomes and evidence

Promote only milestone-relevant task information. Do not forward full task or
agent histories.

## Documentation Updates

Update documentation only when durable truth or material operational state
changes.

Durable truth includes product requirements, architecture decisions, domain
definitions, public contracts, development policies, and accepted technical
specifications.

Do not update documentation merely because a small implementation task was
completed.
