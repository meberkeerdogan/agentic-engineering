# Long-Task Evaluation Review: Synthesis

## Plain-English answer

Our existing test system works, but our three demonstration tasks are too easy to prove that it helps with long projects. They contain only 8-12 lines of starting source code and one or two test files. Every control and treatment run completed, so the experiments mostly tested plumbing and safety.

The papers agree that a useful long-task test needs several meaningful goals, many connected files, persistent changes, strong regression checks, and partial-progress reporting. The most revealing comparison is not “did the agent stay busy?” It is “can the agent keep earlier work correct while completing later work?”

## What the papers agree on

1. **Isolated success does not compose automatically.** SWE-Milestone shows strong isolated milestone results collapsing under continuous work in the same repository.
2. **Binary completion hides useful information.** SWE-EVO, RoadmapBench, and SWE-Milestone all add partial-progress metrics while keeping full verified completion visible.
3. **Regressions are central.** Partial credit without protected old behavior can reward destructive progress.
4. **Medium difficulty is most useful for comparison.** Very small tasks create a ceiling; extremely large tasks create a floor. RoadmapBench sees the clearest model separation in the middle ranges.
5. **More steps are not the same as progress.** RoadmapBench and NL2Repo-Bench show performance saturating after a useful working range. SWE-Milestone finds blind repeated editing with little testing performs badly.
6. **Benchmark quality needs its own verification.** RoadmapBench repaired 45 of 115 draft tasks after rollout review. Instructions, tests, environment, and oracle solutions must agree before agents are compared.

## Important differences

- **SWE-EVO** tests one large release-sized final change. It is good for broad coordination but hides intermediate failure unless tests are grouped.
- **RoadmapBench** tests one version upgrade with named targets and weighted partial credit. It is the closest template for a harder single-run task pack.
- **SWE-Milestone** streams dependent goals into one persistent repository. It is the best template for measuring error accumulation and recovery.
- **NL2Repo-Bench** starts from an empty workspace. It teaches packaging and completion lessons, but it is not the main v0.1 product mode.

## Current implementation audit

| Current surface | What is useful | Why it is not enough yet |
| --- | --- | --- |
| Three-task representative pack | Different task labels, isolated workspaces, declared evaluators, three repeated runs | Starting repositories have only 8-12 source lines and at most two test files; all live runs reached 100% |
| Evidence contracts | Separate target and protected checks; independent acceptance | No grouped target-level partial score or progress-over-time view |
| Batch runner | Matched arms, budgets, resumability, cost/time, false-completion records | Seed numbers label repeated model runs but do not create different task content or guarantee independent randomness |
| Roadmap fixture | Mentions dependencies and checks six target tests | It is one small edit, not a persistent sequence of agent-created milestones |
| Phase memory campaign | Preserves supersession and eviction evidence; records a negative result | It cannot show value when canonical rereading already solves every task |

## Corrections to earlier project claims

- The stored SWE-EVO v6 paper is internally inconsistent. Its prose says the best result is `25%`, but Table 2 contains SWE-agent results of `39.58%` for GLM-4.7 and `37.50%` for GLM-5. We will not repeat the 25% headline without this warning.
- NL2Repo-Bench reports `40.2%` in Table 3 but `39.6%` in its conclusion, and reports DeepSeek V3.2 differently across Tables 3 and 6.
- Planning-tool use, exploration, and test frequency are correlations in several analyses. They do not prove that adding a planner, more reading, or more tests causes better outcomes.
- A benchmark dependency graph schedules work; it does not prove that our adaptive dependency planner improves agents.

## Product decision

Do not add another workflow mechanism yet. First replace the ceiling-prone efficacy pack with a bounded long-task ladder described in [HARDER_TEST_DESIGN.md](HARDER_TEST_DESIGN.md).

The core product can still move toward `v0.1` as an experimental, evidence-first workflow toolkit. However, it is not ready for strong claims about improving long projects until at least the offline harder-task ladder is implemented and one small matched live sentinel shows that the tasks produce useful variation rather than universal success or failure.

## Gate status

The long-task retrospective research gate is **complete** for SWE-EVO, RoadmapBench, SWE-Milestone, and NL2Repo-Bench. No paid agent run is authorized by this review.
