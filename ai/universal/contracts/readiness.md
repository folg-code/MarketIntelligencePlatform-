# Contract: Definition Of Ready

## Purpose

Define when work is ready to enter execution.

## Minimum Criteria

A task is ready when:

- the goal is explicit,
- scope is bounded,
- acceptance expectations are clear enough to verify,
- directly relevant dependencies are known,
- no blocking product or domain decision remains unresolved,
- the likely workflow and owner can be selected,
- required context can be identified without loading the whole repository.

## Not Ready

A task is not ready when:

- expected behavior is ambiguous,
- the request mixes unrelated outcomes,
- required authority is unclear,
- key dependencies are unknown,
- implementation would require guessing product, domain, or architecture truth.

## Rule

Do not use readiness checks to create ceremony around obvious small work. If a
small local task is clear and low risk, use lightweight execution.
