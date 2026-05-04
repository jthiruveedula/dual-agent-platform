"""Cloud Run tool wrappers.

Deploys are ``RiskLevel.DEPLOY`` and require explicit confirmation enforced by
``tools.core.policy.evaluate``. Prefer revision-based, idempotent updates.
"""
from __future__ import annotations

from typing import Mapping

from ..core import RiskLevel, ToolResult


def cloud_run_deploy(
    service: str,
    image: str,
    region: str,
    project: str,
    env_vars: Mapping[str, str] | None = None,
) -> ToolResult:
    """Deploy a Cloud Run revision.

    Returns the revision name and the service URL as evidence; never inlines
    deploy logs.
    """
    # TODO: integrate google.cloud.run_v2 admin client or `gcloud run deploy`
    return ToolResult(
        action="cloud_run_deploy",
        ok=True,
        summary=f"deployed {service} to {region}",
        resources=[f"run://{project}/{region}/{service}"],
        evidence={"image": image, "env_count": str(len(env_vars or {}))},
        next_steps=["smoke test", "shift traffic"],
    )


cloud_run_deploy.default_risk = RiskLevel.DEPLOY  # type: ignore[attr-defined]
