# Development Policy: Contribution

## Purpose

Define how approved changes move through branches, commits, pull
requests, review, and merge.

Keep repository history understandable and make each contribution
traceable to its governing work.

## Branches

Use a dedicated branch for a coherent unit of work.

Prefer names that identify the work type and task, for example:

``` text
feat/123-event-extraction
fix/142-duplicate-events
refactor/156-normalization-boundary
```

Do not combine unrelated work on one branch.

## Commits

Commits should be logically scoped and reviewable.

Prefer Conventional Commit-style subjects:

``` text
feat: add narrative impact calculation
fix: handle duplicate source events
refactor: isolate evidence aggregation
test: add regression coverage for duplicate events
docs: update narrative domain model
chore: update tooling configuration
```

Rules:

-   one commit should represent one coherent change,
-   do not silently mix behavior changes with unrelated refactoring,
-   write the subject as a concise description of the change,
-   use a body only when additional rationale or context materially
    improves understanding,
-   do not claim tests or validation that were not executed.

Temporary local commits may be cleaned before merge according to the
repository merge strategy.

## Pull Requests

One PR should normally represent one coherent approved outcome or
ticket.

A PR should contain enough information to review the change without
reconstructing the agent conversation.

At minimum describe:

``` text
Goal
Scope
Changes
Validation
Architecture / Contracts impact
Documentation impact
Risks / Follow-ups
```

Reference the governing ticket, specification, architecture decision,
ADR, or other authoritative work definition when applicable.

Do not hide scope expansion or unrelated findings inside the PR.

## Review and Validation

Before merge:

-   required CI and quality gates must pass,
-   required independent validation must be complete,
-   required code review must be complete,
-   blocking findings must be resolved,
-   architecture-impacting changes must follow the approved architecture
    path,
-   required durable documentation must be current.

Non-blocking findings may become explicit follow-up work.

## Merge

Use the repository's configured merge strategy consistently.

Do not merge:

-   unresolved blocking review findings,
-   known failing required checks,
-   unapproved architecture or product changes,
-   changes whose evidence or scope is materially unclear.

`DONE` in an execution workflow does not override repository merge
requirements.

## AI-Assisted Contributions

AI-generated or AI-assisted changes follow the same standards as
human-authored changes.

Agent confidence, generated explanations, or passing local checks are
not substitutes for required evidence, review, or approval.

> Make every merged change scoped, traceable, reviewable, and supported
> by evidence.
