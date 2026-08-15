# Contract: Blockers

## Purpose

Represent blockers clearly enough for routing without expanding context
unnecessarily.

## Shape

```yaml
blocker:
  summary:
  type: product | domain | architecture | technical | dependency | access | evidence | external
  blocks:
  required_decision_or_input:
  owner:
  current_safe_work:
```

## Rules

- A blocked task does not automatically block a milestone.
- Record the smallest blocker that explains why progress cannot continue.
- Continue independent approved work when it does not depend on the blocker.
- Escalate blockers to the authority that owns the missing decision or input.
