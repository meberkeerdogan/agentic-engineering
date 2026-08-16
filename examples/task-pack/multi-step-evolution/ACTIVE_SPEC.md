# Active specification: roadmap evolution

Evolve the existing roadmap helpers into a dependency-aware progress summary.

Requirements:

- Add `ready_item_ids(items)` to `roadmap.py`.
- An item is ready when its status is `pending` and every ID in `depends_on` is completed.
- Return ready IDs sorted alphabetically and do not mutate the input.
- Add `blocking_dependencies(items)` to `roadmap.py`.
- Return a mapping from each blocked pending item ID to its sorted incomplete dependency IDs. Do not include ready or completed items.
- Add `build_progress_summary(items)` to `progress.py`.
- Return `total`, `completed`, `completion_ratio`, `ready`, and `blocked`; use `0.0` for the empty ratio and round non-empty ratios to two decimals.
- Preserve the existing item listing and completed-count behavior.

Use only the Python standard library and run all unit tests.
