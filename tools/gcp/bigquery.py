"""BigQuery tool wrappers.

Replace mock bodies with google-cloud-bigquery client calls. The agent layer
should only ever call these public functions.
"""
from __future__ import annotations

from typing import Any

from ..core import RiskLevel, ToolResult


def bq_run_query(sql: str, project: str, location: str = "US") -> ToolResult:
    """Run a BigQuery SQL statement.

    Read-only by default. Mutating DML must be routed through a writer-tool
    that sets ``RiskLevel.WRITE`` and requires confirmation upstream.
    """
    # TODO: integrate google.cloud.bigquery.Client.query
    return ToolResult(
        action="bq_run_query",
        ok=True,
        summary=f"queued query in {project}/{location}",
        resources=[f"bq://{project}"],
        evidence={"sql_preview": sql[:120]},
        next_steps=["fetch results", "persist to table if needed"],
    )


def bq_describe_table(project: str, dataset: str, table: str) -> ToolResult:
    """Return schema, partitioning, clustering, and row count for a table."""
    # TODO: integrate google.cloud.bigquery.Client.get_table
    fqn = f"{project}.{dataset}.{table}"
    return ToolResult(
        action="bq_describe_table",
        ok=True,
        summary=f"described {fqn}",
        resources=[f"bq://{fqn}"],
        evidence={"table": fqn},
        next_steps=[],
    )


# Marker so the policy layer can introspect the default risk for this tool.
bq_run_query.default_risk = RiskLevel.READ  # type: ignore[attr-defined]
bq_describe_table.default_risk = RiskLevel.READ  # type: ignore[attr-defined]


def _unused(_: Any) -> None:  # pragma: no cover - silences linters when stubs unused
    return None
