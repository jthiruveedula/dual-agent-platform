# CLAUDE.md — Dual-Agent Platform Operating Guide

This file orients Claude (or any LLM) working in this repo. Read it first.

## Repo Purpose
A dual-agent platform: an **Architect** plans, a **Builder** executes. Both share a tool layer (`tools/`) for safety, memory, GCP, integrations, and reducers.

## Top-level layout
- `agents/` – agent runtime entrypoints
- `prompts/system/` – system prompts (architect.md, builder.md, etc.)
- `prompts/skills/` – reusable skill recipes (plan_decomposition, approval_routing)
- `tools/reducers/` – token-saving summarizers (policy_guard, schema_fingerprint, etc.)
- `tools/safety/` – hard guardrails (approval_gate, dangerous_action_guard, policies.json)
- `tools/memory/` – lesson store (JSONL) + retriever
- `tools/gcp/` – GCP API wrappers (BigQuery, Composer, Dataflow, GCS, IAM)
- `tools/integrations/` – GitHub, Slack, Email
- `tools/core/` – shared primitives
- `tests/` – unit + integration tests
- `.cursor/` – Cursor IDE rules

## Non-negotiables
1. Never edit `tools/safety/*` to weaken checks.
2. Every mutating action must pass `policy_guard` → `approval_gate` → `dangerous_action_guard`.
3. Never log or persist secrets/PII. Redact before writing to memory.
4. Use reducers to keep token budgets small. Prefer summary IDs over inline blobs.
5. Write a lesson on every failure (`tools/memory/lesson_writer.py`).

## How agents call each other
Architect emits a plan JSON → Builder ingests → Builder reports per-task JSON → Architect reviews and either ships or replans.

## Running
- `pip install -e .`
- `python -m agents.architect --goal "<goal>"`
- `python -m agents.builder --plan plan.json`

## Testing
`pytest tests/ -q` — unit tests must pass before any commit affecting `tools/safety/*`.
