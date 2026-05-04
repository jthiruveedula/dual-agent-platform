# Security Policy

## Reporting a vulnerability

If you believe you have found a security vulnerability, **do not open a public issue**. Instead, contact the maintainer privately via GitHub security advisory on this repository, or by emailing the maintainer listed on the GitHub profile.

Please include:

- A clear description of the issue
- Steps to reproduce or a proof-of-concept
- Affected commit, branch, or release
- Suggested remediation if known

We aim to acknowledge reports within 5 business days and provide an initial assessment within 10 business days.

## Scope

In-scope:

- Bypass of `policy_guard`, `approval_gate`, or `dangerous_action_guard`
- Secrets/PII leakage into memory, logs, or evidence
- Path traversal or injection in tool wrappers
- Privilege escalation in GCP tool wrappers
- Supply-chain risks in declared dependencies

Out of scope:

- Findings against forks or modified copies
- Issues requiring physical access to a developer machine
- Best-practice suggestions without an exploit path

## Disclosure

We practice coordinated disclosure. We will publish a security advisory after a fix is available and adopters have a reasonable upgrade window.

## Hardening expectations for adopters

- Do not disable safety guards in production.
- Pin a known-good commit; review `tools/safety/policies.json` changes carefully.
- Set `DAP_ENV=prod` only on environments with full approval workflows wired up.
- Treat `memory/` directories as sensitive; redact before sharing.
