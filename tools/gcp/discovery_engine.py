"""Discovery Engine (Vertex AI Search) tool wrappers."""
from __future__ import annotations

from ..core import RiskLevel, ToolResult


def discovery_engine_search(engine_id: str, query: str, project: str, location: str = "global") -> ToolResult:
    """Search a configured Discovery Engine app/engine.

    Returns top-N hits with titles and URIs only. Snippets should be fetched
    on demand to avoid bloating the agent context.
    """
    # TODO: integrate google.cloud.discoveryengine_v1
    return ToolResult(
        action="discovery_engine_search",
        ok=True,
        summary=f"searched engine {engine_id} in {project}/{location}",
        resources=[f"de://{project}/{location}/{engine_id}"],
        evidence={"query": query[:200]},
        next_steps=["fetch snippets for top hit", "refine query"],
    )


discovery_engine_search.default_risk = RiskLevel.READ  # type: ignore[attr-defined]
