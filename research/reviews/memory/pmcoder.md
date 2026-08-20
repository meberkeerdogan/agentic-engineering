# Paper Dossier: PMCoder

## Identity and review scope

- Local PDF: [`2608.06811-pmcoder.pdf`](../../papers/2608.06811-pmcoder.pdf)
- Manifest SHA-256: `7ea41c90dee4f328e16c90fca5c99ac7441377cbb20e6793f2ebbb1e8663f5d0`
- Version or date: arXiv v1, 2026-08-07; 12 pages
- Workflow section: memory and context
- Review question: does coupling a live phase planner with episodic memory improve issue resolution, and how closely does our phase-memory experiment match it?
- Relevant evidence: Sections III-VII; Figures 1-5; Tables I-VIII

## Plain-English contribution

PMCoder tracks which repair phase an agent is in, retrieves a limited set of earlier observations suited to that phase, and uses repeated failures or edit churn to trigger replanning. The connection works both ways: the plan changes what memory shows, and memory statistics can change the plan. Verification progress is strengthened with issue-reproduction scripts instead of trusting the model's claim.

## Exact claims and evidence

- **Matched headline result (direct):** across three complete SWE-bench Verified runs with Qwen3-Coder-30B, PMCoder averages `167.3/500` resolved (`33.5%`) versus `142.3/500` (`28.5%`) for a harness-matched mini-SWE-agent baseline: `+25` cases or `+5.0` percentage points. The cluster-bootstrap 95% interval is `[+14.3, +35.7]`, `p < 0.001`. Table III.
- **Coupling ablation (direct):** three-run means are baseline `142.33`, plan-only `148.67`, memory-only `150.67`, and plan+memory `167.33`. The interaction contrast is `+10.3` cases (`+2.1pp`), with `F(1,8)=10.92`, `p=0.011`. Table VIII and Figure 5.
- **Behavioral mechanism (direct):** compared with baseline, failed-action recurrence is halved, give-up/empty-patch rate falls from `8.3%` to `2.7%`, context exhaustion from `6.7%` to `3.0%`, and revert-then-refix recoveries rise from `2.89` to `4.23`. Table V.
- **Grounding split (direct, first-seed analysis):** on instances without a validated reproduction script, PMCoder gains `+12/315`; on armed instances it gains `+19/185`. This supports a plan-memory effect beyond the execution gate but is not a randomized component isolation.
- **Generality probes (direct, single-run):** gains remain positive for DeepSeek-V4-Flash (`+16`), Claude Haiku 4.5 (`+14`), an OpenHands port (`+23`), and TerminalWorld's 20-task official sample (`7/20` versus `5/20`). These are supporting probes, not repeated headline evidence.

## Method

- A start-of-task LLM call creates typed subtasks. Per-step phase detection, progress, hysteresis, and replanning are deterministic across exploration, hypothesis, implementation, and verification.
- Every message becomes an episodic memory node with role, recency, summary, edit status, and touched-file metadata. Retrieved output is not re-ingested.
- A fixed task/recent core plus a phase-conditioned working set fits a token budget. Beam search uses maximal marginal relevance over lexical relevance, file-graph proximity, diversity, and active-subtask keywords.
- Phase policy changes retrieval budgets and weights. Memory-derived failed-return, repeated-edit, read-saturation, and repeated-action statistics can trigger backtracking and a bounded recovery stack.
- The system appends plan and memory context to the latest tool result without rewriting tool-call history.
- Validated issue-reproduction scripts and Python compile checks strengthen verification and edit recovery. The official SWE-bench harness alone assigns final success.
- Headline runs use a 250-step, `$3` per-instance budget and 65,536-token context cap. Qwen headline and the 2x2 ablation have three runs per arm.

## Ablations and failure evidence

- Plan-only and memory-only both help modestly, while their observed combination helps more. This is stronger evidence for coupling than a full-system comparison alone.
- The reproduction gate is not separately ablated from edit-integrity recovery, so their individual contributions remain uncertain.
- Benefits concentrate in tasks the base model can already solve; both arms remain near zero on the longest human-time tier.
- Cross-model, framework, and TerminalWorld checks are single runs. Transfer to private repositories and other languages remains untested.
- Official tests can accept plausible but semantically imperfect patches; the paper claims benchmark improvement, not maintainer-approved patch quality.

## Limitations and transfer risks

- Our `phase_memory.py` is a deterministic, read-only view over manually supplied evidence records. It does not capture every trajectory message, compute lexical/graph retrieval, detect live phases, update plans from memory statistics, inject context automatically, run reproduction gates, or recover edits.
- Our 18-cell campaign tested three small repositories and repeated seed labels with perfect control completion. It is an adaptation and a safety/overhead test, not a PMCoder reproduction.
- Our treatment's supersession and capacity rules address stale decisions and bounded project context, a different memory problem from PMCoder's in-episode trajectory loss.

## Project transfer decision

- **Adopt:** phase should condition which evidence is surfaced, and verified execution—not self-report—should control completion.
- **Adapt:** keep provenance, supersession, and deterministic bounds from our project-memory use case.
- **Reproduce next:** build a bounded PMCoder-style comparison on non-ceiling issue tasks, with automatic trajectory capture, phase-conditioned recall, stuck signals, and a plan+memory versus isolated-component matrix.
- **Defer:** automatic revert-then-refix and reproduction-generated plan transitions until their permissions and failure recovery are independently tested.
- **Reject:** describing the completed campaign as validation of PMCoder's bidirectional coupling.

## Open questions

- Does the public replication package reproduce the paper's three-run counts in our environment?
- Which coupling—phase-to-retrieval or memory-to-replanning—creates most of the interaction gain?
- Can deterministic provenance rules coexist with automatic episodic capture without storing unsafe or stale claims?
