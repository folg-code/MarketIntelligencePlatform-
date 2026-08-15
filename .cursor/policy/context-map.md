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

Load `.cursor/policy/execution-map.md` when selecting a workflow stage,
delegating to an agent, choosing required skills, or checking which policies
must be enforced.

Then choose the smallest matching route below.

When a referenced project document is large, load only the relevant headings,
search hits, or narrow excerpts first. Load the full document only when the
task cannot be executed safely from targeted context.

## Small Local Code Change

Use when the task is small, local, reversible, and does not affect governed
decisions.

Load:

- `.cursor/workflows/lightweight.md`
- `.cursor/policy/execution-map.md` when choosing an optional skill or checking authority
- mapped owner, optional skill, and required policies from `.cursor/policy/execution-map.md`
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

## Work Definition

Use when the request is unclear, product requirements must be created or
updated, approved requirements need a technical specification, or an
authoritative work definition must become an executable task.

Load:

- `.cursor/workflows/work-definition.md`
- `.cursor/policy/execution-map.md`
- mapped owner, skill, and policies for the current work-definition stage
- only the relevant product, architecture, planning, or issue context needed
  for that stage

Do not load implementation code unless the current stage requires it to define
the work safely.

## Feature

Load:

- `.cursor/workflows/feature.md`
- `.cursor/policy/execution-map.md`
- mapped owner, skill, and policies for the current feature stage
- relevant specification, ticket, or PRD sections
- directly affected code and tests

Add Architect, Tester, or Reviewer context only when the execution map requires
that owner or support owner for the current stage.

## Bug

Load:

- `.cursor/workflows/bug.md`
- `.cursor/policy/execution-map.md`
- mapped owner, skill, and policies for the current bug stage
- relevant contracts and expected behavior sources
- narrow failure path code and tests

Do not load unrelated product or milestone history unless the expected behavior
cannot be established.

## Refactor

Load:

- `.cursor/workflows/refactor.md`
- `.cursor/policy/execution-map.md`
- mapped owner, skill, and policies for the current refactor stage
- relevant contracts, affected code, and preservation tests

Escalate if the refactor changes behavior, contracts, domain semantics, or
architecture boundaries.

## Architecture Change

Load:

- `.cursor/workflows/architecture-change.md`
- `.cursor/policy/execution-map.md`
- mapped owner, skill, and policies for the current architecture-change stage
- relevant architecture docs, ADRs, contracts, and affected module interfaces

Do not load implementation details beyond what is needed to understand
boundaries and contracts.

## Milestone Planning Or Validation

Load:

- the relevant milestone workflow
- `.cursor/policy/execution-map.md`
- mapped owner, skill, and policies for the current milestone stage
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
