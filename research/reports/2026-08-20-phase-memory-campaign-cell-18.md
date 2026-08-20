# Phase-Memory Campaign: Cell 18 and Final Result

**Date:** 2026-08-20

**Model:** `gpt-5.6-luna` through the existing ChatGPT Codex login

**Batch:** `codex-memory-campaign-001`

**Cell:** Bounded phase-memory treatment, `roadmap-evolution`, seed `2`

## Final cell

The eighteenth campaign cell passed and completed the full matrix. A fresh plugin-free and MCP-free preflight succeeded, the task ran in an isolated workspace containing `workflow-phase-memory.md` but not `workflow-no-memory.md`, and independent evaluation accepted both implementation artifacts plus all six tests.

| Measure | Cell 18 | Per-cell ceiling |
| --- | ---: | ---: |
| Verified completion | 100% | required |
| Regressions | 0 | 0 |
| False completion | 0 | 0 |
| Estimated credits | 0.230348 | 0.5 |
| Wall time | 69.953 s | 300 s |
| Human interventions | 0 | 0 |

The measured turn used 118,042 input tokens, including 93,696 cached, 2,059 output tokens, and 416 reasoning tokens.

The memory ledger exactly matched the source SHA-256 digest `bfd76819f32a2711aa824afbd02c0def77621956f093690ae67c0777f17bea79`. Its deterministic view retained `roadmap-current`, `roadmap-evidence`, and `roadmap-failure` and evicted `roadmap-distractor`. The agent explicitly recognized that the distractor was excluded. Its eight-event trajectory independently verified with zero watchdog signals, intervention, or memory-attributable error.

Against seed `2` control, treatment quality was equal, cost was `0.22%` lower, and time was `10.62%` lower. Across all three roadmap pairs, quality was equal, treatment cost was `0.22%` lower, and treatment time was `4.93%` lower.

## Complete 18-cell result

| Task block | Control credits | Treatment credits | Cost difference | Control seconds | Treatment seconds | Time difference |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Low-pressure median | 0.529814 | 0.636748 | +20.18% | 179.923 | 173.187 | -3.74% |
| Supersession restock | 0.719620 | 0.720647 | +0.14% | 225.578 | 199.953 | -11.36% |
| Eviction roadmap | 0.682923 | 0.681413 | -0.22% | 213.750 | 203.202 | -4.93% |
| All nine runs per arm | 1.932357 | 2.038808 | +5.51% | 619.251 | 576.342 | -6.93% |

Both arms achieved `9 / 9` independently verified completions with zero regressions, false completions, or human interventions. All six pressure-task treatments correctly applied supersession or eviction. Across only the six pressure-task pairs, treatment cost was effectively equal (`0.03%` lower) and time was `8.23%` lower, but verified completion remained equal.

The complete campaign used `3.971165` measured credits and `1,195.593` model seconds. Six observe-only watchdog alerts across five cells were reviewed as contextual false positives and made no intervention.

## Promotion decision

**Decision: do not promote bounded phase memory as the default workflow. Keep it optional and experimental.**

The predeclared rule required at least a `0.10` improvement in mean verified completion across the supersession and eviction tasks. The observed improvement was `0.00`, so the primary efficacy condition failed. All safety and overhead conditions passed:

- no completion loss on the low-pressure task;
- no memory-attributable errors;
- no additional regressions or false completion;
- mean treatment cost increased by only `0.011828` credits per run, below the `0.10` limit;
- mean treatment time decreased by `4.768` seconds per run;
- no human intervention.

The result establishes that the deterministic memory mechanism is safe and behaves as designed on these tasks. It does not establish better coding outcomes. The next useful experiment should use harder, longer tasks where the baseline does not already achieve perfect completion, more memory pressure, additional repositories and models, and more repeated runs. Any efficiency hypothesis should be declared before that experiment rather than inferred after this one.

## Reproducibility

The private raw evidence remains under ignored `.agentic-runs/live-batches/codex-memory-campaign-001/` storage. The generated 18-run experiment report has fingerprint `82270bdbe8cf04b2af576cd6026f640ad4a3a737e03dc161aec3bdbcd2dff553` and file SHA-256 `dd81a6bf7ad8955f2d7a15f6644417b2483956015ae074f4b26fc02b49928679`.

Final-cell evidence fingerprints:

- Evaluation report: `1e89c7ebc8f0eb399abbad661303b3014b5df23e6c58011462a1946f2bebb9b5`
- Memory view: `22acaeeb9261e0aa466de960fbf7d1e0f6ad1985471100e4d297a90fdd459594`
- Trajectory: `b765591fd90402442bda1767a3364d77a6fd434625d1ec790564e982f2b94009`
- Watchdog report: `8d36bc456f51b647999890cb675ba00fc3024f510b4011e1ced92bfde01f714c`
- Campaign plan: `6367dd78e47b2880239bb4b143484c3a028f5e5e151e7bbb528f4e1c4e43076f`
- Live configuration: `1f5ce84cb123d9a9f3d8764de3028fe566d3f943b58f3f3f0321ed31e3e2d5a3`
- Execution inputs: `1c461c40d8e35ee222851d080ed6217e8ad36940916d0a171876db85446d5307`
