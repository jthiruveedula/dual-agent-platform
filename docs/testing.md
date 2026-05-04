# Testing

This document describes how the dual-agent platform is tested and how to run, extend, and debug the test suite.

## Goals

Testing in this repository optimizes for:

- **Determinism**: tests must produce stable results across runs and environments.
- **Safety coverage**: every guard in the safety chain has explicit tests.
- **Contract stability**: shared tool contracts (`ToolResult`, `RiskLevel`) are protected by tests.
- **Memory correctness**: lesson read/write paths are covered end-to-end.

## Test layout

```text
tests/
  # Safety, memory, smoke e2e, and core contract tests
```

Test categories include:

| Category | Purpose |
| --- | --- |
| Safety tests | Validate `policy_guard`, `approval_gate`, and `dangerous_action_guard` behavior. |
| Memory tests | Validate `MemoryStore`, lesson writer, and lesson retriever paths. |
| Smoke e2e | Exercise an Architect -> Builder happy path through the safety chain. |
| Core contract tests | Pin shared types and tool result envelopes. |

## Running tests

From the repository root:

```bash
pytest -q
```

For a single test file:

```bash
pytest -q tests/<file>.py
```

For a specific test by name:

```bash
pytest -q -k <expression>
```

## Linting

The repository uses Ruff. Run it locally before pushing:

```bash
ruff check .
```

Linting and tests are enforced by the CI workflow defined under `.github/`.

## Writing new tests

1. Place tests under `tests/` with a clear name reflecting the unit under test.
2. Prefer pure-function and contract-level tests over integration where possible.
3. For safety changes, add a test case for **allow**, **approval-required**, and **deny** outcomes.
4. For memory changes, exercise both read and write paths.
5. Keep fixtures minimal and avoid network calls.

## Continuous integration

CI runs Ruff and pytest on every push. Failing checks block merges via standard branch protection where configured.

## Related docs

- [`development.md`](development.md)
- [`safety.md`](safety.md)
- [`memory-and-self-correction.md`](memory-and-self-correction.md)
