# Paper Dossier: SpecPath

## Identity and review scope

- Local PDF: [`2608.09799-specpath.pdf`](../../papers/2608.09799-specpath.pdf)
- Manifest SHA-256: `8b87b62876842e1ec2dcd06b951e039ed2ab7fe9d5bcf6a022100273df5e7298`
- Version or date: arXiv v1, 2026-08-10; reviewed 2026-08-20
- Workflow section: core verified workflow, active specification
- Review question: does canonical success remain reliable when equivalent final requirements arrive through different revision histories, and what intervention follows from the evidence?
- Relevant evidence: problem formulation; Tables 1-3; Figures 1-3; suite construction, experimental design, results, discussion, and threats

## Plain-English contribution

SpecPath gives an agent different requirement conversations that all mean the same final thing. The repository, tests, agent setup, and budget stay fixed. An agent may solve the direct, consolidated request but fail after seeing an equivalent history containing repetition, splitting, replacement, or cancellation.

The paper demonstrates path sensitivity and proposes an explicit requirement ledger as a future intervention. It does not test that ledger, identify the agent's internal failure mechanism, or estimate how common the problem is in normal software work.

## Exact claims and evidence

- **Stable averages hide changed identities (direct result):** direct task-macro final-contract realization (FCR) is `78.8%`; the mean across duplicate, override, cancellation, and split is `78.7%`. Figure 3 and Results.
- **Paired robustness failure (direct result):** of 210 possible five-history blocks, 127 have complete scores. Direct succeeds in 100; 35 of those fail on at least one equivalent history. Task-macro any conditional path violation (CPV) is `36.4%` with a five-task cluster-bootstrap interval of `25.6%-45.1%`.
- **Multiple operators expose violations (direct result):** duplicate, override, cancellation, and split produce 19, 8, 13, and 11 positive blocks, with task-macro CPV `18.3%`, `10.8%`, `14.1%`, and `12.2%`. Counts overlap.
- **The effect appears across all five task families (direct result):** within-family positive/eligible counts range from `4/25` to `10/22`, or `16.0%-47.4%`. The inferential unit remains the task/PR family, not 100 independent tasks.
- **Controls limit causal interpretation (direct result):** length-matched and paraphrase-direct average FCR changes are `-4.0` and `-3.1` points; both cluster-bootstrap intervals include zero. Duplicate has the largest observed CPV. The data support presentation sensitivity but not a unique stale-memory or non-monotonic-revision mechanism.
- **Timeout sensitivity (direct result):** 41 selected generation timeouts receive 2,400 seconds; all finish and 26 of 32 scored recoveries pass. Budget is therefore part of the evaluated agent configuration.

## Method

- Five curated Python task families come from public PRs in Kedro, NeMo Agent Toolkit, pytest-odoo, SBSim, and Tracecat.
- Requirements are decomposed into behavioral atoms with identity, condition, scope, polarity, and observable result. Hidden activation/deactivation/restatement traces normalize into the same final active contract.
- Seven conditions are direct, duplicate, split, override, cancellation, paraphrase-direct, and length-matched-no-revision. The five core conditions form paired blocks.
- Construction proceeds through source, contract, verifier, path, and independent-audit gates. Gold patches must pass; base and nonempty selective mutants must fail; fixed-patch signatures must be identical across histories.
- Two independent reviewers recover the active contract from visible histories without the hidden trace. Ambiguous histories are repaired and re-reviewed before the suite is frozen.
- The matrix crosses 5 tasks, 7 model deployments, 2 scaffolds, 7 conditions, and 3 repeats for 1,470 planned executions. The scaffolds are mini-swe-agent and OpenHands.
- Each execution sees the complete chronological history before editing and starts from a fresh base repository. Primary timeout is 1,200 seconds; verifier commands receive 120 seconds.
- Final-contract realization measures average success. Conditional path violation measures whether a complete block that succeeds directly fails under an equivalent core history. The task family is the cluster for inference.

## Ablations and failure evidence

- Paraphrase and length-matched controls test wording and added context. Duplicate and split show that failures are not limited to explicit overrides or cancellations.
- Post-hoc metadata regrading changes any-CPV only from `36.4%` to `38.6%`, but cannot recover 133 incomplete records.
- Doubling timeout recovers many selected failures, showing sensitivity to budget.
- Mini and OpenHands estimates overlap with unequal support, so the paper treats scaffold as a possible moderator rather than ranking one winner.
- Only 127 of 210 possible core blocks are complete. Provider, metadata, and verifier invalidity are uneven across configurations.

## Limitations and transfer risks

- Five hand-curated Python PR families are a diagnostic suite, not a population sample. The paper cannot estimate real-world prevalence.
- Finite tests establish tested behavior only, not program equivalence or internal contract state.
- Separate stochastic runs mean CPV is observed robustness, not a deterministic paired causal effect with common randomness.
- Synthetic histories provide experimental control but may differ in naturalness from real conversations.
- The paper's explicit contract ledger is a proposed intervention, not an evaluated result.
- Agentic Engineering's compiler receives explicit structured revision operations. It does not infer active atoms from natural-language conversations, so it avoids the paper's central resolution task rather than solving it. Its equivalence unit tests are small local fixtures, not a SpecPath reproduction.

## Project transfer decision

- **Adopt:** preserve stable requirement identity, explicit supersession, current status, acceptance criteria, and canonical active behavior. Surface: `active_spec.py` and its schemas.
- **Adapt:** require users or a trusted extraction step to encode revision operations explicitly; deterministic compilation then rejects ambiguity and cycles. This is safer than silently claiming natural-language resolution.
- **Reproduce later:** compare the compiler-assisted workflow with canonical rereading across direct, duplicate, split, override, and cancellation histories under fixed repo, verifier, agent, and budget.
- **Adopt for evaluation:** report direct competence and paired path robustness separately; equal aggregate completion is not proof of invariance.
- **Reject:** describing the current compiler as a reproduction or validated cure for specification-path sensitivity.

## Open questions

- Does an explicit ledger reduce CPV without lowering direct FCR or increasing cost excessively?
- Who may translate natural-language changes into trusted structured operations, and how is that translation audited?
- Which real project revision histories are sufficiently equivalent to support paired testing?
- Can paired seed or replay strategies better separate stochastic variation from history effects?
