# Development Policy: Testing

## Purpose

Define how the project creates and evaluates evidence that required
behavior works and existing behavior remains protected.

## Principles

-   Test behavior rather than private implementation details.
-   Prefer the highest stable existing seam that provides sufficient
    confidence.
-   Use the smallest sufficient test scope.
-   Reuse valid evidence instead of rerunning checks without reason.
-   Missing evidence is not a pass.
-   Report executed checks separately from inferred, assumed, or
    unverified behavior.
-   Independent validation must remain independent when required by the
    workflow.

## Test Levels

Use the level that best matches the risk:

-   unit tests for isolated behavior and contracts,
-   integration tests for interactions between real components or
    external boundaries,
-   system/end-to-end tests for critical integrated flows when lower
    levels are insufficient.

Do not require a higher test level when a lower stable seam proves the
behavior sufficiently.

## TDD and Test-First Work

Use test-first development when required by the active workflow or
testing mode.

Typical cases include:

-   confirmed defects requiring regression protection,
-   behavior-preserving refactors requiring a baseline,
-   features where executable expectations can be defined before
    implementation.

TDD is a tool for controlling behavior and feedback, not a requirement
to test implementation details.

## Defects

Prefer an automated regression test when a confirmed defect can be
represented reliably at a stable seam.

When automation is impractical, preserve sufficient defect evidence
according to the bug workflow.

A regression test should fail for the confirmed defect and pass after
the fix.

## Refactoring

Before behavior-preserving structural work, establish sufficient
behavior baseline evidence.

The baseline should protect approved observable behavior, not freeze
accidental internal structure.

## Validation

Implementation-local checks provide fast feedback.

Authoritative validation should:

-   use fresh evidence,
-   verify relevant acceptance criteria and contracts,
-   execute required quality gates,
-   identify missing evidence explicitly,
-   rerun only the validation scope potentially affected by remediation
    unless broader evidence was invalidated.

Milestone validation evaluates the integrated milestone outcome rather
than task completion.

## Test Quality

Tests should be:

-   deterministic where reasonably possible,
-   isolated from unnecessary external state,
-   readable as behavioral expectations,
-   resistant to irrelevant implementation changes,
-   explicit about fixtures, assumptions, and required environment.

Mock only where it improves isolation without removing the behavior the
test is intended to prove.

## Evidence

Validation reports must distinguish:

-   verified,
-   failed,
-   inferred,
-   assumed,
-   not checked.

Never report a check as passed unless it was actually executed or
accepted as valid existing evidence.

> Testing exists to challenge claims about behavior, not to manufacture
> green status.
