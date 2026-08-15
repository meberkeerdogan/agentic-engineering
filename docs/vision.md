# Vision

Agentic Engineering exists to improve the systems through which AI agents perform software engineering. It is an umbrella for research-informed, measurable, and reusable improvements to agentic coding.

## Problem

Coding agents can plan, edit, test, review, and summarize work, but long-running projects expose weaknesses in planning, context management, progress measurement, recovery, verification, and continuity. Teams need ways to improve the whole system around an agent, not only the prompt or skill given to it.

Without durable engineering mechanisms, important details often live only in chat history:

- when to ask for approval
- which tests to run
- how to handle failure
- what to record before stopping
- how to hand work to another person or agent
- how to compare an agent run against expectations

## Project Scope

Agentic Engineering should support multiple kinds of solution. A problem may call for a playbook or skill, but it may instead require a deterministic evaluator, persistent state model, benchmark, context strategy, agent harness, safety policy, tool adapter, orchestration method, or another mechanism. The project should compare approaches by evidence rather than make one abstraction universal.

The project should help with five jobs:

- **Understand** recurring failure modes and opportunities in agentic software engineering.
- **Design** interventions at the appropriate layer: instructions, tools, runtime, evaluation, or process.
- **Package** useful interventions so they can be reused across agents and projects.
- **Run** agent work with inspectable state, evidence, and controls.
- **Evaluate** whether interventions improve outcomes on realistic work.

## Design Values

- **Inspectable**: A person can understand what happened and why.
- **Composable**: Small playbooks and skills can be combined into larger workflows.
- **Portable**: Definitions should not be trapped in one tool.
- **Safe**: Risky operations should be explicit and reviewable.
- **Practical**: The first useful version should help real projects quickly.
- **Evidence-driven**: Claims of improvement should be backed by reproducible evaluation.
- **Pluralistic**: Use the mechanism that fits the problem rather than forcing every solution into one format.

## Non-Goals

- Replacing coding agents.
- Treating playbooks, workflows, skills, or loops as the only valid solution.
- Hiding tool behavior behind opaque automation.
- Building a general project management suite.
- Claiming improvement based only on an agent's self-assessment.
- Optimizing for every agent environment before individual approaches demonstrate value.
