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
