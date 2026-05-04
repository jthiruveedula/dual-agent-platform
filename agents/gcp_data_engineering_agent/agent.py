"""GCP Data Engineering Agent.

The LLM is the planner/interpreter; this module is a thin Python entry point
that dispatches operations through the shared tool layer and applies the
confirmation policy.
"""
from __future__ import annotations

from typing import Any, Callable, Mapping

from tools import gcp
from tools.core import OperationRequest, ToolResult, evaluate

# Stable, allow-listed dispatch table. New capabilities should be added here
# rather than via inline code generation.
_REGISTRY: Mapping[str, Callable[..., ToolResult]] = {
    "bq_run_query": gcp.bq_run_query,
    "bq_describe_table": gcp.bq_describe_table,
    "gcs_list": gcp.gcs_list,
    "gcs_read_text": gcp.gcs_read_text,
    "log_search": gcp.log_search,
    "cloud_run_deploy": gcp.cloud_run_deploy,
    "vertex_infer": gcp.vertex_infer,
    "discovery_engine_search": gcp.discovery_engine_search,
}


def list_tools() -> list[str]:
    """Return the allow-listed tool names available to the planner."""
    return sorted(_REGISTRY)


def execute(request: OperationRequest) -> ToolResult:
    """Dispatch ``request`` to the matching tool, enforcing policy first."""
    decision = evaluate(request)
    if not decision.allowed:
        return ToolResult(
            action=request.name,
            ok=False,
            summary="blocked by policy",
            error=decision.reason,
            next_steps=["obtain confirmation", "retry with confirmed=True"],
        )

    tool = _REGISTRY.get(request.name)
    if tool is None:
        return ToolResult(
            action=request.name,
            ok=False,
            summary="no such tool",
            error=f"unknown tool: {request.name}",
            next_steps=["add a permanent wrapper in tools/gcp/"]
        )

    try:
        return tool(**dict(request.params))
    except TypeError as exc:
        return ToolResult(
            action=request.name,
            ok=False,
            summary="bad arguments",
            error=str(exc),
            next_steps=["inspect tool signature"],
        )


def summarize(results: list[ToolResult]) -> dict[str, Any]:
    """Compact roll-up suitable for sending back to the orchestrator."""
    return {
        "ok": all(r.ok for r in results),
        "steps": len(results),
        "resources": sorted({r for res in results for r in res.resources}),
        "errors": [r.error for r in results if r.error],
    }
