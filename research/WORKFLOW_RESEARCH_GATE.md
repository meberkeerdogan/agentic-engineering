# Workflow Research Gate

Every research-backed workflow section must pass this gate before new implementation begins or an experimental mechanism is promoted. Completed sections that predate the gate must pass it retrospectively before further expansion.

The gate prevents a paper's headline, abstract, or second-hand summary from becoming a product rule without understanding the tested setting and transfer limits.

## Required sequence

1. **Define the section question.** State the agent problem, intended users, simpler baseline, and decision the evidence must support.
2. **Select primary sources.** Name the papers that directly test the mechanism, the papers that challenge it, and any benchmark or methodology papers needed to interpret results.
3. **Read each paper in full.** Review the method, task and dataset construction, models, prompts and tools, sample sizes, metrics, baselines, ablations, results, limitations, appendices, and available code or artifacts. Bind the reviewed PDF to its manifest checksum.
4. **Create a paper dossier.** Use [`reviews/TEMPLATE.md`](reviews/TEMPLATE.md). Separate direct paper claims from project inferences and record exact evidence locations.
5. **Synthesize across papers.** Explain agreements, conflicts, missing evidence, transfer risks, and whether the proposed product setting matches the studied setting.
6. **Make explicit transfer decisions.** For each idea choose `adopt`, `adapt`, `reproduce`, `reject`, or `defer`, with a reason. Never describe an adapted experiment as a paper reproduction.
7. **Predeclare the evaluation.** Fix the control, treatment, tasks, repetitions, metrics, budgets, failure conditions, and promotion rule before live results are observed.
8. **Link implementation to evidence.** The module documentation must link its dossiers, synthesis, experiment definition, and final result.

## Passing criteria

A workflow section is research-ready only when:

- every directly relevant primary paper has a completed dossier;
- important negative or conflicting evidence is included;
- claims preserve the paper's tested scope and sample size;
- paper results, project inferences, and new project contributions are clearly distinguished;
- material differences from paper methods are documented;
- a simpler baseline and falsifiable promotion rule exist;
- unresolved evidence gaps are named instead of silently assumed away.

An implementation can be technically complete while this gate remains incomplete. In that case it must stay experimental and cannot be presented as research-validated.

## Retrospective rule

For sections implemented before this gate:

1. preserve the existing implementation and historical experiment results;
2. complete the missing dossiers and synthesis;
3. compare the implementation with the actual paper methods;
4. record deviations, unsupported assumptions, and corrections;
5. revise future experiments or defaults without rewriting the historical record.

Retrospective review may validate the existing design, narrow its claims, or require a new experiment. It does not automatically require rewriting working code.
