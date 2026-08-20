# Paper Dossier: Runtime-Structured Task Decomposition

## Identity and review scope

- Local PDF: [`2605.15425-runtime-structured-decomposition.pdf`](../../papers/2605.15425-runtime-structured-decomposition.pdf)
- Manifest SHA-256: `8566964f244122ec14620e3eccde0b50d3399c24ea0f532a98899bc941d118be`
- Version or date: arXiv v1, 2026-05-14; reviewed 2026-08-20
- Workflow section: core verified workflow and decomposition
- Review question: does runtime branching and selective retry justify decomposing coding tasks into validated subtasks?
- Relevant evidence: complete five-page paper; Figures 1-3; Tables 1-2; Sections 2-5

## Plain-English contribution

The paper moves workflow structure out of a long prompt and into normal program logic. Small LLM calls return typed results. Code validates each result, stores only valid state, and retries only the failed step rather than rerunning an entire pipeline.

The evidence is about recovery cost under a deliberately injected malformed input. It does not show better task quality, because all three compared workflows were correct in every run.

## Exact claims and evidence

- **Two controlled cases, equal quality (direct result):** monolithic, static-decomposed, and runtime-structured configurations all achieve `100%` correctness over ten runs for a two-file/three-bug Python task and ten runs for a Kubernetes root-cause task. Tables 1-2.
- **Normal execution costs more when decomposed (direct result):** debugging uses `703 +/- 49` tokens monolithic, `2,181 +/- 240` static, and `2,225 +/- 270` RSTD. Kubernetes uses `904 +/- 17`, `2,553 +/- 224`, and `2,716 +/- 424`. Tables 1-2.
- **Selective retry is cheaper under the simulated failure (direct result):** debugging retry costs `703 +/- 49` monolithic, `933 +/- 93` static, and `460 +/- 77` RSTD. Kubernetes costs `904 +/- 17`, `1,632 +/- 145`, and `436 +/- 132`; RSTD is `51.7%` below monolithic and `73.2%` below static in that case.
- **Static decomposition can be worse (direct result):** Kubernetes static retry is `80.5%` above monolithic because it reruns three downstream stages.
- **Natural failure rate is low (direct result):** `0/40` subtask executions fail schema validation in debugging and `2/100` in Kubernetes. Retry-cost measurements therefore use a simulated malformed upstream input, not naturally observed task failure.
- **Latency overhead is material (direct result):** framework time is roughly 18% of total decomposed latency, while multiple API round trips raise overall latency to roughly 22-29 seconds versus 10-15 seconds monolithic.

## Method

- A developer-authored decomposition engine branches on schema validity, content thresholds, and completion state.
- Typed LLM judgment operators receive only bounded context and return schema-constrained outputs. Validation failure adds the error to a targeted repair prompt.
- A state manager stores valid outputs by subtask identifier; invalid results never become downstream state.
- Three configurations isolate runtime branching: one monolithic prompt, the same fixed static graph with cascading reruns, and RSTD with selective retry.
- Both use cases use `gpt-4` at temperature 0 and ten runs per configuration. Token counts use `tiktoken`; monolithic code comes from AutoGen/SRE-agent examples and structured code uses Mellea.
- Retry tests inject one structurally malformed input: validation failure in the debugging pipeline and root-cause-analysis failure in Kubernetes.

## Ablations and failure evidence

- Static decomposition is the key negative control: decomposition alone can raise retry cost.
- All configurations are equally correct, so no task-quality improvement is demonstrated.
- RSTD has the highest normal token cost in both cases and the highest latency in Kubernetes.
- Natural validation failures are only 0-2%; the paper does not measure whether expected retry savings repay normal overhead in deployment.

## Limitations and transfer risks

- Two hand-built controlled cases and ten repetitions at temperature 0 are too small for broad coding-agent claims.
- Simulated failures demonstrate an architectural cost property, not real failure frequency or end-to-end value.
- Policies and graphs are developer-authored; automatic decomposition is future work.
- The compared frameworks differ, so some overhead may be implementation-specific.
- Agentic Engineering's dependency planner computes read-only static/adaptive ordering. It neither executes judgment operators nor performs selective subtask retry, so the completed planning sentinel is not an RSTD reproduction.
- The verified state store shares the “only validated state advances” principle, but current retry granularity is a whole declared work item.

## Project transfer decision

- **Adopt:** invalid intermediate output must not become authoritative downstream state.
- **Adapt:** use declared work-item boundaries as selective retry units before adding finer LLM judgment stages.
- **Reject as a default:** decomposition for short tasks or low-failure pipelines; normal overhead can dominate.
- **Defer:** per-subtask model selection and dynamic branch creation until real trajectory data identifies expensive repeated stages.
- **Reproduce later:** inject equivalent bounded failures into monolithic, cascading-static, and selective-retry workflows while measuring total expected cost, not retry cost alone.

## Open questions

- At what observed failure probability does selective retry repay its normal overhead?
- Do schema-valid outputs correlate with semantically correct intermediate results?
- Can one framework implement all three conditions to remove framework confounds?
- Which real coding trajectories exhibit repeatable subtask-local failure?
