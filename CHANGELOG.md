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
