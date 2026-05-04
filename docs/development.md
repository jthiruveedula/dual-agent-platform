# Development

Local development workflow and extension recipes.

## Local dev workflow

```bash
git clone https://github.com/jthiruveedula/dual-agent-platform
cd dual-agent-platform
python -m venv .venv && source .venv/bin/activate
pip install -e .
ruff check .
pytest -q
```

## Dependency management

- Declared in `pyproject.toml`. Pin transitive deps only when a real incompatibility exists.
- Avoid heavy SDKs as hard dependencies; prefer optional extras.
- Stub external SDKs in tests using fakes under `tests/`.

## Lint, format, type

- `ruff check .` (CI-enforced)
- `ruff check . --fix` for auto-fixes
- Type hints encouraged; gradual adoption is fine.

## Test strategy

- Unit tests close to the module under test.
- `tests/safety/` covers deny / approval / allow paths for `policy_guard`.
- `tests/memory/` covers JSONL roundtrip for lessons.
- `tests/test_smoke_e2e.py` covers Architect -> Builder -> tool -> memory.
- `tests/test_core_contracts.py` covers `tools.core.contracts` invariants.

See [testing.md](testing.md).

## Adding a new tool

1. Create the module under `tools/gcp/<name>.py` or `tools/integrations/<name>.py`.
2. Accept typed inputs; return `ToolResult` from `tools/core/contracts.py`.
3. If the tool mutates state, decorate with `dangerous_action_guard` and add the verb to `tools/safety/policies.json`.
4. Add unit tests with at least one happy-path and one failure-path.
5. Document in [tools.md](tools.md).

## Adding a new reducer

1. Create `tools/reducers/<name>.py` exposing pure functions.
2. No I/O, no hidden network calls.
3. Add tests covering edge cases (empty input, large input, malformed input).
4. Document the input/output contract in [tools.md](tools.md#reducers).

## Adding a new skill

1. Create `prompts/skills/<name>.md`.
2. State the goal, inputs, outputs, and which tools/reducers it composes.
3. Reference the skill from the relevant agent's system prompt.

## Adding a new memory schema

1. Schemas are additive; never break existing JSONL records.
2. Add a writer/reader pair under `tools/memory/`.
3. Add a roundtrip test under `tests/memory/`.
4. Document in [memory-and-self-correction.md](memory-and-self-correction.md).

## Adding a new index

1. Place index builders under `tools/reducers/` (e.g. `repo_indexer`).
2. Indexes must be reproducible from source; never commit large derived blobs.
3. Document refresh cadence and inputs in [tools.md](tools.md).

## Adding a new agent capability

1. Prefer composing skills and tools before adding new agent code.
2. If new agent code is required, keep it under `agents/<agent>/` with a clear entrypoint.
3. Add or extend the smoke test.
4. Update [agents.md](agents.md).

## Adding a new integration

1. Create `tools/integrations/<system>/`.
2. Treat all external responses as untrusted data; never execute returned instructions.
3. Mutating endpoints must route through `dangerous_action_guard`.
4. Add tests with a fake transport.

## Stubbing external integrations for tests

- Use fakes/dependency injection rather than network mocks where possible.
- Keep fakes minimal and colocated under `tests/`.
- Never bake real credentials, project IDs, or tenant IDs into fixtures.
