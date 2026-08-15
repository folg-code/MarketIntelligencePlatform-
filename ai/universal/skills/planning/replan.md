# Skill: Replan

## Purpose

Update an execution plan when new evidence makes the current plan invalid, inefficient, or incomplete.

Preserve approved outcome and scope unless higher authority explicitly changes them.

## Use When

Use when:

- dependencies changed,
- assumptions were invalidated,
- work decomposition or sequencing no longer makes sense,
- architecture or discovered complexity changes the execution path.

## Input

Use:

- current plan or wave,
- relevant new evidence,
- current task and dependency state,
- governing milestone scope and architecture decisions.

## Procedure

1. Identify exactly what new evidence invalidated the current plan.
2. Determine the smallest planning level affected.
3. Update sequencing, decomposition, dependencies, or routing as needed.
4. Preserve valid existing work and decisions.
5. Escalate changes affecting product behavior, milestone scope, protected domain decisions, or required architecture approval.
6. Produce the smallest revised plan sufficient to continue safely.

## Output

Produce a concise `ReplanDecision`:

```yaml
trigger:
impact_level:
changes:
preserved:
escalations:
next_step:
```

## Boundaries

Do not:

- silently change product or milestone scope,
- replace valid work without reason,
- use replanning as speculative redesign,
- perform implementation,
- hide the evidence that triggered the replan.

> Replan only what new evidence makes necessary.
