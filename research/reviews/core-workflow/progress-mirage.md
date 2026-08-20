# Paper Dossier: Progress Mirage

## Identity and review scope

- Local PDF: [`2607.25152-progress-mirage.pdf`](../../papers/2607.25152-progress-mirage.pdf)
- Manifest SHA-256: `0f4e38a6a796c069f921412877a71e9cee67a38959505d0e943e8bf35d779ed0`
- Version or date: 23-page preliminary draft, reviewed 2026-08-20
- Workflow section: core verified workflow and testing/evidence
- Review question: when is an agent or transcript-only judge insufficient to decide progress, and which parts of the proposed external-verification architecture are experimentally supported?
- Relevant evidence: Sections 3-7; Tables 1-3; Figures 1-4; pilot scope, measurement amendments, threats, and reproducibility discussion

## Plain-English contribution

The paper tests a simple distinction: a judge can read the agent's story about its work, or it can independently measure the real outcome. On a synthetic signup task where success is hidden outside the transcript, self-report and even a stronger transcript-only judge confuse plausible edits with real improvement. On a bounded task whose requirements are visible in the artifact, the stronger judge succeeds.

The paper therefore supports matching evaluator access to where truth lives. It does not prove that every evaluator must be another AI or a separate service, and most of its wider operational workflow is presented as unvalidated design advice.

## Exact claims and evidence

- **Self-report divergence (direct result):** one fixed frontier agent claimed improvement in all `54 / 54` open-task cycles, while `56%` had oracle delta at or below zero. Section 4.2.
- **Self-verdict becomes accept-all (direct result):** across three repetitions of six cycles, it accepts all cycles, has mirage `0.56`, and erodes mean deployed conversion from peak `95.0` to final `76.7`, a `19%` retreat. Table 1 and Section 4.5.
- **A stronger in-band judge does not close the hidden-signal gap (direct result):** it accepts `40%` of regression candidates, accepts cycles with a `44%` mirage rate, and rejects `37.5%` of positive-delta candidates. Section 4.3. The errors are bidirectional, not simply lenient grading.
- **Boundary falsification (direct result):** on B1, a structural five-requirement artifact task, the same stronger judge has mirage `0.00` and perfect discrimination; self-verdict remains `0.50`. Table 2 and Section 4.4.
- **Out-of-band zero mirage is structural, not an empirical effect (definition):** it accepts only positive oracle deltas, so its mirage and monotonic deployed trajectory are zero by construction. The empirical comparison concerns which bad changes in-band gates accept and which good changes they reject. Sections 3.15 and 4.2.
- **Gate versus numeric feedback (small ablation):** sign-only feedback reaches mean final `110.0` versus `113.0` with full oracle numbers over three repetitions each. The authors interpret the gate as load-bearing but explicitly do not claim the information effect is absent. Table 3 and Section 4.6.

## Method

- Task T1 asks an agent to edit a signup funnel to maximize conversions. A synthetic user simulator deterministically scores CTA presence, payload size, funnel steps, and copy length over a fixed cohort.
- The oracle is in another container and network. The agent can write only the shared artifact; the oracle reads it read-only. Each run proves the host can reach a canary while the agent cannot, and each cycle scans agent artifacts for that canary.
- The agent, tools, task, and six-cycle budget are fixed. Only the gate's information channel changes.
- `in-band-self` accepts an edit plus the agent's rationale. `in-band-judge` sees the full files, diff, summary, and verdict history under a critical prompt, but not the oracle. `out-of-band` accepts only a positive oracle delta and rolls rejected candidates back.
- An independent monitor records oracle trajectories for all arms. Dependent variables include mirage rate, conditional acceptance, false rejection, final deployed outcome, first positive outcome, and wasted cycles.
- The pilot contains T1 and boundary task B1, three repetitions per evaluator arm, six cycles per repetition, one fixed agent, and one stronger judge. A three-repetition sign-only variant is additional.
- The hypotheses were recorded before measurement, but the required commit-hash freeze was not completed. Definitions and mid-run apparatus changes are disclosed, so the authors correctly call this exploratory under a pre-freeze draft rather than fully preregistered confirmatory evidence.

## Ablations and failure evidence

- B1 is a falsification control showing that competent in-band evaluation can work when the success signal is visible.
- Sign-only feedback partially separates gating from information content, but only at three repetitions.
- Time to first positive result is one cycle for every run and does not distinguish arms.
- Candidate wasted-cycle rate is `0.56` for all main arms; the treatment filters bad candidates rather than proving better candidate generation.
- The oracle rewards removing email verification because it counts conversions only. The stronger judge's rejection is sensible under a broader value definition. This demonstrates that an external metric can itself be the wrong reward.
- Append-only state, file handoff, frame-adversarial review, and self-healing scheduling come from one field observation and were not individually tested by the controlled pilot.

## Limitations and transfer risks

- One synthetic task family, one boundary task, one agent model, one judge model, six cycles, and three repetitions provide evidence of a mechanism, not a stable effect size.
- The oracle is immediate, noiseless, deterministic, and only four-dimensional. Real metrics are delayed, noisy, gameable, and value-incomplete.
- Positive-only acceptance forbids temporary regressions and neutral maintenance. It can block refactoring, exploration, and valley-crossing work.
- The full-feedback treatment changes both gating and information. Sign-only reduces this confound but remains underpowered.
- Agentic Engineering's deterministic tests and artifact checks are already external to executor self-report for bounded coding tasks. They do not require a separate AI service. True product or user outcomes would require a domain-specific world-state evaluator.

## Project transfer decision

- **Adopt:** do not accept executor self-report as completion. Surface: evidence contracts, experiment metrics, and state transitions.
- **Adapt:** use the cheapest authoritative evaluator that can see the success signal: deterministic tests for artifact-visible claims; independently queried world state for external outcomes.
- **Reproduce, narrowly:** retain the existing deterministic claim-versus-audit fixture as proof of the structural possibility only. It does not reproduce rates, judge comparisons, or a live loop.
- **Defer:** positive-delta-only deployment gates for noisy real metrics. Required work: quality-adjusted plural metrics, uncertainty intervals, and an explicit temporary-regression policy.
- **Defer:** frame-adversarial review and self-healing scheduling as efficacy mechanisms because the paper did not isolate them.

## Open questions

- How should an evaluator combine product outcome, quality, safety, and long-term value?
- Which coding tasks have truth entirely visible in artifacts, and which require external systems?
- How should gates handle delayed feedback and intentionally temporary regressions?
- Can a stronger result be reproduced across multiple models, realistic tasks, and more repetitions?
