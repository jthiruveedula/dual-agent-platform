"""BigQuery pre-validation gateway.

This module enforces the GCP Dry-Run & Pre-Validation Pattern: any
BigQuery action classified as a *mutation* or *high-cost read* MUST be
passed through ``bq_pre_validate_and_request_approval`` before reaching
the approval_gate. The dry-run metrics (validity, bytes processed,
estimated cost) are embedded into the approval payload so that the
human/system reviewer sees risk and cost up-front.
"""
from __future__ import annotations

import json
from typing import Any, Callable, Optional

from tools.core import ToolResult
from tools.gcp.bq_dry_run import bq_dry_run_query

# Default high-cost threshold: 10 GiB scanned for read-only queries.
HIGH_COST_READ_THRESHOLD_BYTES: int = 10 * 1024 ** 3

_MUTATING_PREFIXES: tuple[str, ...] = (
    "INSERT",
    "UPDATE",
    "DELETE",
    "MERGE",
    "CREATE",
    "DROP",
    "ALTER",
    "TRUNCATE",
)


def is_mutating_bq_query(sql: str) -> bool:
    """Return True if the SQL begins with a DML/DDL keyword."""
    return sql.lstrip().upper().startswith(_MUTATING_PREFIXES)


def requires_pre_validation(sql: str) -> bool:
    """Conservative classifier: every BQ action passes through dry-run."""
    _ = sql
    return True


def bq_pre_validate_and_request_approval(
    *,
    sql: str,
    project: str,
    target: str,
    environment: str,
    reason: str,
    rollback_plan: str,
    require_approval_fn: Callable[..., Any],
    location: str = "US",
    client: Optional[Any] = None,
    bytes_threshold: int = HIGH_COST_READ_THRESHOLD_BYTES,
) -> ToolResult:
    """Run BigQuery dry-run, then submit an approval request enriched
    with the dry-run metrics serialized into ``validation_plan``.
    """
    dry = bq_dry_run_query(sql, project=project, location=location, client=client)

    if not dry.ok or not dry.evidence.get("valid", False):
        return ToolResult(
            action="bq_pre_validate",
            ok=False,
            summary="Dry-run failed; not forwarding to approval_gate.",
            resources=[f"bq://{project}"],
            evidence={"dry_run": dry.evidence},
            next_steps=["fix SQL and re-run pre-validation"],
        )

    total_bytes = int(dry.evidence["total_bytes_processed"])
    estimated_cost = float(dry.evidence["estimated_cost_usd"])
    mutating = is_mutating_bq_query(sql)
    high_cost_read = (not mutating) and total_bytes >= bytes_threshold
    blast_radius = "high" if mutating else ("medium" if high_cost_read else "low")

    validation_plan = json.dumps(
        {
            "dry_run": {
                "valid": True,
                "total_bytes_processed": total_bytes,
                "estimated_cost_usd": estimated_cost,
                "mutating": mutating,
                "high_cost_read": high_cost_read,
            }
        },
        sort_keys=True,
    )

    decision = require_approval_fn(
        action="bq_run_query",
        target=target,
        environment=environment,
        blast_radius=blast_radius,
        reason=reason,
        rollback_plan=rollback_plan,
        validation_plan=validation_plan,
    )

    return ToolResult(
        action="bq_pre_validate",
        ok=True,
        summary=(
            f"Dry-run OK ({total_bytes} bytes, ~${estimated_cost:.4f}); "
            f"approval decision attached."
        ),
        resources=[f"bq://{project}"],
        evidence={
            "dry_run": dry.evidence,
            "approval_decision": getattr(decision, "__dict__", {"decision": str(decision)}),
        },
        next_steps=["execute query if approved"],
    )

