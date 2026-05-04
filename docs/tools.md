# Tools and Reducers

This document describes the shared tool layer and reducers that power the dual-agent platform. The platform is **tool-first**: agents call prebuilt, testable Python tools before generating ad hoc code.

## Tool layout

All tools live under `tools/` and are organized by concern:

```text
tools/
  core/           # Shared contracts such as ToolResult and RiskLevel
  gcp/            # GCP service wrappers (bq, gcs, logging, cloud_run, vertex, discovery_engine)
  integrations/   # External systems (jira, confluence, github, mcp)
  reducers/       # Context compression utilities
  safety/         # approval_gate, dangerous_action_guard, policies.json
  memory/         # memory_store, lesson_writer, lesson_retriever
```

## Core contracts

Every tool returns a structured result so the Builder can reason about success, failure, and risk uniformly.

| Contract | Purpose |
| --- | --- |
| `ToolResult` | Standard return envelope for all tool calls. |
| `RiskLevel` | Classification used by safety guards to decide on approval and denial. |

## Tool groups

### GCP tools (`tools/gcp/`)

Wrappers around common Google Cloud services used by the GCP Data Engineering Agent:

- `bq` - BigQuery query, load, and metadata operations.
- `gcs` - Cloud Storage object and bucket operations.
- `logging` - Cloud Logging queries and structured log access.
- `cloud_run` - Cloud Run service inspection and invocation.
- `vertex` - Vertex AI access points.
- `discovery_engine` - Discovery Engine search and retrieval.

### Integrations (`tools/integrations/`)

External systems used by the Story Orchestration Agent and SDLC workflows:

- `jira` - Issue and story operations.
- `confluence` - Page reads and structured content retrieval.
- `github` - Repository, PR, and issue operations.
- `mcp` - Model Context Protocol bridge.

## Reducers

Reducers compress high-volume context before it is handed to the model. They keep prompts within budget and make planning more deterministic.

| Reducer | What it compresses |
| --- | --- |
| `policy_guard` | Evaluates planned actions against `policies.json`. |
| `schema_fingerprint` | Reduces large schema metadata to stable fingerprints. |
| `log_clusterer` | Clusters logs into representative samples. |

## Safety tools

Safety tools are not optional. Every mutating Builder step is routed through them in order:

1. `policy_guard` - policy evaluation against declared rules.
2. `approval_gate` - human approval requirement for item-scope destructive actions.
3. `dangerous_action_guard` - hard denial for dataset-scope destructive actions.

See [`safety.md`](safety.md) for the full safety model.

## Adding a new tool

1. Place the tool in the appropriate subfolder under `tools/`.
2. Return a `ToolResult` and assign an explicit `RiskLevel`.
3. Add tests under `tests/` covering both success and failure paths.
4. Run `pytest -q` and `ruff check` locally before opening a PR.

## Related docs

- [`architecture.md`](architecture.md)
- [`safety.md`](safety.md)
- [`agents.md`](agents.md)
