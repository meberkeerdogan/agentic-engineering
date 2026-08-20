# Workflow Section Research Audit

This audit tracks whether each product section has replication-grade paper review, not merely citations or design-level summaries. `Retrospective required` means implementation already exists but the new research gate was not completed first.

These retrospective reviews improve research quality, but they are not `v0.1` release blockers unless a review finds a concrete correctness or safety problem in the supported product path.

| Workflow section | Priority papers | Current evidence | Gate status | Next record |
| --- | --- | --- | --- | --- |
| Core verified workflow | LongHorizon-Harness, Progress Mirage, SpecPath, Agentless, Runtime-Structured Task Decomposition | [Five paper dossiers and full synthesis](reviews/core-workflow/SYNTHESIS.md); implementation-alignment audit; scoped Progress Mirage fixture | Retrospective gate passed | Run the predeclared harder matched evaluation before any default promotion |
| Memory and context | Prometheus, ContextBench, PMCoder | Full dossiers and [synthesis](reviews/memory/SYNTHESIS.md); implementation audit; preserved 18-cell negative result | Retrospective gate passed | Add retrieval-quality instrumentation and harder non-ceiling tasks before another live run |
| Long-task evaluation | SWE-EVO, RoadmapBench, SWE-Milestone, NL2Repo-Bench | Benchmark summaries and representative fixtures | Retrospective required | Benchmark dossiers and task-validity synthesis |
| Planning and monitoring | CodePlan, From Plan to Action, LivePlan, PMCoder | Implemented experiments, sentinel results, and watchdog calibration | Retrospective required | Planning and monitoring dossiers plus alignment audit |
| Testing and evidence | Agentic Property-Based Testing, TICoder, Progress Mirage | Offline property-evidence mechanism and external-verification design | Retrospective required | Testing dossiers and live evaluation design |
| Multi-agent orchestration | CAID, CooperBench, Runtime-Structured Task Decomposition | Offline isolated runner and no default promotion | Retrospective required | Multi-agent dossiers and single-agent comparison design |
| Reproduction methodology | PaperBench, AutoReproduce, EXP-Bench | Reproduction toolkit and one scoped claim reproduction | Retrospective required | Methodology dossiers and toolkit conformance audit |
| Repository guidance and agent interface | Evaluating AGENTS.md, SWE-agent, Agentless | Bounded guidance and baseline design | Retrospective required | Guidance/interface synthesis and onboarding implications |
| Learning Companion | No direct paper currently selected | Product-derived proposal-only boundary | Evidence-source decision required | Literature search or explicit novel-design rationale |

## Repair order

1. Core verified workflow, because it supports the product's central claim.
2. Memory and context, because a full live campaign has already completed.
3. Long-task evaluation, because harder tasks are the next research need.
4. Planning and monitoring.
5. Testing and evidence.
6. Multi-agent orchestration.
7. Reproduction methodology.
8. Repository guidance, interface, and Learning Companion.

Each repair is a separate milestone with its own review files, tests or integrity checks, commit, and evidence-linked learning report.
