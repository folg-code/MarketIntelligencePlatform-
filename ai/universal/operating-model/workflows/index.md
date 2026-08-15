# Workflow Index

Use this index before opening a full workflow file.

| Request type | Default route | Primary agent | Typical skill |
| --- | --- | --- | --- |
| Small local reversible change | `lightweight.md` | Engineer | Relevant engineering skill |
| New approved behavior | `feature.md` | Engineer | `implement-feature` |
| Reported defect | `bug.md` | Tester, then Engineer | `confirm-defect`, `fix-bug` |
| Behavior-preserving structure change | `refactor.md` | Tester, then Engineer | `establish-behavior-baseline`, `refactor-safely` |
| Boundary, contract, or dependency change | `architecture-change.md` | Architect | `architecture-assessment`, `architecture-proposal` |
| Progressive milestone execution | `milestone-development.md` | Orchestrator | `plan-wave`, `replan` |
| Integrated milestone acceptance | `milestone-validation.md` | Orchestrator, Tester | `validate-milestone-outcome` |

## Escalation Triggers

Leave lightweight mode and use the appropriate full workflow when the work may
affect:

- product behavior or acceptance criteria,
- architecture boundaries or module responsibilities,
- public or cross-module contracts,
- protected domain semantics,
- persisted data or migrations,
- external integrations,
- significant dependencies,
- milestone scope, outcome, or roadmap assumptions.

## Token Rule

Open only the selected workflow and the role or skill files needed for the
current stage.

Do not load every workflow to decide how to execute one task.
