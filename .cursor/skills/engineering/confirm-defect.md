# Skill: Confirm Defect

## Purpose

Establish sufficient evidence that reported behavior is a real software defect.

Distinguish defects from configuration, data, environment, or requirement ambiguity.

## Use When

Use when a bug report requires confirmation before regression testing or fixing.

## Input

Use:

- bug report,
- expected behavior source,
- relevant code or runtime context,
- available logs, traces, tests, or production evidence.

## Procedure

1. State observed and expected behavior.
2. Reproduce the failure when practical.
3. Otherwise gather sufficient deterministic evidence from available sources.
4. Narrow the failure enough to separate it from environment, configuration, data, or requirement ambiguity.
5. Record the smallest useful failure evidence.
6. If expected behavior is unclear or the report is not a defect, stop and route accordingly.

## Output

Produce `DefectEvidence`:

```yaml
observed:
expected:
evidence:
reproduction:
scope:
confidence:
unresolved:
```

## Boundaries

Do not:

- fix the defect,
- invent expected behavior,
- broaden investigation beyond what is needed to confirm the defect,
- treat an assumption as evidence.

> Confirm the defect before optimizing the explanation.
