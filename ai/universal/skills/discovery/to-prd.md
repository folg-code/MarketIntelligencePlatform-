# Skill: To PRD

## Purpose

Transform sufficiently clarified discovery into durable product
requirements by creating or updating the project PRD.

Preserve established product truth and apply only the changes supported
by the completed discovery.

## Use When

Use when:

-   discovery is sufficiently complete,
-   the product problem and intended outcome are understood,
-   scope boundaries are explicit enough to document,
-   product requirements need to be created or updated before
    specification or execution.

Do not use when blocking product ambiguity remains.

## Input

Use:

-   the discovery handoff produced by `grill-me`,
-   the current PRD when one exists,
-   only other product sources required to apply the change correctly.

`readiness.status` should be `READY`.

If blocking contradictions or unresolved product decisions remain,
return to discovery.

## Procedure

1.  Identify what product truth the discovery adds or changes.
2.  Load only the existing PRD context required to apply and validate
    the change.
3.  Separate established facts, decisions, assumptions, and unresolved
    items.
4.  Create or update the affected problem, outcome, scope, requirements,
    and constraints.
5.  Preserve unrelated existing product truth.
6.  Preserve non-blocking unresolved decisions explicitly.
7.  Check consistency with the rest of the PRD.
8.  Verify that no product behavior was invented.

For an initial project, create the broader PRD required to define the
planned product scope.

For later changes, update only the product truth affected by the
discovery.

## Output

Produce or update the project PRD.

At minimum, represent relevant information from:

``` yaml
problem:
users:
outcome:

scope:
  included:
  excluded:

requirements:

constraints:

decisions:

assumptions:

unresolved:
```

Use the project's established PRD structure when one exists.

The structure above defines information to preserve, not a mandatory
document format.

Do not rewrite unrelated PRD sections.

## Boundaries

Do not:

-   perform new discovery unless required input is missing,
-   invent product behavior,
-   make architecture or implementation decisions,
-   turn technical preferences into product requirements,
-   hide assumptions or unresolved decisions,
-   duplicate detailed specification owned by `to-spec`,
-   rewrite unaffected product truth.

> Convert completed discovery into durable product truth.
