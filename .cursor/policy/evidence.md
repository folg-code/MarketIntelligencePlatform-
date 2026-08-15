# Contract: Evidence

## Purpose

Make claims about behavior traceable and honest.

## Evidence Categories

Use these labels when reporting confidence:

- `verified`: directly checked in this task or accepted as valid existing evidence,
- `failed`: checked and did not pass,
- `inferred`: supported by code or reasoning but not directly executed,
- `assumed`: plausible but not established,
- `not_checked`: intentionally or unavoidably left unverified.

## Rules

- Do not report a check as passed unless it actually ran or was accepted as
  valid existing evidence.
- Prefer stable behavioral evidence over implementation-detail evidence.
- Reuse valid evidence instead of rerunning broad checks without reason.
- Missing evidence is not a pass.
- Keep raw evidence references compact unless details are needed to diagnose a
  failure.
