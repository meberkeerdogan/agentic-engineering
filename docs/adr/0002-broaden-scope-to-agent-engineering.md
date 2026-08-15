# 0002. Broaden Scope to Agent Engineering

Date: 2026-08-14

## Status

Accepted

## Context

The repository was initially framed around agent loops and later around reusable playbooks, workflows, and skills. Those mechanisms are useful, but centering them in the project identity can bias future work toward particular solution formats.

The actual goal is broader: improve the reliability, effectiveness, safety, continuity, and inspectability of AI agents performing software engineering. Different problems may require different interventions, including benchmarks, evaluators, specifications, context and memory systems, harnesses, orchestration, safety controls, adapters, playbooks, workflows, skills, or approaches not yet identified.

## Decision

Use **Agentic Engineering** as the project identity and `agentic-engineering` as the repository slug.

Treat this repository as an umbrella project for research-informed and measurably useful improvements to agentic software engineering. Do not require contributions to fit a loop, playbook, workflow, or skill abstraction.

Select solution forms based on the problem being solved. Where an intervention claims to improve agent outcomes, prefer an explicit baseline, external success criteria, and reproducible evidence.

Keep the existing directories because they contain valid starting components. Add or reorganize package boundaries when working implementations reveal clearer ownership boundaries.

## Consequences

- Future agents and contributors should begin from an agent-engineering problem, not a preferred artifact type.
- Playbooks, workflows, and skills remain supported but no longer define the project boundary.
- Harnesses, evaluators, benchmarks, memory systems, research reproductions, and other solution categories are explicitly in scope.
- The roadmap should prioritize measurable problems and experiments before prematurely standardizing formats or runtimes.
- The physical workspace folder may retain an older local name without defining the repository's product identity.
