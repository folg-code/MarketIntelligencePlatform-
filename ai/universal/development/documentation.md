# Development Policy: Documentation

## Purpose

Keep project knowledge and operational state current enough that agents and
humans can work from repository truth instead of conversation history.

Documentation is part of the coordination model, not an archive of every
intermediate thought.

## Documentation Classes

Distinguish durable truth from operational state.

### Durable Truth

Examples:

- PRD and accepted product requirements,
- architecture documentation,
- ADRs,
- domain definitions,
- contracts,
- development policies,
- durable technical specifications.

Durable truth changes only when the underlying approved truth changes.

### Operational State

Examples:

- roadmap status,
- current milestone,
- current wave,
- active plan,
- blockers,
- relevant discoveries,
- deferred work,
- next actions.

Operational state is a current snapshot and may be replaced as the project
progresses.

## Ownership

Default ownership:

- product truth -> product authority / product-writing skill,
- architecture documentation and ADRs -> Architect,
- current milestone, wave, plan, blockers, and routing state -> Orchestrator,
- implementation-specific technical documentation -> Engineer when required,
- validation evidence -> Tester,
- review evidence -> Reviewer,
- repository governance policies -> Human / project governance.

Ownership may be delegated explicitly but should not become ambiguous.

## Current Project State

Maintain a compact operational entry point, such as:

```text
planning/current.md
```

It should contain only information needed to understand the active execution
state, for example:

```text
Current Milestone
Current Wave
Relevant task status
Blockers
Recent material discoveries
Current plan / next actions
Replanning triggers when relevant
```

Do not duplicate authoritative product, architecture, or specification content.
Reference it.

## Update Rules

Update documentation when project knowledge or operational state would
otherwise become materially stale.

Typical update points include:

- milestone baseline established,
- wave planned,
- material task outcome or blocker changes the plan,
- wave review completed,
- replanning changes the execution path,
- milestone becomes ready for validation,
- milestone decision changes roadmap state,
- accepted product, domain, architecture, contract, or policy truth changes.

Do not update multiple status documents after every implementation action
without a material state change.

Do not update durable documentation merely because a small implementation task
was completed.

## Plans and Replanning

Current plans represent the best known execution path, not permanent truth.

When replanning:

- replace or clearly supersede obsolete operational plans,
- preserve the reason for material replanning when useful,
- do not leave multiple competing documents appearing current,
- update downstream references when required.

Historical detail should be retained only when it provides durable decision
value.

## Context Loading

Do not load all documentation by default.

Start from the project context map and follow references to authoritative
sources only as required by the assigned responsibility.

Prefer:

```text
context map
-> current state when relevant
-> governing task/workflow
-> relevant authoritative sources
-> directly affected code/evidence
```

over loading broad repository history.

## Documentation Quality

Documentation should be:

- authoritative within its declared scope,
- concise enough to remain usable,
- explicit about unresolved or provisional information,
- free of duplicated truth when a reference is sufficient,
- updated by the role that owns the affected knowledge.

Conversation history is not a durable project source of truth.

> Keep repository truth current, minimal, and navigable.
