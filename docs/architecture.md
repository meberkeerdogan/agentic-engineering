# Architecture Notes

This document captures the starting architecture direction. It is expected to change as the project moves from concept to prototypes. No single package boundary or solution form below defines the scope of the project.

## Architecture Principle

Treat agentic software engineering as a system. Instructions, skills, playbooks, workflows, harnesses, evaluators, memory, tools, benchmarks, and human controls are independently useful layers that can be combined or evaluated separately.

## Core Model

```text
Playbook
|-- metadata
|-- purpose
|-- inputs
|-- workflow
|-- skills
|-- tools
|-- verification
|-- outputs

Workflow
|-- metadata
|-- steps
|-- checkpoints
|-- evaluators
|-- handoff
```

### Playbook

A playbook is a reusable guide for an agent task or family of tasks. It can be inspected, versioned, adapted, and improved over time.

### Workflow

A workflow is the executable or repeatable process inside a playbook. It may combine steps, skills, tools, verification rules, and handoff outputs.

### Skill

A skill is a reusable instruction set or capability that an agent can apply inside one or more playbooks.

### Step

A step is one action inside a workflow. Examples:

- gather repository context
- draft an implementation plan
- edit files
- run tests
- review a diff
- summarize the handoff

### Checkpoint

A checkpoint pauses or verifies the workflow before continuing. It may require a human decision, automated evaluation, or both.

### Evaluator

An evaluator decides whether a result is acceptable. Evaluators can be deterministic checks, such as tests, or structured reviews, such as a rubric.

### Context

Context is the information a playbook depends on. It can include repository files, prompts, tool output, issue data, prior decisions, and constraints.

### Handoff

A handoff is the structured output of a workflow. It should let a person or another agent continue without reconstructing the whole run.

## Candidate Package Boundaries

- **Evaluation and benchmarks**: Define external success criteria, fixtures, metrics, and reproducible comparisons.
- **Harness and state**: Manage execution state, context boundaries, evidence, retries, recovery, and audit history.
- **Playbook format**: Defines portable playbook files and validation rules.
- **Skill format**: Defines reusable skill files and metadata.
- **Workflow schema**: Defines reusable workflow structure and state transitions.
- **Runner**: Executes or simulates workflow steps and checkpoint state.
- **Adapters**: Integrate with coding-agent tools, shells, CI, or GitHub.
- **Evaluators**: Provide reusable checks and review rubrics.
- **Research and experiments**: Reproduce relevant findings and test new interventions against baselines.
- **Examples**: Demonstrate practical playbooks and skills for common workflows.

## First Implementation Questions

- Should playbook files be written in YAML, JSON, Markdown, code, or a hybrid?
- Should skills share the same schema system as playbooks?
- Should the runner be a CLI, library, or both?
- Which state should be persisted between steps?
- How should human approval be represented?
- What is the minimum useful evaluator interface?
- Which agent-engineering failures deserve intervention first, and at which layer?
- How will each proposed improvement be measured against a baseline?

## Decision Records

Architecture decisions should be recorded in `docs/adr/` using the template in [docs/adr/0001-record-architecture-decisions.md](adr/0001-record-architecture-decisions.md).
