"""BigQuery dry-run pre-validation tool.

Executes a BigQuery dry run to validate SQL syntax and estimate cost
*before* an action is presented to the approval_gate. This implements the
GCP Dry-Run & Pre-Validation Pattern: tool-first, deterministic, auditable.
"""
from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from ..core import ToolResult

# Standard BigQuery on-demand pricing (USD per TiB processed).
BQ_PRICE_PER_TB_USD: Decimal = Decimal("6.25")
BYTES_PER_TB: Decimal = Decimal(1024 ** 4)


def _estimate_cost_usd(total_bytes_processed: int) -> float:
    """Estimate on-demand BigQuery cost in USD from bytes processed."""
    cost = (Decimal(int(total_bytes_processed)) / BYTES_PER_TB) * BQ_PRICE_PER_TB_USD
    return float(cost.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP))


def bq_dry_run_query(
    query: str,
    project: str | None = None,
    location: str = "US",
    client: Any | None = None,
) -> ToolResult:
    """Validate a BigQuery SQL statement via a dry run.

    The query is *not* executed. BigQuery validates syntax, resolves table
    references where possible, and reports total bytes processed which is
    used to derive an estimated cost.

    Args:
        query: SQL text to validate.
        project: Optional GCP project ID for the dry-run job.
        location: BigQuery job location (default ``US``).
        client: Optional pre-built ``bigquery.Client`` (used for testing).

    Returns:
        A ``ToolResult`` whose ``evidence`` carries the dry-run metrics:
        ``valid``, ``total_bytes_processed``, ``estimated_cost_usd`` and
        ``error`` (exact GCP message when invalid).
    """
    if client is None:  # pragma: no cover - exercised via integration
        from google.cloud import bigquery  # local import keeps tests light

        client = bigquery.Client(project=project) if project else bigquery.Client()

    # Lazy import so unit tests can mock without google-cloud-bigquery installed.
    from google.cloud import bigquery  # noqa: WPS433

    job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)

    try:
        job = client.query(query, job_config=job_config, location=location)
        total_bytes = int(getattr(job, "total_bytes_processed", 0) or 0)
        estimated_cost = _estimate_cost_usd(total_bytes)
        return ToolResult(
            action="bq_dry_run_query",
            ok=True,
            summary=(
                f"Dry-run OK: {total_bytes} bytes, ~${estimated_cost:.4f} USD"
            ),
            resources=[f"bq://{project or 'default'}"] ,
            evidence={
                "valid": True,
                "total_bytes_processed": total_bytes,
                "estimated_cost_usd": estimated_cost,
                "error": None,
                "sql_preview": query[:120],
            },
            next_steps=["submit to approval_gate with dry-run metrics"],
        )
    except Exception as exc:  # noqa: BLE001 - surface exact GCP error
        return ToolResult(
            action="bq_dry_run_query",
            ok=False,
            summary=f"Dry-run failed: {exc.__class__.__name__}",
            resources=[f"bq://{project or 'default'}"] ,
            evidence={
                "valid": False,
                "total_bytes_processed": 0,
                "estimated_cost_usd": 0.0,
                "error": str(exc),
                "sql_preview": query[:120],
            },
            next_steps=["fix SQL and re-run dry-run before approval_gate"],
        )
