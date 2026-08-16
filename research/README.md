# Research Library

This directory keeps the evidence used to design and evaluate Agentic Engineering. It is intentionally separate from project guidance: a paper can motivate an experiment without becoming a permanent rule.

## Start Here

- [Critical review: Long-Horizon Agent Reliability](reports/2026-08-14-long-horizon-reliability-review.md)
- [Live Codex workflow pilot](reports/2026-08-16-live-codex-workflow-pilot.md)
- [Source index](sources.md)
- [PDF integrity and extraction manifest](papers/manifest.json)

## Paper Corpus

| Paper | Local PDF | Why it is included |
| --- | --- | --- |
| CodePlan | [2309.12499](papers/2309.12499-codeplan.pdf) | Adaptive dependency-aware repository planning experiment |
| Large Language Models Cannot Self-Correct Reasoning Yet | [2310.01798](papers/2310.01798-intrinsic-self-correction.pdf) | Limits of self-correction without external feedback |
| SWE-agent | [2405.15793](papers/2405.15793-swe-agent.pdf) | Evidence that agent-computer interface design affects performance |
| Agentless | [2407.01489](papers/2407.01489-agentless.pdf) | Simple, interpretable baseline for agentic systems |
| PaperBench | [2504.01848](papers/2504.01848-paperbench.pdf) | Hierarchical rubrics for research replication |
| AutoReproduce | [2505.20662](papers/2505.20662-autoreproduce.pdf) | Paper lineage and executable reproduction |
| EXP-Bench | [2505.24785](papers/2505.24785-exp-bench.pdf) | Evaluation of complete research experiments |
| Prometheus | [2507.19942](papers/2507.19942-prometheus.pdf) | Structural and temporal memory for repository navigation |
| Agentic Property-Based Testing | [2510.09907](papers/2510.09907-agentic-property-based-testing.pdf) | Agent-generated properties as complementary evaluators |
| Live-SWE-agent | [2511.13646](papers/2511.13646-live-swe-agent.pdf) | Experimental runtime scaffold self-modification |
| NL2Repo-Bench | [2512.12730](papers/2512.12730-nl2repo-bench.pdf) | Long-horizon repository generation benchmark |
| SWE-EVO | [2512.18470](papers/2512.18470-swe-evo.pdf) | Release-scale, multi-file software-evolution benchmark |
| CooperBench | [2601.13295](papers/2601.13295-cooperbench.pdf) | Evidence about failures in unstructured agent collaboration |
| ContextBench | [2602.05892](papers/2602.05892-contextbench.pdf) | Process-level evaluation of context retrieval |
| Evaluating AGENTS.md | [2602.11988](papers/2602.11988-evaluating-agents-md.pdf) | Evidence about repository-level context files |
| SWE-Milestone | [2603.13428](papers/2603.13428-swe-milestone.pdf) | Continuous software evolution and milestone DAG evaluation |
| CAID | [2603.21489](papers/2603.21489-caid.pdf) | Isolated, dependency-aware multi-agent execution |
| From Plan to Action | [2604.12147](papers/2604.12147-plan-to-action.pdf) | Plan quality, compliance, and reminder effects |
| Runtime-Structured Task Decomposition | [2605.15425](papers/2605.15425-runtime-structured-decomposition.pdf) | Deterministic orchestration and subtask-level retries |
| RoadmapBench | [2605.15846](papers/2605.15846-roadmapbench.pdf) | Long-horizon version-upgrade benchmark |
| TICoder | [2606.08135](papers/2606.08135-ticoder.pdf) | Test-driven planning and implementation-aware reuse |
| Progress Mirage | [2607.25152](papers/2607.25152-progress-mirage.pdf) | Self-evaluation bias and externally grounded verification |
| LongHorizon-Harness | [2608.01964](papers/2608.01964-longhorizon-harness.pdf) | Manager-executor-auditor harness architecture |
| Horizon Gap | [2608.06663](papers/2608.06663-horizon-gap.pdf) | Survey and taxonomy of long-horizon agent research |
| LivePlan | [2608.06701](papers/2608.06701-liveplan.pdf) | Deterministic monitoring and corrective steering |
| PMCoder | [2608.06811](papers/2608.06811-pmcoder.pdf) | Coupled planning, episodic memory, and stuck detection |
| SpecPath | [2608.09799](papers/2608.09799-specpath.pdf) | Active-contract resolution across changing requirements |

The first supplied response cited eight papers directly. RoadmapBench was discussed but missing from its footnotes, so its primary paper was added. The follow-up response incorrectly linked its NL2Repo-Bench claim to SWE-EVO; the actual NL2Repo-Bench paper was located and added. The archive now contains every research paper named or cited across both responses. Practitioner articles and official web guidance remain links in the source index rather than being mislabeled as papers.

## Reproducibility

Run the extraction and integrity check from the repository root:

```powershell
uv run --group research python research/scripts/extract_papers.py research/papers --manifest research/papers/manifest.json
```

The script checks the PDF signature, extracts every page, and records file size, page count, title, text length, and SHA-256. A changed preprint will therefore be visible rather than silently replacing the reviewed evidence.
Pass an optional output directory after `research/papers` when you also want to retain the extracted text.

## Corpus Policy

- Prefer primary papers and official technical sources.
- Record the exact downloaded artifact and checksum.
- Distinguish paper results from project design inferences.
- Record limitations, negative results, and transfer risks.
- Reproduce important claims locally before making them default workflow behavior.
- Add large corpora selectively; the current PDFs fit normal GitHub file limits, but Git LFS or external archival storage should be considered if this collection grows materially.
