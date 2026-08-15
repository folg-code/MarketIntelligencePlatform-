# Project Template

Reusable AI-assisted engineering template for new projects.

This repository separates:

- Cursor-native AI engineering framework in `.cursor/` (`agents/`, `skills/`,
  `workflows/`, `policy/`),
- durable project knowledge in `docs/`,
- current execution state in `planning/`.

## Start Here

Agents should begin with:

1. `AGENTS.md`
2. `.cursor/policy/context-map.md`

The default rule is lightweight execution for small, local, reversible work.
Use full workflows only when risk or governed decisions require them.

## Main Structure

```text
AGENTS.md
.cursor/
  agents/
  skills/
  workflows/
  policy/
docs/
  product/
  architecture/
planning/
  current.md
  milestones/
  waves/
```

## Using This Template

For a new project:

1. Fill in `docs/product/PRD.md` only as product truth becomes known.
2. Fill in architecture docs only when architecture decisions become durable.
3. Keep `planning/current.md` short and current.
4. Prefer vertical tracer-bullet tasks for faster integration feedback.
5. Avoid updating documentation after every small code change unless durable
   truth or material execution state changed.
