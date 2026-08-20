# Memory and Context Review: Synthesis and Implementation Audit

## Decision question

Should bounded phase memory become part of the default Agentic Engineering workflow, and did the completed campaign test the mechanisms claimed by Prometheus, ContextBench, or PMCoder?

## What the papers jointly show

1. **Memory can matter when an agent loses useful evidence.** Prometheus reports less repeated retrieval and a better result on a 50-task memory ablation. PMCoder provides stronger three-run evidence that coupled planning and memory improve issue resolution.
2. **More context can be worse.** ContextBench shows high recall with low precision, repeated inspection, and useful evidence being dropped before patching. A simple scaffold often has better retrieval F1 than complex ones.
3. **The retrieval policy and control loop are separate mechanisms.** Prometheus caches query-relevant repository code. PMCoder couples phase-aware episodic recall to stuck detection and replanning. Our module filters a prewritten project ledger by task, phase, supersession, and capacity.
4. **Final completion is necessary but not sufficient for studying memory.** We also need retrieval precision, obsolete-item exposure, redundancy, and whether relevant evidence survives until the edit and verification steps.

## Implementation alignment audit

| Project surface | Evidence-aligned part | Material deviation | Decision |
| --- | --- | --- | --- |
| `phase_memory.py` | Bounded task/phase retrieval, provenance, supersession, deterministic eviction, no side effects | Manual structured entries; no semantic or graph retrieval, live phase detection, trajectory capture, or plan feedback | Keep as a safe **project-memory adaptation**, not a paper reproduction |
| `memory_campaign.py` | Matched control/treatment workflows, repeated seeds, pressure cases, immutable evidence, promotion rule | Checks declared memory behavior, not ContextBench retrieval quality or PMCoder coupling | Keep for readiness and safety; extend metrics before efficacy claims |
| 18-cell live campaign | Same task matrix, independent evaluation, cost/time, preserved negative result | Three small ceiling tasks; seed labels are repeated agent runs, not different task contents; no plan-only/memory-only ablation | Valid evidence that this treatment did not improve completion in this setting |
| Canonical-rereading control | Credible simple baseline, consistent with ContextBench's warning about over-engineering | Small task scale may make rereading artificially easy | Retain; add simple repository search on larger tasks |
| Watchdog and dependency planner | Some stuck and plan signals exist as separate experimental modules | They are not bidirectionally connected to phase memory | Do not claim PMCoder-style coupling |

## Corrections and clarified claims

- The current mechanism was **informed by** memory research but is not a reproduction of Prometheus or PMCoder.
- The campaign's `9/9` versus `9/9` result establishes safe deterministic filtering on its fixtures, not useful memory retrieval in general.
- A `6.93%` time reduction is secondary descriptive evidence because the predeclared rule required completion improvement and both arms were at the ceiling. Treatment also cost `5.51%` more overall.
- Prometheus's `70%` versus `56%` memory result is a one-run 50-task ablation, not universal proof. Its multiple-patch ablation is internally reported as both `68.8%` and `69.2%`.
- ContextBench's shared evaluation challenges Prometheus's broad retrieval claim: Prometheus attains high recall and the best Pass@1, but a simple mini-SWE-agent has substantially better retrieval F1.
- PMCoder supplies the closest evidence for phase-aware memory, but its key intervention is bidirectional plan-memory coupling plus execution grounding, which our campaign did not implement.

## Transfer decisions

- **Keep optional:** deterministic bounded project memory for cases with explicit stale-decision or context-pressure risk.
- **Add before another live run:** trajectory-derived retrieval events and metrics for relevant evidence found, irrelevant or obsolete evidence shown, repeated reads, and evidence retained at patch time.
- **Prototype separately:** automatic episodic capture and phase-conditioned retrieval. Do not mix it immediately with automatic replanning or recovery.
- **Ablate in order:** simple canonical search, retrieval only, planner only, plan+memory, then execution grounding. This avoids attributing a full-system gain to memory.
- **Defer:** Prometheus-scale knowledge graphs until repository navigation is measured as a recurring bottleneck.

## Predeclared next evaluation

- **Tasks:** issue-resolution or repository-evolution tasks where the control is below 100%, with longer trajectories, several repositories, stale evidence, and relevant evidence separated across files.
- **Arms:** canonical rereading/search; phase-conditioned episodic retrieval; phase planner only; coupled planner+memory. Execution grounding should be a later factor or held equal.
- **Controls:** same model, tools, repository, evaluator, step/context/cost budget, and matched seeds.
- **Repetitions:** at least three runs per task and arm; retain per-instance paired results.
- **Primary outcome:** verified completion without protected regression or false completion.
- **Mechanism outcomes:** evidence precision/recall, obsolete-evidence exposure, repeated retrieval, evidence drop, failed-action recurrence, context exhaustion, cost, and time.
- **Promotion rule:** require a predeclared verified-completion or robustness gain on memory-pressure tasks, no low-pressure loss, no safety regression, and mechanism evidence showing the gain is plausibly memory-related.

The completed 18-cell campaign should not be rerun unchanged. Its ceiling makes another identical matrix low-value. The next step is to implement the measurement layer and construct harder tasks before spending on agents again.

## Gate status

The memory-and-context retrospective research gate is **complete** for Prometheus, ContextBench, and PMCoder. The implementation remains optional and experimental; completing the review means its evidence boundary is now understood, not that the method has earned default promotion.
