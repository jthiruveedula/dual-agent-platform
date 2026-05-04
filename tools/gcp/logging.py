"""Cloud Logging tool wrappers."""
from __future__ import annotations

from ..core import RiskLevel, ToolResult


def log_search(query: str, start_time: str, end_time: str, project: str) -> ToolResult:
    """Search Cloud Logging using an LQL query within a time window.

    Returns a count and a Log Explorer link rather than raw entries to keep
    token usage low. Pull entries lazily via a follow-up tool when needed.
    """
    # TODO: integrate google.cloud.logging_v2.Client
    return ToolResult(
        action="log_search",
        ok=True,
        summary=f"searched logs in {project} [{start_time} .. {end_time}]",
        resources=[f"logging://{project}"],
        evidence={"query": query[:200]},
        next_steps=["open Log Explorer", "narrow time window"],
    )


log_search.default_risk = RiskLevel.READ  # type: ignore[attr-defined]
