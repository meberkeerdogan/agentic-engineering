# Paper Dossier: Prometheus

## Identity and review scope

- Local PDF: [`2507.19942-prometheus.pdf`](../../papers/2507.19942-prometheus.pdf)
- Manifest SHA-256: `e59b0b23e2c4dd2d6eb35c9a996abcf7d3423c8e5d70e740126a0323ebd7a86d`
- Version or date: arXiv v2, 2026-02-07; 21 pages
- Workflow section: memory and context
- Review question: does reusable repository-context memory improve long-horizon navigation enough to justify a memory layer in Agentic Engineering?
- Relevant evidence: Sections 2-4; Algorithm 1; Tables 2-5; Figures 3-7; threats to validity

## Plain-English contribution

Prometheus builds a structural map of a repository, lets an LLM navigate that map for each focused question, and stores useful code snippets so later questions can reuse them instead of searching again. This is a cache of repository evidence inside one issue-resolution run. It is not a ledger of project decisions or phase progress.

## Exact claims and evidence

- **End-to-end result (direct):** with GPT-5, Prometheus resolves `74.4%` of SWE-bench Verified and `33.8%` of SWE-PolyBench Verified. These are full-system results, not memory-only effects. Tables 2-3.
- **Retrieval hit rates (direct, protocol-limited):** on the paper's gold-patch-derived comparison, Prometheus reports file, symbol, and span hit rates of `0.915`, `0.850`, and `0.807`. Table 4 does not report precision, F1, sample uncertainty, or the full ContextBench protocol.
- **Working-memory ablation (direct):** on one random 50-task SWE-bench Verified subset, memory resolves `70%` at `$200.79`; no memory resolves `56%` at `$367.73`. The paper describes this as a `25%` relative resolution improvement and `45.4%` lower inference cost. Figure 7.
- **Other component effects (direct):** the full system resolves `74.4%`; removing bug reproduction yields `64.0%`, regression testing `70.2%`, and multiple-patch selection `68.8%` in Table 5. The surrounding prose says `69.2%` for patch selection, an internal inconsistency.

## Method

- Tree-sitter turns source into file and AST nodes; documentation becomes linked text chunks. Neo4j stores the graph.
- An LLM converts a need into an essential query, extra requirements, and purpose. It checks memory first, then traverses graph tools on a miss.
- Retrieved spans are structurally deduplicated, reordered by source location, and stored as context units with file and line provenance.
- Each memory record embeds the three query fields separately. Approximate nearest-neighbor candidates are unioned, cosine-reranked, thresholded at `0.85`, and limited to five entries. PostgreSQL stores the records.
- The full pipeline also classifies issues, reproduces bugs, generates up to five patches, verifies them in Docker, and can use web search. GPT-5 runs at temperature `1.0`.

## Ablations and failure evidence

- The memory ablation has only 50 tasks and one run per condition because of cost. No confidence interval or paired significance test is reported.
- The main leaderboard comparison mixes systems, models, tools, and orchestration. It cannot attribute the headline result to memory.
- The full-system ablations isolate one component at a time, but do not isolate knowledge-graph retrieval from memory retrieval.
- ContextBench later finds Prometheus has high recall but low precision and lower retrieval F1 than a simple mini-SWE-agent baseline. More context is not automatically better context.

## Limitations and transfer risks

- Prometheus memory retains query-relevant code context during one repair episode. Agentic Engineering's phase memory retains evidence-backed decisions, failures, and artifacts across declared phases. Calling our mechanism a Prometheus reproduction would be incorrect.
- The graph, embedding service, databases, multi-agent stages, web search, and patch sampling add material complexity. Our present tasks have not shown repository navigation to be the bottleneck.
- The authors fix prompts and settings but explicitly report one run per experiment. Serving and model variance remain unmeasured.

## Project transfer decision

- **Adopt:** every retained item must preserve source location and provenance. Surface: `phase_memory.py`; gate: references must resolve and retrieved summaries remain subordinate to canonical evidence.
- **Adapt:** memory-first reuse and bounded retrieval. Our deterministic task/phase ranking replaces embeddings and graph traversal. Gate: beat canonical rereading on non-ceiling tasks without losing correctness.
- **Defer:** repository knowledge graph, semantic embeddings, and multi-agent retrieval. Required evidence: diagnose repeated repository search as a material failure or cost source first.
- **Reject:** interpreting the 50-task, single-run ablation as proof that our phase ledger will improve outcomes.

## Open questions

- Would a cheap symbol index match most of the graph's benefit?
- How sensitive are the memory results to the selected 50 tasks and similarity threshold?
- What are precision, redundancy, and evidence-retention results under a shared ContextBench protocol?
