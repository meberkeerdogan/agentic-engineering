# Vision

Agent Loops exists to make coding-agent work more reliable, legible, and reusable.

## Problem

Coding agents can plan, edit, test, review, and summarize work, but each run can feel one-off. Teams need a way to describe the process around the agent, not only the prompt or skill given to it.

Without explicit workflows, important details often live in chat history:

- when to ask for approval
- which tests to run
- how to handle failure
- what to record before stopping
- how to hand work to another person or agent
- how to compare an agent run against expectations

## Product Idea

Agent Loops should let people define agent workflows as reusable loops and skills. A loop describes the sequence of steps, the context each step needs, the checks that validate progress, and the handoff produced at the end. A skill packages focused agent behavior so it can be reused inside one loop or across many workflows.

The project should help with four jobs:

- **Design** repeatable agent workflows.
- **Package** reusable coding-agent skills.
- **Run** workflows with visible checkpoints.
- **Improve** workflows over time using structured outcomes.

## Design Values

- **Inspectable**: A person can understand what happened and why.
- **Composable**: Small loops and skills can be combined into larger workflows.
- **Portable**: Definitions should not be trapped in one tool.
- **Safe**: Risky operations should be explicit and reviewable.
- **Practical**: The first useful version should help real projects quickly.

## Non-Goals

- Replacing coding agents.
- Hiding tool behavior behind opaque automation.
- Building a full project management suite.
- Optimizing for every agent environment before the core model works.
