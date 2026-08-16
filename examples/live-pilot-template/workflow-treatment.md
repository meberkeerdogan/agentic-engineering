# Verified-loop treatment workflow

Use a short evidence-driven loop:

1. Read the active specification and translate every requirement into a check.
2. Inspect the repository and implement only the requested change.
3. Run the declared tests and inspect the resulting diff.
4. If a required check fails, make one focused correction and rerun all checks.
5. Claim completion only when every requirement has direct evidence and protected behavior still passes.

Stop after the bounded task is verified. Do not broaden the task or add dependencies.
