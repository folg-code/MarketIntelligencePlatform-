# Contract: Execution Map

## Purpose

Define the authoritative mapping between workflows, stages, agents, skills, and
policies.

The Orchestrator owns this map for routing, planning, supervision, and
delegation. Specialist agents own execution quality only inside the stage
delegated to them.

## Orchestrator Rule

Before delegating non-lightweight work, the Orchestrator must:

1. classify the request,
2. select the workflow,
3. identify the current stage,
4. load only the agent, skill, policy, project-doc, code, and test context
   required for that stage,
5. delegate to the mapped owner,
6. verify the required handoff before moving to the next stage.

If the required workflow, stage owner, skill, or policy is missing, unclear, or
not mapped, escalate to Human/product authority. Do not invent a workflow,
substitute an unrelated skill, waive a policy, or continue by best guess.

## Authority Model

```yaml
orchestrator:
  may:
    - classify work
    - select mapped workflow and stage
    - select mapped stage owner, skill, and policy set
    - delegate with minimum sufficient context
    - integrate reports
    - plan next steps
    - replan within approved scope and authority
  must_not_without_human:
    - waive a required policy
    - skip a required workflow stage
    - substitute an unmapped or unrelated skill
    - approve product, protected domain, roadmap, or scope changes
    - approve architecture changes outside delegated authority
    - allow execution when the required workflow, owner, skill, or policy is missing

specialist_agents:
  may:
    - execute only the delegated workflow stage
    - use only the assigned skill and required policies
    - make local decisions explicitly allowed by the delegated skill and policies
    - report blockers, missing context, and required deviations
  must_not:
    - change workflow or stage
    - ignore assigned policies
    - use unassigned skills as substitutes
    - expand scope
    - approve deviations
    - proceed when delegated workflow, skill, policy, or authority is unclear
```

## Delegation Contract

Every non-lightweight delegation must include:

```yaml
delegation:
  workflow:
  stage:
  owner:
  required_skill:
  required_policies:
  allowed_decisions:
  must_escalate:
  expected_handoff:
```

The receiving specialist must treat this delegation as binding. If the
delegation is incomplete, contradictory, or impossible to satisfy, the
specialist reports the issue to the Orchestrator instead of improvising.

## Agent Responsibility Index

```yaml
orchestrator:
  primary_for: [routing, delegation, stage gates, progress integration, replanning]

engineer:
  primary_for: [implementation stages]

tester:
  primary_for: [defect confirmation, baselines, validation stages]

architect:
  primary_for: [architecture assessment, proposal, decision, architecture support]

reviewer:
  primary_for: [review stages]
```

Stage-specific ownership is authoritative only in the Workflow Stage Map below.

## Workflow Stage Map

### lightweight

```yaml
workflow: .cursor/workflows/lightweight.md
owner: engineer
skills:
  optional:
    - .cursor/skills/engineering/implement-feature.md
    - .cursor/skills/engineering/fix-bug.md
    - .cursor/skills/engineering/refactor-safely.md
policies:
  always:
    - .cursor/policy/context-map.md
    - .cursor/policy/engineering.md
    - .cursor/policy/reports.md
    - .cursor/policy/done.md
    - .cursor/policy/contribution-policy.md
```

### work-definition

```yaml
workflow: .cursor/workflows/work-definition.md
stages:
  READY:
    owner: orchestrator
    policies: [readiness, workflow-rules, context-map]
  DISCOVERY:
    owner: orchestrator
    skills: [grill-me]
    policies: [readiness, reports, blockers]
  PRODUCT_REQUIREMENTS:
    owner: orchestrator
    support_owner: Human/product authority
    skills: [to-prd]
    policies: [documentation, evidence, reports]
  TECH_SPEC:
    owner: orchestrator
    support_owner: architect when architecture impact exists, otherwise engineer
    skills: [to-spec]
    policies: [engineering, testing, evidence, reports]
  TICKETING:
    owner: orchestrator
    skills: [to-ticket]
    policies: [readiness, task-packet, reports, blockers]
  READY_FOR_EXECUTION:
    owner: orchestrator
    policies: [execution-map, readiness, task-packet]
```

### feature

```yaml
workflow: .cursor/workflows/feature.md
stages:
  READY:
    owner: orchestrator
    policies: [readiness, workflow-rules, task-packet]
  PREPARATION:
    owner: orchestrator
    policies: [context-map, task-packet, reports]
  ARCHITECTURE_GATE:
    owner: orchestrator
    support_owner: architect
    skills: [architecture-assessment when impact is UNKNOWN/CROSS_MODULE/ARCHITECTURAL]
    policies: [workflow-rules, engineering, evidence]
  TESTING_GATE:
    owner: orchestrator
    support_owner: tester
    policies: [testing, evidence]
  IMPLEMENTATION:
    owner: engineer
    skills: [implement-feature]
    policies: [engineering, testing, reports, done, contribution-policy]
  VALIDATION:
    owner: tester
    skills: [validate-change]
    policies: [testing, evidence, reports]
  REVIEW:
    owner: reviewer
    skills: [code-review]
    policies: [reports, engineering, testing, evidence, contribution-policy]
  DOCUMENTATION_GATE:
    owner: orchestrator
    policies: [documentation, done]
  DONE:
    owner: orchestrator
    policies: [done, reports, contribution-policy]
```

### bug

```yaml
workflow: .cursor/workflows/bug.md
stages:
  READY:
    owner: orchestrator
    policies: [readiness, workflow-rules, task-packet]
  PREPARATION:
    owner: orchestrator
    policies: [context-map, task-packet, reports]
  DEFECT_CONFIRMATION:
    owner: tester
    skills: [confirm-defect]
    policies: [testing, evidence, reports]
  ARCHITECTURE_GATE:
    owner: orchestrator
    support_owner: architect
    skills: [architecture-assessment when impact is UNKNOWN/CROSS_MODULE/ARCHITECTURAL]
    policies: [workflow-rules, engineering, evidence]
  REGRESSION_TEST_GATE:
    owner: tester
    skills: [establish-regression-test]
    policies: [testing, evidence, reports]
  IMPLEMENTATION:
    owner: engineer
    skills: [fix-bug]
    policies: [engineering, testing, reports, done, contribution-policy]
  VALIDATION:
    owner: tester
    skills: [validate-change]
    policies: [testing, evidence, reports]
  REVIEW:
    owner: reviewer
    skills: [code-review]
    policies: [reports, engineering, testing, evidence, contribution-policy]
  DOCUMENTATION_GATE:
    owner: orchestrator
    policies: [documentation, done]
  DONE:
    owner: orchestrator
    policies: [done, reports, contribution-policy]
```

### refactor

```yaml
workflow: .cursor/workflows/refactor.md
stages:
  READY:
    owner: orchestrator
    policies: [readiness, workflow-rules, task-packet]
  PREPARATION:
    owner: orchestrator
    policies: [context-map, task-packet, reports]
  ARCHITECTURE_GATE:
    owner: orchestrator
    support_owner: architect
    skills: [architecture-assessment when impact is UNKNOWN/CROSS_MODULE/ARCHITECTURAL]
    policies: [workflow-rules, engineering, evidence]
  BEHAVIOR_BASELINE_GATE:
    owner: tester
    skills: [establish-behavior-baseline]
    policies: [testing, evidence, reports]
  IMPLEMENTATION:
    owner: engineer
    skills: [refactor-safely]
    policies: [engineering, testing, reports, done, contribution-policy]
  VALIDATION:
    owner: tester
    skills: [validate-change]
    policies: [testing, evidence, reports]
  REVIEW:
    owner: reviewer
    skills: [code-review]
    policies: [reports, engineering, testing, evidence, contribution-policy]
  DOCUMENTATION_GATE:
    owner: orchestrator
    policies: [documentation, done]
  DONE:
    owner: orchestrator
    policies: [done, reports, contribution-policy]
```

### architecture-change

```yaml
workflow: .cursor/workflows/architecture-change.md
stages:
  READY:
    owner: orchestrator
    policies: [readiness, workflow-rules, task-packet]
  PREPARATION:
    owner: orchestrator
    policies: [context-map, task-packet, reports]
  ARCHITECTURE_ASSESSMENT:
    owner: architect
    skills: [architecture-assessment]
    policies: [workflow-rules, evidence, reports]
  ARCHITECTURE_PROPOSAL:
    owner: architect
    skills: [architecture-proposal]
    policies: [workflow-rules, documentation, reports]
  APPROVAL_GATE:
    owner: orchestrator
    policies: [workflow-rules, blockers, evidence]
  ARCHITECTURE_DECISION:
    owner: architect
    skills: [architecture-proposal]
    policies: [documentation, evidence, reports]
  DOCUMENTATION:
    owner: architect
    policies: [documentation, done]
  IMPLEMENTATION_DERIVATION:
    owner: orchestrator
    policies: [task-packet, reports, workflow-rules]
  DONE:
    owner: orchestrator
    policies: [done, reports]
```

### milestone-development

```yaml
workflow: .cursor/workflows/milestone-development.md
stages:
  READY:
    owner: orchestrator
    policies: [readiness, workflow-rules]
  MILESTONE_BASELINE:
    owner: orchestrator
    policies: [context-map, evidence, reports]
  WAVE_PLANNING:
    owner: orchestrator
    skills: [plan-wave]
    policies: [task-packet, workflow-rules, reports]
  EXECUTION_DISPATCH:
    owner: orchestrator
    policies: [execution-map, context-map, task-packet]
  PROGRESS_INTEGRATION:
    owner: orchestrator
    policies: [reports, evidence, blockers]
  WAVE_REVIEW:
    owner: orchestrator
    policies: [reports, evidence, done]
  MILESTONE_READINESS_GATE:
    owner: orchestrator
    skills: [replan when REPLAN is selected]
    policies: [readiness, done, blockers]
```

### milestone-validation

```yaml
workflow: .cursor/workflows/milestone-validation.md
stages:
  READY:
    owner: orchestrator
    policies: [readiness, workflow-rules]
  VALIDATION_BASELINE:
    owner: orchestrator
    policies: [context-map, evidence, reports]
  EVIDENCE_ASSESSMENT:
    owner: orchestrator
    policies: [evidence, reports, blockers]
  MILESTONE_VALIDATION:
    owner: tester
    skills: [validate-milestone-outcome]
    policies: [testing, evidence, reports]
  MILESTONE_REVIEW:
    owner: reviewer
    skills: [code-review]
    policies: [reports, evidence, engineering]
  HUMAN_QA_GATE:
    owner: orchestrator
    policies: [evidence, blockers, reports]
  MILESTONE_DECISION:
    owner: orchestrator
    policies: [done, evidence, reports]
```

## Skill Path Map

```yaml
architecture-assessment: .cursor/skills/review/architecture-assessment.md
architecture-proposal: .cursor/skills/review/architecture-proposal.md
code-review: .cursor/skills/review/code-review.md
confirm-defect: .cursor/skills/engineering/confirm-defect.md
establish-behavior-baseline: .cursor/skills/engineering/establish-behavior-baseline.md
establish-regression-test: .cursor/skills/engineering/establish-regression-test.md
fix-bug: .cursor/skills/engineering/fix-bug.md
grill-me: .cursor/skills/discovery/grill-me.md
implement-feature: .cursor/skills/engineering/implement-feature.md
plan-wave: .cursor/skills/planning/plan-wave.md
refactor-safely: .cursor/skills/engineering/refactor-safely.md
replan: .cursor/skills/planning/replan.md
to-prd: .cursor/skills/discovery/to-prd.md
to-spec: .cursor/skills/planning/to-spec.md
to-ticket: .cursor/skills/planning/to-ticket.md
validate-change: .cursor/skills/engineering/validate-change.md
validate-milestone-outcome: .cursor/skills/review/validate-milestone-outcome.md
```

## Policy Path Map

```yaml
blockers: .cursor/policy/blockers.md
context-map: .cursor/policy/context-map.md
contribution-policy: .cursor/policy/contribution-policy.md
documentation: .cursor/policy/documentation.md
done: .cursor/policy/done.md
engineering: .cursor/policy/engineering.md
evidence: .cursor/policy/evidence.md
execution-map: .cursor/policy/execution-map.md
operating-principles: .cursor/policy/operating-principles.md
readiness: .cursor/policy/readiness.md
reports: .cursor/policy/reports.md
task-packet: .cursor/policy/task-packet.md
testing: .cursor/policy/testing.md
workflow-rules: .cursor/policy/workflow-rules.md
```

## Policy Enforcement Owners

```yaml
workflow-rules:
  primary: orchestrator
  enforced_by: all stage owners
execution-map:
  primary: orchestrator
  enforced_by: orchestrator
context-map:
  primary: orchestrator
  enforced_by: all agents
task-packet:
  primary: orchestrator
  enforced_by: receiving agent
reports:
  primary: stage owner
  enforced_by: orchestrator
readiness:
  primary: orchestrator
  enforced_by: orchestrator
done:
  primary: orchestrator
  enforced_by: reviewer when review is required
engineering:
  primary: engineer
  enforced_by: reviewer
testing:
  primary: tester
  enforced_by: reviewer and orchestrator
evidence:
  primary: tester
  enforced_by: reviewer and orchestrator
documentation:
  primary: orchestrator
  executed_by: relevant specialist
blockers:
  primary: orchestrator
  enforced_by: all agents
contribution-policy:
  primary: orchestrator
  enforced_by: reviewer
```

## Missing Capability Escalation

Escalate to Human/product authority when:

- the selected workflow does not exist,
- the selected workflow has no mapped owner for the current stage,
- the mapped skill does not exist,
- the mapped skill is not appropriate for the actual task,
- required policy is missing,
- a stage requires a decision outside delegated authority.

The escalation must include:

```yaml
missing_or_unclear:
requested_workflow:
current_stage:
expected_owner:
expected_skill:
expected_policy:
why_it_blocks_progress:
```
