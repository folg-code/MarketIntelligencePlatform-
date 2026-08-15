# Contract: TaskPacket

## Purpose

Define the minimum context needed to delegate executable work without forwarding
full agent history.

## Minimum Shape

```yaml
task:
  id:
  type:
  goal:
scope:
  included:
  excluded:
acceptance_criteria:
context:
  required_docs:
  relevant_code:
  relevant_tests:
constraints:
dependencies:
write_scope:
evidence_required:
escalation_triggers:
unresolved:
```

Omit empty fields when the project issue format already carries the same
information clearly.

## Rules

- Include references, not copied source material, when a reference is enough.
- Include only context required by the receiving role.
- Do not use a TaskPacket to redefine requirements or architecture.
- A TaskPacket can route work; it does not approve governed decisions.
