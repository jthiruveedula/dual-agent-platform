# GitHub Copilot Instructions — Dual-Agent Platform

This repo hosts two cooperating agents:
- `agents/gcp_data_engineering_agent/`: GCP data engineering execution.
- `agents/story_orchestration_agent/`: Jira/Confluence/GitHub SDLC orchestration.

## Tool-First Policy (HARD)
When suggesting code:
1. First search `tools/gcp/` and `tools/integrations/` for an existing function.
2. Reuse `tools/core/contracts.py` (`ToolResult`, `RiskLevel`, `PolicyDecision`).
3. Do NOT propose one-off scripts for routine GCP/SDLC actions.
4. Only propose new code when capability is missing or user explicitly requests it; place it under `tools/` as a permanent implementation.

## Style
- Python 3.11+, type hints, dataclasses, enums.
- Docstrings on public functions.
- Tests in `tests/` mirroring the source path.
- No secrets in code; use env vars / Secret Manager.

## Safety
- Risky ops (DELETE/DROP/OVERWRITE/force-merge) gated by `tools/core/policy.py` and require user confirmation.
- Default to dev/sandbox; never assume prod.

## Output Pattern
Return `ToolResult` with action, resources, summary, evidence, next_steps. Avoid long chain-of-thought. Cite resource IDs, not bodies.

