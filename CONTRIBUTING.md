# Contributing

Thank you for considering a contribution. This project is opinionated about safety and tool-first execution; please read this file fully before opening a PR.

## Philosophy

- **Tool-first.** Add or extend tools; do not script around them.
- **Safety is non-negotiable.** Mutating code paths must route through the safety stack.
- **Docs are part of the change.** Behavior changes without doc changes will be rejected.
- **Small, reviewable PRs.** Large changes start as a discussion issue.

## Welcome contributions

- New tools under `tools/gcp/`, `tools/integrations/`.
- New reducers under `tools/reducers/`.
- New skills under `prompts/skills/`.
- New memory schemas (additive) under `tools/memory/`.
- New tests, fixtures, and CI improvements.
- Documentation upgrades.

## Propose large changes first

For anything touching `agents/*`, `tools/safety/*`, `tools/core/contracts.py`, or the policy table, open an issue describing intent, blast radius, rollback, and tests **before** writing code.

## Branch and PR workflow

1. Fork or branch from `main`. Use `feat/`, `fix/`, `docs/`, `safety/` prefixes.
2. Keep PRs under ~400 lines of diff where possible.
3. Reference an issue if one exists.
4. Fill out the PR description: what, why, blast radius, tests, docs updated.
5. Pass CI: `ruff check .` and `pytest -q`.

## Coding standards

- Python 3 typed where practical; prefer dataclasses or pydantic for tool I/O.
- Pure functions for reducers. No hidden network calls.
- Tools return `ToolResult` from `tools/core/contracts.py`.
- No secrets in code, tests, or memory. Use env vars.

## Testing requirements

- New tools: at least one happy-path and one failure-path test.
- Safety changes: deny / approval / allow tests in `tests/safety/`.
- Memory changes: roundtrip test in `tests/memory/`.
- Behavior changes that touch the runtime: extend `tests/test_smoke_e2e.py`.

## Safety requirements

- Any new destructive verb must be added to `tools/safety/policies.json` with explicit `deny` or `requires_approval`.
- New mutating tools must be decorated by `dangerous_action_guard` or call it explicitly.
- Never log raw payloads that may contain PII.

## How to add things

- **New tool, reducer, skill, integration, or memory schema:** see [docs/development.md](docs/development.md).
- **Approval-gated code:** see [docs/safety.md](docs/safety.md).

## Documentation

If your PR changes any public behavior, update the matching doc(s) in `docs/`. Update [README.md](README.md) only if landing-page facts change.

## Review expectations

- A maintainer reviews within a reasonable window; bumping the PR with a comment is fine.
- Safety PRs require explicit maintainer approval.
- Squash-merge by default.

## Issue triage labels (suggested)

`type:bug`, `type:feature`, `type:docs`, `area:safety`, `area:memory`, `area:gcp`, `area:integrations`, `good-first-issue`, `needs-design`.

## Code of Conduct

By contributing you agree to abide by [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
