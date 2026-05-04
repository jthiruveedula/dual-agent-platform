# dual-agent-platform

Dual-agent platform combining a **GCP Data Engineering Agent** and a **Story Orchestration Agent** with a strict tool-first execution model, low token usage, and reusable orchestration patterns. Designed to work in Claude Code, Cursor, and GitHub Copilot via repository-level instructions and modular rule files.

## Core Operating Principle

Do NOT generate one-off Python programs for routine cloud or data engineering actions when an existing tool/function can be used. Prefer calling prebuilt Python tools and MCP integrations. Generate new code only when:

- a required capability does not exist,
- the user explicitly asks for a new tool, or
- the repository pattern requires a permanent implementation.

## Repository Layout

```
agents/
  gcp_data_engineering_agent/   # Agent 1 - GCP & data ops
  story_orchestration_agent/    # Agent 2 - SDLC orchestration
tools/
  core/                         # Shared contracts (ToolResult, RiskLevel, confirmation policy)
  gcp/                          # bq, gcs, logging, cloud_run, vertex, discovery_engine
  integrations/                 # jira, confluence, github, mcp
skills/                         # Reusable capability bundles
prompts/                        # System & sub-agent prompts
tests/                          # Unit tests for agents & tools
.cursor/rules/                  # Cursor rule files
.github/copilot-instructions.md # Copilot repo-level instructions
```

## Agent 1: GCP Data Engineering Agent

Domains: GCS, BigQuery, Cloud Logging, Cloud Run, Discovery Engine, Vertex AI, IAM-aware ops.

Rules:
- Use existing Python tool wrappers first.
- Treat tools as the execution boundary; the LLM is planner/interpreter.
- Return structured outputs: action, resources, summary, evidence, next steps.
- Risky operations require explicit confirmation. Prefer idempotent operations.

## Agent 2: Story Orchestration Agent

Connected systems: Jira, Confluence, Git/GitHub, MCP services, GCP Data Engineering Agent.

Responsibilities: read story → plan → delegate cloud ops → implement → test → collect evidence → PR → lower-env deploy → status updates.

## Tool-First Decision Policy

1. Does a tool already exist?
2. Can MCP or an approved integration handle this?
3. Is this a reusable capability worth adding to the shared tool layer?
4. Is ad hoc code truly necessary?

Default to tool usage over generated scripts.

## Safety Policy

- Confirmation required before destructive changes.
- Read-only / write / deploy / delete actions are distinguished via `RiskLevel`.
- Environment boundaries respected: `local`, `dev`, `qa`, `lower`, `prod`. Never assume prod access.

## Quickstart

```bash
pip install -e .
pytest -q
```

See `prompts/` for the system prompts, `.cursor/rules/` for Cursor configuration, and `.github/copilot-instructions.md` for Copilot.


## Platform Runtime: Architect + Builder

In addition to the GCP Data Engineering and Story Orchestration agents, this repo ships a generic safety-first dual-agent runtime:

- `agents/architect/` — plans a goal into structured steps, retrieves prior lessons, and routes risky steps to approval.
- `agents/builder/` — executes plan steps via the shared tool layer, gated by `policy_guard` -> `approval_gate` -> `dangerous_action_guard`.

```bash
python -m agents.architect --goal "Backfill BQ table x.y for last 7 days"
python -m agents.builder --plan plan.json
```

## Safety Stack

- `tools/reducers/policy_guard.py` — deterministic classifier (`evaluate`, `evaluate_action`, `classify_step`).
- `tools/safety/approval_gate.py` — surfaces an approval comment for human sign-off.
- `tools/safety/dangerous_action_guard.py` — decorator that blocks destructive ops without an approval token.
- `tools/safety/policies.json` — declarative policy table consumed by the guard.

Default policy semantics:

- Dataset-scope destructive ops (drop_dataset, delete_dataset) -> `deny`.
- Item-scope destructive ops (delete_table, truncate, alter, set-iam-policy) -> `allow` + `requires_approval=True`.
- Read/list/get/describe/query -> `allow`.
- Unknown verbs -> `allow` + `requires_approval=True` (fail-closed on intent).

## Memory (JSONL)

- `tools/memory/memory_store.py` — append-only JSONL store under `$DAP_MEMORY_DIR` (default `./memory/`).
- `tools/memory/lesson_writer.py` — `write_lesson(title, context, lesson, tags, store=...)`, `record_error(...)`.
- `tools/memory/lesson_retriever.py` — `retrieve_relevant(tags=..., limit=5, store=...)`, `should_block_repeat(signature, threshold=3)`.

Agents retrieve lessons before planning and write lessons on failure to avoid repeating known-broken paths.

## Reducers (token-efficient)

`tools/reducers/` provides pure functions used by both agents to keep prompt tokens low:
`policy_guard`, `approval_comment_builder`, `error_classifier`, `log_clusterer`, `repo_indexer`,
`resource_discovery`, `schema_fingerprint`, `sql_template_router`, `tool_cache`, `artifact_packager`.

## Tests & CI

- `tests/safety/test_policy_guard.py` — deny / approval / allow paths.
- `tests/memory/test_lesson_roundtrip.py` — JSONL write + retrieve.
- `tests/test_smoke_e2e.py` — Architect plan -> policy_guard -> Builder execute -> lesson persistence.
- `tests/test_core_contracts.py` — `tools.core.contracts` invariants.

CI (`.github/workflows/ci.yml`) runs `ruff check .` then `pytest -q` on every push.
