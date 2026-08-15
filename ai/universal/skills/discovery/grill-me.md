# Skill: Grill Me

## Purpose

Expose missing information, hidden assumptions, contradictions, and unresolved decisions before a request is formalized.

Use the smallest set of high-value questions needed to reduce uncertainty.

## Use When

Use when:

- scope is unclear,
- multiple interpretations are plausible,
- important constraints or assumptions may be missing,
- the request is not ready for `to-prd`, `to-spec`, or `to-ticket`.

## Procedure

1. Identify the core problem, user, and desired outcome.
2. Challenge scope, exclusions, and hidden adjacent work.
3. Surface assumptions and distinguish them from project facts.
4. Probe only relevant edge cases and failure modes.
5. Identify important constraints and dependencies.
6. Classify unresolved decisions as:
   - product,
   - domain,
   - architecture,
   - technical,
   - external.
7. Decide whether the input is ready for the next artifact.

Resolve only what follows unambiguously from project sources.

## Output

Synthesize the discovery session into the handoff for the next skill.

```yaml
understood:
  - ...

decisions:
  - ...

assumptions:
  - ...

unresolved:
  - ...

contradictions:
  - ...

scope:
  included:
    - ...
  excluded:
    - ...

readiness:
  status: READY | NOT_READY
  next_step:
```

Use:

- `understood` for established facts and clarified problem context,
- `decisions` for explicit choices made during discovery,
- `assumptions` for claims not established as project facts,
- `unresolved` for decisions still requiring resolution,
- `contradictions` for conflicts that remain unresolved,
- `scope` for explicit inclusion and exclusion boundaries.

Omit empty sections.

The output is the synthesized discovery handoff. Do not require a separate synthesis step.

## Boundaries

Do not:

- invent product behavior,
- make protected domain or architecture decisions,
- expand scope,
- produce artifacts owned by another skill,
- ask questions that do not materially affect the next decision.

> Reduce uncertainty, not generate ceremony.