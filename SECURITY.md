# Security Policy

Agent Loops is early-stage software. Please do not use unreleased code to run untrusted automation in sensitive environments.

## Reporting a Vulnerability

If you believe you found a security issue:

1. Do not open a public issue with exploit details.
2. Contact the maintainers privately once a security contact is published.
3. Include a clear description, reproduction steps, impact, and any suggested mitigation.

Until a private contact is listed, open a public issue with a high-level note that a private security report is needed, without sharing exploit details.

## Security Principles

- Human approval should be required for destructive or high-risk actions.
- Loop and skill definitions should make tool access and permissions visible.
- Secrets should never be committed to the repository.
- Logs should avoid leaking tokens, private prompts, credentials, or user data.
- Verification should happen before publishing, deploying, or handing off important work.
