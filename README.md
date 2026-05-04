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
