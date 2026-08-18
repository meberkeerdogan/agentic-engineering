# M10: Optional Learning Companion

**Status:** Offline proposal boundary implemented; live agent adapters remain separately approval-gated

## Purpose

The Learning Companion lets a separate teaching agent explain a meaningful engineering milestone without filling the main engineering agent's context. In plain English, the engineering workflow supplies a small packet of checked facts, decisions, failed experiments, and at most four files. A fresh companion turns that packet into a lesson proposal.

The technical pattern is a **proposal-only sidecar**: an optional process beside the critical engineering path. It can explain work but cannot verify completion, change engineering state, or edit the learning path directly.

```text
verified engineering milestone
        -> bounded milestone packet
        -> fresh learning companion
        -> validated lesson proposal
        -> human or main-agent review
        -> optional LEARNING_PATH.md update
```

## Boundaries

- `enabled: false` returns a deterministic skipped report without creating an agent.
- Enabled milestones receive a fresh companion instance and no conversation history.
- Every focus file must already be bound to milestone evidence, with a maximum of four.
- Selected approaches and alternatives must come from declared decisions.
- Every failed or inconclusive experiment in the packet must remain in the lesson.
- Reports have structurally empty `engineering_state_mutations` and `verification_claims` arrays.
- Learning-path changes are proposals only; applying them remains outside the companion.

These constraints keep teaching errors from becoming engineering truth.

## Interfaces

- [`learning-milestone.schema.json`](../../schemas/learning-milestone.schema.json) defines the bounded evidence packet and learner policy.
- [`learning-companion-submission.schema.json`](../../schemas/learning-companion-submission.schema.json) defines what a teaching agent may return.
- [`learning-companion-report.schema.json`](../../schemas/learning-companion-report.schema.json) binds the proposal to the exact milestone fingerprint.
- `LearningCompanionRunner` accepts a factory for any agent adapter and rejects reused companion instances.
- `render_learning_prompt` produces the bounded prompt an adapter sends to the companion.
- `build_learning_report` validates and fingerprints a captured submission.

The included CLI validates a submission without invoking a model:

```powershell
uv run python -m agentic_engineering.learning_companion `
  examples/learning-milestone.json `
  examples/learning-companion-submission.json `
  --output learning-companion-report.json
```

## Alternatives considered

- **Teach inside the main agent:** simplest, but consumes engineering context and mixes two responsibilities.
- **Summarize Git history afterward:** cheap and independent, but loses rationale, rejected alternatives, and failed attempts.
- **Persistent teaching agent:** remembers more, but can accumulate stale assumptions. The runner instead requires a fresh agent per milestone.

## Sequence protection and next gate

M10 is not connected to the active 18-cell phase-memory campaign. Its experiment definition, prompts, batch order, and private resumable state remain unchanged.

A runtime-specific companion adapter can be added later. Before default enablement, it should be compared with inline teaching for lesson accuracy, learner usefulness, context saved, cost, and time. Authenticated companion calls require their own explicit budget approval.
