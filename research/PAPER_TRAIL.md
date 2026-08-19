# Future-Paper Evidence Trail

This file connects the product work to a possible general research paper. It is an index, not a replacement for the detailed reports or raw evidence.

## General research question

How can coding-agent workflow changes be tested and promoted using external verification, controlled comparisons, reproducible evidence, and explicit cost and safety limits?

The product contribution is the reusable Agentic Engineering workflow. Individual methods such as phase memory, dependency planning, watchdogs, and learning companions are case studies inside that broader workflow.

## Current findings

| Area | Current evidence | Interpretation | Focused record |
| --- | --- | --- | --- |
| External verification | Independent evaluators can reject unsupported completion claims and bind accepted results to evidence. | An agent's own completion statement is not enough. | [Progress Mirage reproduction](reproductions/progress-mirage-claim/reproduction.json) |
| Workflow comparison | Isolated control/treatment cells, repeated seeds, fixed budgets, and resumable state work with authenticated coding-agent runs. | The evaluation infrastructure is operational, not only a design. | [Live workflow pilot](reports/2026-08-16-live-codex-workflow-pilot.md) |
| Adaptive planning | The safety sentinel found no completion gain and higher measured cost and time for the adaptive treatment. | Do not promote adaptive planning from the current evidence. | [Dependency-planning sentinel](reports/2026-08-17-dependency-planning-live-sentinel.md) |
| Deterministic watchdog | Observe-only rules produced contextual false positives during valid investigation. | Useful for telemetry, but not reliable enough for default advice or control. | [Phase-memory sentinel](reports/2026-08-17-phase-memory-live-sentinel.md) |
| Bounded phase memory | All nine controls and all three low-pressure treatments verified with no regressions or false completion. Across the median block, treatment quality was equal, cost was `20.18%` higher, and time was `3.74%` lower. | Phase memory is safe but adds credit overhead on the negative-control task; value depends on the remaining supersession and eviction results. | [Median block result](reports/2026-08-19-phase-memory-campaign-cell-12.md) |
| Learning companion | A proposal-only sidecar can teach from bounded evidence without verification or mutation authority. | The boundary is implemented offline; teaching quality and context savings remain untested. | [M10](../docs/modules/10-learning-companion.md) |

Negative and inconclusive findings remain part of the contribution because they show why workflow features should pass evidence gates before becoming defaults.

## Record required for each experiment

Each focused report should preserve:

1. the research question and expected comparison;
2. the fixed protocol, task, seed, workflow arm, model, environment, and limits;
3. verified outcomes, regressions, false completion, cost, time, and intervention counts;
4. trajectory or other process evidence, including false alarms and failures;
5. evidence fingerprints and links to reproducible artifacts;
6. a plain-English interpretation, limitations, and the resulting product decision.

## Candidate paper structure

1. Problem: coding-agent improvements are often adopted from plausible demonstrations rather than controlled evidence.
2. Method: the Agentic Engineering workflow for specifications, independent verification, isolated experiments, budgets, trajectories, and promotion gates.
3. Case studies: dependency planning, deterministic watchdogs, bounded phase memory, and failed or inconclusive interventions.
4. Results: verified outcomes, reliability, cost, time, false completion, and false-alert behavior.
5. Product artifact: the reusable open-source schemas, runners, task packs, and evidence records.
6. Limitations and replication: more models, repositories, task types, and independent reproduction are required before broad claims.

## Paper-readiness gate

The general workflow can be described now, but outcome claims should wait until the active 18-cell phase-memory campaign finishes. Stronger publication evidence should also include at least one additional model or task family and an independent reproduction of the main result.
