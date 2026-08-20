# Paper Dossier: ContextBench

## Identity and review scope

- Local PDF: [`2602.05892-contextbench.pdf`](../../papers/2602.05892-contextbench.pdf)
- Manifest SHA-256: `517140a2504959bfb94c7c875f6e80a031e899bc362dcc73c446536b45e18a46`
- Version or date: arXiv v3, 2026-02-11; 34 pages
- Workflow section: memory and context
- Review question: how should we measure whether memory retrieves useful context rather than merely more context?
- Relevant evidence: Sections 2-4; Tables 1-5; Appendices A, G, and H

## Plain-English contribution

ContextBench evaluates the evidence an agent finds while it works, not only whether its final patch passes. Experts mark a compact set of code needed to solve each issue. The benchmark then measures how much of that evidence an agent finds, how much noise it collects, how often it rereads the same material, and whether useful evidence survives until patch generation.

## Exact claims and evidence

- **Corpus (direct):** `1,136` tasks from 66 repositories and eight languages, with `4,548` files, `23,116` blocks, and `522,115` context lines. A 500-task Lite subset supports lower-cost evaluation. Table 1.
- **Simple scaffold result (direct):** with GPT-5 on Lite, mini-SWE-agent has the best file F1 (`0.634`) and block F1 (`0.375`) of the five scaffolds, while Prometheus has higher block recall (`0.646`) but much lower precision (`0.258`) and equal block F1 to SWE-agent (`0.285`). Prometheus has the best Pass@1 (`0.512`). Table 2.
- **Model result (direct):** Claude Sonnet 4.5 reaches the best Pass@1 (`0.530`) and line F1 (`0.344`) under mini-SWE-agent; all four models remain below `0.45` block F1 and `0.35` line F1. Table 3.
- **Retrieval dynamics (direct):** GPT-5 averages 5.87 retrieval steps with 119.29 lines per step at `$0.45`; models trade early coverage against redundancy. All show evidence usage drop. Tables 4-5.
- **Gold-context robustness (direct case study):** for 82 tasks with two or three semantically equivalent valid patches, average gold-context Jaccard similarity is `0.9518`. Section 3.5.

## Method

- The authors combine four issue benchmarks, remove exact and embedding-similar duplicates, score difficulty, and manually remove semantically trivial cases.
- Six authors and experienced developers annotate contexts over four months. A strong LLM receives only the annotated context and gets five patch attempts; at least one official-test-passing patch establishes sufficiency. Other cases use annotation agreement and refinement.
- Tree-sitter aligns gold and agent evidence at file, AST-block, and line levels.
- Metrics include recall, precision, F1, early coverage (AUC-Cov), repeated retrieval, and evidence keep/drop between exploration and final patch context.
- Gold contexts are compact and verified as sufficient, but the authors do not claim global minimality.

## Ablations and failure evidence

- More complex agent scaffolding does not consistently improve retrieval F1 over mini-SWE-agent.
- High recall often comes with low precision; broad retrieval can add reasoning noise.
- Agents can find gold evidence and later drop it, so retrieval alone is not successful memory use.
- Gold context is conditioned on accepted patches. Alternative helpful evidence may be penalized, although the 82-task robustness result reduces this concern.

## Limitations and transfer risks

- ContextBench evaluates repository code retrieval, not decision supersession, phase transitions, or durable project memory.
- Its gold-context construction is expensive and is unsuitable as the only routine product metric.
- Pass@1 and retrieval quality are related but not interchangeable; one should not be used as proof of the other.
- Agentic Engineering's completed 18-cell campaign measured verified completion, regressions, cost, time, and memory errors, but not recall, precision, redundancy, or evidence drop.

## Project transfer decision

- **Adopt:** measure evidence quality separately from final task success. Required metrics for the next memory experiment: relevant-item precision/recall, repeated reads, obsolete-item exposure, and final evidence retention.
- **Adapt:** use fixture-declared necessary evidence for bounded experiments before paying for expert gold-context annotation.
- **Adopt:** keep a simple search or canonical-rereading control; complex memory must prove value.
- **Reject:** promoting memory because it retrieves more context or because the agent mentions the correct retained item.

## Open questions

- Which ContextBench metrics best predict failure on repository-evolution tasks rather than issue repair?
- Can evidence-retention metrics be collected from Codex trajectories without exposing private content?
- How should alternative valid evidence paths be credited in our smaller fixtures?
