# Changelog

All notable changes to Agentic Engineering will be documented in this file.

This project follows the spirit of [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and intends to use semantic versioning once releases begin.

## [Unreleased]

### Added

- Initial open-source repository scaffold.
- Umbrella structure for playbooks, workflows, skills, schemas, and runners.
- Project onboarding playbook and `create-agents-md` skill.
- Project preference schema, example, and `AGENTS.md` template.
- Broadened the project identity beyond loops, playbooks, workflows, and skills to general agentic software-engineering improvement.
- Research library containing nine primary papers on long-horizon agent reliability, integrity metadata, source provenance, and a critical research-to-design review.
- Expanded the research corpus to twenty-seven papers and documented the complete evidence-first implementation plan, paper adoption decisions, and delivery order.
- Split implementation into nine promotion-gated modules and completed M01 with portable core schemas, examples, and automated validation tests.
- Added the M02 active-spec compiler with explicit revision operations, preserved supersession lineage, deterministic behavior fingerprints, a CLI, and contract-equivalence tests.
- Added the M03 single-pass baseline with command, artifact, structured-rubric, and world-state evaluators, deterministic evidence reports, protected-regression detection, and a golden fixture.
- Added the M04 single-writer verified-state store with hash-chained events, dependency-aware state reduction, strict transitions, report-fingerprint validation, and evidence-only verification.
- Added the M05 verified single-agent runner with manager-controlled transitions, fresh executors per attempt, constrained submissions, and independent single-pass auditing.
- Added the M06 experiment harness with fixed control/treatment matrices, seeded replay adapters, independent false-completion derivation, evidence requirements, paired metric summaries, and deterministic report fingerprints.
- Added the first M07 optional intervention slice: an observe-only trajectory watchdog for repeated actions, stagnation, oscillation, premature patching, and skipped validation, with no advice or blocking side effects.
- Added watchdog calibration contracts and tooling for complete signal labels, missed-failure accounting, duplicate protection, per-type precision and recall, and evidence-gated advisory experiment eligibility.
- Added the M06g representative task pack with three task categories, repeated seeds, protected baselines, known passing solutions, deterministic repository fingerprints, and a zero-model-call readiness validator.
- Added the M06h live trajectory bridge with redacted Codex JSONL provenance, durable workspace fingerprints, executor-claim and independent-audit events, schema validation, and observe-only watchdog compatibility.
- Added the M06i representative live sentinel: a two-cell multi-file control/treatment stage with one-cell invocations, explicit credit and time ceilings, and no efficacy claim.
- Completed the M06i live sentinel: both arms independently verified without regressions; treatment used more measured credits but less wall time, and both observe-only trajectories exposed a watchdog rule requiring calibration.
- Added the first real M07 watchdog calibration dataset with two privacy-safe sentinel cases, contextual false-positive labels, schema checks, and evidence that premature-patching advice remains ineligible.
- Added the M06j multi-step evolution sentinel with separate paid approval gates, one-cell invocations, explicit 0.75-credit and 450-second per-cell ceilings, and a complete offline control/treatment simulation.
- Completed the M06j live evolution sentinel: both arms independently verified without regressions, while treatment used more measured credits and wall time and both trajectories reinforced the need for contextual watchdog calibration.
- Expanded real M07 calibration to four privacy-safe live sentinel cases; all four premature-patching alerts are contextual false positives and the signal remains below the advisory support gate.
- Added M07b calibration-gated advisory reports with deterministic safe-boundary messages, fail-closed fingerprint checks, eligible-type filtering, and no intervention or blocking capability.
- Added M07c static and adaptive dependency-plan primitives with cycle rejection, evidenced runtime states, transitive failure blocking, deterministic ready-frontier prioritization, and no execution side effects.
- Added M07d bounded phase-aware memory with immutable provenance, safe supersession, deterministic capacity eviction, task/phase-aware retrieval, and no write side effects.
- Added M07e independently reviewed property-test evidence with specification-bound proposals, rejection of invented properties, read-only external results, and explicit counterexample follow-up.
- Added M08 paper reproduction tooling with hash-bound lineage, locked environment declarations, trusted local experiment execution, rubric scoring, explicit deviations, and a scoped Progress Mirage claim reproduction.
- Added M09 isolated multi-agent orchestration with dependency waves, concurrent worktrees, dependency commit delivery, declared-path enforcement, deterministic commits, topological integration, and final validation.
- Completed the nine-module implementation sequence and reconciled the roadmap, architecture, and user documentation with the remaining experiment-based promotion gates.
- Added an offline M07c evidence campaign with an isolated static/adaptive planning factor, three dependency graph shapes, three repeated seeds, deterministic readiness evidence, and no paid-run authorization.
- Added a separately approval-gated M07c safety sentinel with one diamond-graph task, one seed, two workflow arms, one cell per invocation, and explicit 0.75-credit/450-second per-cell ceilings.
- Completed and independently verified the M07c static control cell within budget, recorded its privacy-safe trajectory review, and kept the adaptive treatment separately approval-gated.
- Completed the M07c dependency-planning safety sentinel: both arms independently verified without regressions, while the adaptive treatment produced no completion gain and used more measured credits and wall time.
- Added an offline M07d phase-memory evidence campaign with an isolated canonical-rereading/bounded-retrieval factor, low-pressure, supersession, and eviction cases, three repeated seeds, deterministic evidence checks, and no paid-run authorization.
- Added a separately approval-gated M07d phase-memory safety sentinel with one eviction-pressure roadmap task, one seed, two workflow arms, one cell per invocation, and explicit 0.75-credit/450-second per-cell ceilings.
- Completed and independently verified the M07d canonical-rereading control within budget, confirmed workflow and ledger isolation, recorded a zero-signal trajectory review, and kept the bounded-memory treatment separately approval-gated.
- Completed the M07d phase-memory safety sentinel: both arms independently verified without regressions, bounded memory was cheaper and faster in the single pair, and no efficacy claim or default promotion was made.
- Added the budgeted M07d live efficacy campaign with an 18-cell resumable matrix, one cell per invocation, conservative 0.5-credit/300-second per-cell ceilings, complete offline test-double validation, and no paid-run authorization.
- Started the M07d live efficacy campaign with one independently verified median control cell, recorded its clean isolation and zero-signal trajectory, and paused with the remaining 17 cells separately approval-gated.
- Continued the M07d live efficacy campaign with a second independently verified median control cell, confirmed clean isolation and a zero-signal trajectory, and paused at 2 of 18 cells with the remaining 16 separately approval-gated.
- Completed all three low-pressure median control seeds in the M07d live efficacy campaign with independent verification, clean isolation, and zero regressions, false completions, watchdog signals, or interventions; paused at 3 of 18 cells.
- Started the M07d supersession-pressure control block with a verified `restock-report` seed, preserved a contextual watchdog false positive, and paused at 4 of 18 cells with no regressions, false completion, or intervention.
- Continued the M07d supersession-pressure control block with a second verified `restock-report` seed, a zero-signal trajectory, and no regressions, false completion, or intervention; paused at 5 of 18 cells.
- Added durable learner-oriented agent guidance and a concise project learning path covering completed topics, current experiments, exercises, and suggested next concepts.
- Added M10's optional Learning Companion contracts and runner: fresh agent instances, bounded milestone evidence, preserved failed experiments, proposal-only lessons, deterministic reports, and no engineering verification or mutation authority.
- Added a durable future-paper evidence trail and research-record policy linking product development, controlled experiments, negative findings, limitations, and reproducible artifacts.
