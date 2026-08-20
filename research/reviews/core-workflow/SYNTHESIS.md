# Core Workflow Review: Verification and Specification Subsection

## Decision question

Should Agentic Engineering keep its active-specification, evidence-based acceptance, verified-state, fresh-executor, and independent-auditor boundaries—and what claims or experiments must be narrowed after reading the primary papers in full?

The simpler baseline is a single agent that rereads canonical requirements, edits the repository, runs its own checks, and reports completion. The reviewed treatment adds explicit contract state, separates execution claims from acceptance, and uses a fresh execution/audit boundary.

## What the papers agree on

1. **Conversation is not authoritative state.** LongHorizon-Harness discards raw executor history in favor of verified task state. SpecPath shows that an append-only conversation can contain obsolete and still-active requirements at once. Progress Mirage shows that a transcript can contain a persuasive but false account of progress.
2. **Truth must be checked where it lives.** Local tests and artifacts are enough for bounded, visible specifications. External product outcomes require independent world access. A stronger transcript-only judge cannot recover a hidden signal.
3. **Pairing matters.** Average success can look unchanged while the particular runs that succeed change. Our experiments should compare matched tasks and seeds and preserve per-run evidence, not only arm averages.
4. **The harness is part of capability.** LongHorizon-Harness can materially raise completion with the same model, but its cost and benefit depend on task type and executor capability.

## Important disagreements and limits

- LongHorizon-Harness evaluates a complete multi-role intervention without isolating each component. SpecPath's contract ledger is only a proposed intervention. Progress Mirage directly validates only the out-of-band gate and rejection feedback; append-only state, file handoff, adversarial review, and scheduling are unvalidated auxiliary notes.
- Positive-only outcome gates preserve the best measured state by definition, but can reject neutral maintenance and temporary regressions. Agentic Engineering therefore protects declared baselines while allowing a contract to define which temporary changes are acceptable.
- Read-only auditing in the paper is monitored against mutation. Our evaluator schema requires `read_only: true`, but command evaluators are not OS-sandboxed and could mutate state. The current label expresses intent, not a complete technical guarantee.
- Freshness in our runner is a distinct executor object. It does not prove a fresh model process or enforce raw-context disposal in every adapter.

## Implementation alignment audit

| Project surface | Evidence-aligned part | Material deviation | Current decision |
| --- | --- | --- | --- |
| `active_spec.py` | Stable requirement IDs, explicit supersession, canonical active behavior | Structured operations are supplied; no natural-language contract resolution or SpecPath-scale evaluation | Keep as an **adaptation**; test path invariance later |
| `evaluators.py` | Completion comes from declared artifact, command, rubric, or world-state evidence | Command read-only status is declared, not technically enforced; world-state metrics can still be misspecified | Keep experimental boundary; add sandbox hardening before strong read-only claims |
| `state_store.py` | Append-only hash-chained history; only clean evaluation evidence verifies work | Best-known revision is recorded but automatic workspace rollback/preservation is outside this store | Keep; test end-to-end preservation in long tasks |
| `runner.py` | Executor cannot self-verify; fresh executor objects; separate audit request | Deterministic manager, predeclared items, one execute-audit attempt at a time, no paper-style LLM replanning | Keep as a smaller verified baseline, not a LongHorizon reproduction |
| Progress Mirage fixture | Reproduces one deterministic claim/audit disagreement with source hashes and deviations | No agent loop, evaluator-arm comparison, oracle isolation, or effect-size reproduction | Keep labeled `supported_in_fixture` only |

## Corrections made

- Correct the LongHorizon Opus subset result from `20.0 -> 34.3` to the paper's `20.6 -> 35.3` binary completion (`55.8 -> 66.9` partial).
- Do not call Progress Mirage fully preregistered: the pilot used hypotheses recorded before measurement but did not complete its prescribed commit-hash freeze and disclosed amendments.
- Do not infer that a contract ledger has been validated by SpecPath. It is a proposed design requiring a controlled follow-up.
- Do not describe out-of-band zero mirage or monotonic deployment as discovered effects; both follow from the positive-delta gate definition.

## Transfer decisions

- **Adopt:** evidence, not executor narrative, controls completion.
- **Adopt:** explicit requirement identity and supersession for structured project state.
- **Adapt:** manager-executor-auditor separation as a deterministic verified baseline.
- **Adapt:** select evaluator location by the claim: artifact-local checks for bounded code, independent world-state access for external outcomes.
- **Reproduce later:** SpecPath-style path invariance and a matched long-horizon runner comparison.
- **Defer:** LLM manager replanning, automatic repeated MEA rounds, and positive-only real-world gates.
- **Reject as defaults:** universal multi-role overhead, transcript-only acceptance for external goals, and claims that structured compilation already solves natural-language contract resolution.

## Predeclared next evaluation

The review does not authorize a new paid experiment. Before a core-workflow efficacy run, freeze:

- **Control:** canonical-rereading single agent with the same repository, task, evaluator, tools, model, and budget.
- **Treatment:** current verified runner plus structured active contract and separate evaluator.
- **Tasks:** at least one bounded issue, one contract-equivalent revision family, and one multi-step repository evolution task; avoid ceiling tasks both arms solve trivially.
- **Repetitions:** at least three matched seeds per task and arm; analyze task families as clusters when applicable.
- **Primary metrics:** verified completion, protected regressions, false completion, conditional path violation, credits, time, and human intervention.
- **Failure conditions:** evaluator mutation, missing paired evidence, environment mismatch, budget breach, or an unverified completion claim.
- **Promotion rule:** treatment must improve verified completion or conditional robustness without increasing regressions or false completion; report cost and time even if quality improves. No universal default follows from one task family.

## Gate status and remaining work

This verification/specification subsection is complete. The whole core-workflow gate remains **partial** until Agentless and Runtime-Structured Task Decomposition receive dossiers and are synthesized as simpler-baseline and decomposition evidence.
