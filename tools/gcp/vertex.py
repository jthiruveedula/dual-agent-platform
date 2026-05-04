"""Vertex AI inference tool wrappers."""
from __future__ import annotations

from typing import Any, Mapping

from ..core import RiskLevel, ToolResult


def vertex_infer(model: str, prompt: str, config: Mapping[str, Any] | None = None) -> ToolResult:
    """Run a Vertex AI generation request.

    The agent should pass only the minimum context required by ``model``.
    Long completions should be summarized rather than echoed back.
    """
    # TODO: integrate vertexai.generative_models.GenerativeModel
    cfg = dict(config or {})
    return ToolResult(
        action="vertex_infer",
        ok=True,
        summary=f"invoked {model} (prompt {len(prompt)} chars)",
        resources=[f"vertex://{model}"],
        evidence={"config_keys": ",".join(sorted(cfg.keys()))},
        next_steps=["summarize completion", "persist artifact"],
    )


vertex_infer.default_risk = RiskLevel.READ  # type: ignore[attr-defined]
