# dual-agent-platform

Tool-first, safety-gated dual-agent platform for GCP data engineering and SDLC story orchestration. Designed to run inside Claude Code, Cursor, and GitHub Copilot via repository-level instructions, with an auditable Architect -> Builder runtime, deterministic policy guards, and a JSONL lesson memory.

## Why this exists

Most LLM agents regenerate ad hoc Python for every task. That is slow, expensive, unsafe, and impossible to audit. This repo enforces the opposite default: **call prebuilt, tested tools first; generate code only when no tool fits**. Risky operations are classified, gated, and logged.

## Key capabilities

- **Architect + Builder runtime** with structured plan handoff.
- **Domain agents**: GCP Data Engineering Agent and Story Orchestration Agent.
- **Deterministic safety stack**: `policy_guard` -> `approval_gate` -> `dangerous_action_guard`.
- **JSONL lesson memory** with retrieve-before-plan and write-on-failure.
- **Reducers** that compress prompts (schemas, logs, errors, repo indexes, SQL templates).
- **CI**: Ruff + pytest on every push.

## Architecture at a glance

Architect emits a plan; Builder executes each step through the safety chain (`policy_guard` -> `approval_gate` -> `dangerous_action_guard`) into the shared tool layer. Lessons flow back through `memory/` for retrieval on the next plan. Deeper detail: [docs/architecture.md](docs/architecture.md).

## Repository layout

```
agents/        # Architect, Builder, GCP DE Agent, Story Orchestration Agent
tools/
  core/        # Shared contracts (ToolResult, RiskLevel)
  gcp/         # bq, gcs, logging, cloud_run, vertex, discovery_engine
  integrations/# jira, confluence, github, mcp
  reducers/    # policy_guard, schema_fingerprint, log_clusterer, ...
  safety/      # approval_gate, dangerous_action_guard, policies.json
  memory/      # memory_store, lesson_writer, lesson_retriever
prompts/       # System and skill prompts
tests/         # safety, memory, smoke e2e, core contracts
.cursor/rules/ # Cursor rule files
.github/       # Copilot instructions, CI workflow
```

## Quickstart

```bash
pip install -e .
pytest -q
python -m agents.architect --goal "Backfill BQ table x.y for last 7 days"
python -m agents.builder   --plan plan.json
```

Full operational guide: [docs/usage.md](docs/usage.md).

## Safety and approval model

Every mutating action is classified by `policy_guard` and must pass `approval_gate` and `dangerous_action_guard`. Dataset-scope destructive ops are denied by default; item-scope destructive ops require approval; unknown verbs fail closed. See [docs/safety.md](docs/safety.md).

## Memory and self-correction

Agents retrieve relevant lessons before planning and write a lesson on every failure. Memory is append-only JSONL under `$DAP_MEMORY_DIR`. See [docs/memory-and-self-correction.md](docs/memory-and-self-correction.md).

## Development

- Local dev, lint, and test workflow: [docs/development.md](docs/development.md)
- Adding tools, reducers, skills, memory schemas, indexes, or agent capabilities: [docs/development.md](docs/development.md)
- Test strategy: [docs/testing.md](docs/testing.md)

## Documentation map

| Topic | Doc |
|---|---|
| Usage and commands | [docs/usage.md](docs/usage.md) |
| Architecture | [docs/architecture.md](docs/architecture.md) |
| Development | [docs/development.md](docs/development.md) |
| Safety and approvals | [docs/safety.md](docs/safety.md) |
| Memory and self-correction | [docs/memory-and-self-correction.md](docs/memory-and-self-correction.md) |
| Agents | [docs/agents.md](docs/agents.md) |
| Tools and reducers | [docs/tools.md](docs/tools.md) |
| Testing | [docs/testing.md](docs/testing.md) |
| Release process | [docs/release-process.md](docs/release-process.md) |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Large changes should start with a short design discussion in an issue before implementation.

## Status and roadmap

Pre-release. Public surface: Architect/Builder runtime, safety stack, memory store, reducers, GCP and integration tool wrappers (varying maturity). Roadmap and stubs are marked in [docs/architecture.md](docs/architecture.md).

## Security, support, conduct

- Vulnerability reporting: [SECURITY.md](SECURITY.md)
- Support channels: [SUPPORT.md](SUPPORT.md)
- Community standards: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)

## License

License intent not yet declared. Maintainer to confirm before public adoption.
