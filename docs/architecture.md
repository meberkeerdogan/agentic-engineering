# Architecture Notes

This document captures the starting architecture direction. It is expected to change as the project moves from concept to prototype.

## Core Model

```text
Loop
|-- metadata
|-- inputs
|-- steps
|-- checkpoints
|-- evaluators
|-- outputs
```

### Loop

A loop is a named workflow that can be run, inspected, versioned, and improved.

### Step

A step is one action inside a loop. Examples:

- gather repository context
- draft an implementation plan
- edit files
- run tests
- review a diff
- summarize the handoff

### Checkpoint

A checkpoint pauses or verifies the loop before continuing. It may require a human decision, automated evaluation, or both.

### Evaluator

An evaluator decides whether a result is acceptable. Evaluators can be deterministic checks, such as tests, or structured reviews, such as a rubric.

### Context

Context is the information a loop depends on. It can include repository files, prompts, tool output, issue data, prior decisions, and constraints.

### Handoff

A handoff is the structured output of a loop. It should let a person or another agent continue without reconstructing the whole run.

## Candidate Package Boundaries

- **Loop schema**: Defines portable loop files and validation rules.
- **Runner**: Executes loop steps and handles checkpoint state.
- **Adapters**: Integrate with coding-agent tools, shells, CI, or GitHub.
- **Evaluators**: Provide reusable checks and review rubrics.
- **Examples**: Demonstrate practical loops for common workflows.

## First Implementation Questions

- Should loop files be written in YAML, JSON, Markdown, or code?
- Should the runner be a CLI, library, or both?
- Which state should be persisted between steps?
- How should human approval be represented?
- What is the minimum useful evaluator interface?

## Decision Records

Architecture decisions should be recorded in `docs/adr/` using the template in [docs/adr/0001-record-architecture-decisions.md](adr/0001-record-architecture-decisions.md).
