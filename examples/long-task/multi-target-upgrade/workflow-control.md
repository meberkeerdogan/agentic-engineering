# Canonical Rereading Workflow

Read `ACTIVE_SPEC.md`, inspect the existing modules, and run the visible tests. Implement one target at a time, checking the relevant callers before editing. After every meaningful change, rerun focused tests, then finish with the complete visible suite and inspect the final diff. Do not claim completion while a stated target is missing or a visible test fails.
