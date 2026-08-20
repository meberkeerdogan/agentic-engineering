# Paper Dossier: LongHorizon-Harness

## Identity and review scope

- Local PDF: [`2608.01964-longhorizon-harness.pdf`](../../papers/2608.01964-longhorizon-harness.pdf)
- Manifest SHA-256: `ce534c4fd69b47086b724cdcf7af10faad54f44b025c13bd67ab6975d58f200a`
- Version or date: stored 29-page preprint, reviewed 2026-08-20
- Workflow section: core verified workflow
- Review question: does fresh, bounded execution plus independently audited external state improve long-horizon task completion enough to justify the project's manager-executor-auditor boundary?
- Relevant evidence: Sections 2-4; Tables 1-4; Figures 2-6; Appendix A experimental configuration; Tables 5-10 and case studies in Appendices B-C

## Plain-English contribution

The paper replaces one ever-growing agent conversation with repeated rounds. A manager chooses a bounded next job from verified task state, a fresh executor is the only role allowed to change the environment, and a read-only auditor checks the result. The next round keeps the compact verified state and audit reports, not the executor's raw trajectory.

The contribution is a complete harness evaluated on three benchmarks. It is not evidence that role separation solves every hard task: the method helps most when the main problem is preserving and checking state across many dependent actions.

## Exact claims and evidence

- **Matched WeaveBench gain (direct result):** on all 114 tasks, Qwen 3.7-Plus with Claude Code rises from `51.8%` to `80.7%` PassRate and from `0.702` to `0.835` mean score. Same model and executor backend are used. Table 1 and Section 3.2.
- **OSWorld gain (direct result with a tool-mode caveat):** on all 108 tasks, Qwen 3.7-Plus rises from `2.8%` to `8.3%` binary completion and `21.5%` to `35.2%` partial score. The treatment uses hybrid GUI+CLI, while the reported baseline is single-action GUI, so this is not a pure harness-only comparison. Table 2 and Appendix A.2.
- **Second-backbone OSWorld result (direct result with the same caveat):** on a 34-task subset, Claude Opus 4.7 rises from `20.6%` to `35.3%` binary and `55.8%` to `66.9%` partial score. Table 3 and Table 5. This corrects the project's earlier `20.0` to `34.3` transcription.
- **Terminal-Bench gain (direct result):** Qwen 3.7-Plus with Claude Code rises from `69.7%` to `77.2%`; the benchmark score averages three independent trials per task. Figure 3 and Appendix A.3.
- **Cost varies by setting (direct result):** total tokens are `2.3x` baseline on WeaveBench and OSWorld output tokens are `3.6x`, but Terminal-Bench uses `24%` fewer total tokens. The auditor consumes `19.4%`, `24.8%`, and `38.1%` of harness tokens; the manager consumes only `2.8%`, `2.0%`, and `8.1%`. Figure 5 and Section 3.3.
- **Benefit depends on the bottleneck (author interpretation supported by breakdowns):** large gains occur in stateful system administration and artifact-checkable work; some data-science, mathematics, model-training, and video categories regress. Figure 6 and Tables 6-10.

## Method

- The persistent state contains requirements, artifacts, facts, statuses, and references to audit evidence. Raw executor trajectories are discarded.
- The manager sees the original goal, current verified state, and accumulated audit reports, but cannot access the environment. It returns `execute`, `done`, `blocked`, or `ask` and constructs a subtask contract with acceptance criteria and boundaries.
- A new executor receives the goal, state, bounded contract, and relevant audits. It is the only modifying role and has multiple tool cycles inside one round.
- A fresh auditor receives the contract, executor report, state, and relevant audits, but not raw executor reasoning. It independently inspects the environment with read-only tools and reports completion, integrity, evidence, and gaps.
- Only a clean audit can mark a fact or requirement complete. The manager decides how to incorporate audit proposals.
- Runs allow up to 25 rounds. Executor timeout is 1,800 seconds per round; manager and auditor each receive 300 seconds. Terminal-Bench trials have a five-hour task timeout.
- The primary comparisons use Qwen 3.7-Plus; an Opus 4.7 subset checks another backbone. The same backbone normally fills all three roles, so independence is primarily contextual and permission-based, not model-based.

## Ablations and failure evidence

- There is no clean component ablation separating fresh context, explicit state, manager planning, and independent audit.
- The OSWorld comparison also changes the available interaction mode from single-action GUI to hybrid GUI+CLI.
- WeaveBench mean score falls slightly in the Desktop domain despite a higher pass rate.
- Terminal-Bench category scores regress for data science, mathematics, model training, and video processing. The paper says auditing can detect a wrong result but cannot supply missing reasoning, perception, or motor capability.
- Extra verification can hurt already-strong trajectories, and per-task token cost can become extreme. One Games task rises from `6.0M` to `97.2M` tokens.
- The paper has no dedicated limitations section. Its appendices nevertheless identify hidden thresholds, ambiguous task semantics, visual precision, and weak verifier closure as residual failure sources.

## Limitations and transfer risks

- The strongest clean harness comparison is WeaveBench. OSWorld changes both harness and tool mode.
- The benchmarks cover GUI, hybrid, and terminal execution, not months of real repository evolution.
- One preprint and a small second-backbone subset do not establish universal model or domain transfer.
- The architecture is expensive when verification and retries dominate.
- Agentic Engineering's current runner is smaller: its manager is deterministic state-transition code, work items are predeclared, and it does not perform the paper's repeated LLM replanning. Its `read_only` command flag is a contract declaration, not an operating-system-enforced sandbox. Freshness is checked at the Python object boundary, not proven as a clean process or context window.

## Project transfer decision

- **Adopt:** executor claims cannot update authoritative state; only evaluator evidence can. Surface: `state_store.py`. Gate: every verified transition remains report-bound and regression-free.
- **Adapt:** fresh executor and separate auditor roles. Surface: `runner.py`. We use deterministic work selection and deterministic evaluators first. Gate: compare against a simpler single-pass workflow on long tasks before default promotion.
- **Adapt:** durable compact state instead of raw trajectory replay. Surface: state store and later memory modules. Gate: demonstrate benefit without completion, regression, or cost harm.
- **Defer:** an LLM manager with up to 25 MEA rounds. Reason: component value and cost are not isolated. Required experiment: fixed-task comparison against deterministic work selection.
- **Reject as a universal rule:** using the harness for every task. Bounded tasks with cheap deterministic checks may not justify the overhead.

## Open questions

- How much of the gain comes from audit, fresh context, state representation, or extra attempts?
- Can read-only auditing be technically sandboxed across all evaluator types?
- Does the benefit persist on repository-evolution tasks under equal tool surfaces and equal budgets?
- What stopping rule avoids over-verification on already-correct work?
