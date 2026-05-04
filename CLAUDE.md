# CLAUDE.md - AI-Assistant Operating Guide

This file is the durable instruction contract for Claude Code, Cursor, and Copilot working in this repository. It is intentionally **not** a project overview; for that read [README.md](README.md) and the [docs/](docs/) tree.

## Role

You are a senior contributor inside a tool-first, safety-gated dual-agent platform. Default to using existing tools, reducers, and skills. Generate new code only when no tool fits, the user explicitly asks, or a reusable pattern is needed.

## Repo invariants (do not violate)

1. **Never weaken safety.** Do not edit `tools/safety/*` or `tools/reducers/policy_guard.py` without an explicit user request and matching tests.
2. **Every mutating action must pass** `policy_guard` -> `approval_gate` -> `dangerous_action_guard`.
3. **Never log or persist secrets/PII.** Redact before writing to memory or evidence.
4. **Reducers over raw blobs.** Prefer summary IDs, schema fingerprints, and clustered logs.
5. **Write a lesson on every failure** via `tools/memory/lesson_writer.py`.
6. **Tests must pass** (`ruff check . && pytest -q`) before any commit affecting `tools/safety/*`, `tools/memory/*`, or agent runtimes.

## Source of truth map

| Concern | File |
|---|---|
| Project overview | `README.md` |
| AI-assistant rules (this file) | `CLAUDE.md` |
| Cursor rules | `.cursor/rules/` |
| Copilot rules | `.github/copilot-instructions.md` |
| Safety policy table | `tools/safety/policies.json` |
| System prompts | `prompts/system/` |
| Skills | `prompts/skills/` |

If these disagree, fix the disagreement in a single PR. Do not silently diverge.

## Edit discipline

- **Safe to edit freely:** `prompts/`, `docs/`, `tests/` (additive), `tools/integrations/*` (with tests).
- **Edit with care:** `agents/*`, `tools/gcp/*`, `tools/memory/*`, `tools/reducers/*`.
- **Do not edit without explicit instruction:** `tools/safety/*`, `tools/core/contracts.py`, `policies.json`.

## Documentation-as-code

Any change that alters public behavior, CLI flags, tool contracts, policy semantics, memory schema, or reducer outputs **must** update the relevant `docs/*.md` in the same PR. Examples in docs must match real code paths.

## Repo layout

- `agents/` - agent runtime entrypoints (architect, builder, gcp_data_engineering_agent, story_orchestration_agent)
- `prompts/system/` - system prompts (architect.md, builder.md, etc.)
- `prompts/skills/` - reusable skill recipes (plan_decomposition, approval_routing)
- `tools/reducers/` - token-saving summarizers (policy_guard, schema_fingerprint, etc.)
- `tools/safety/` - hard guardrails (approval_gate, dangerous_action_guard, policies.json)
- `tools/memory/` - lesson store (JSONL) + retriever
- `tools/gcp/` - GCP API wrappers (BigQuery, Composer, Dataflow, GCS, IAM)
- `tools/integrations/` - GitHub, Slack, Email, Jira, Confluence, MCP
- `tools/core/` - shared primitives (ToolResult, RiskLevel)
- `tests/` - unit + integration tests
- `.cursor/` - Cursor IDE rules

## Running

```bash
pip install -e .
python -m agents.architect --goal "<goal>"
python -m agents.builder   --plan plan.json
pytest -q
```

## Handoff contract

Architect emits a plan JSON -> Builder ingests -> Builder reports per-task JSON -> Architect reviews and either ships or replans. See [docs/agents.md](docs/agents.md).

## When uncertain

Stop and ask. Prefer a small, reviewable PR over a sweeping change. Do not bypass an approval gate "because the test fixture allows it".
