"""Unit tests for the BigQuery dry-run pre-validation tool."""
from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock

import pytest


@pytest.fixture(autouse=True)
def _stub_bigquery(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Provide a stubbed ``google.cloud.bigquery`` module for tests."""
    fake_bq = types.ModuleType("bigquery")

    class _QueryJobConfig:
        def __init__(self, dry_run: bool = False, use_query_cache: bool = True) -> None:
            self.dry_run = dry_run
            self.use_query_cache = use_query_cache

    fake_bq.QueryJobConfig = _QueryJobConfig
    fake_bq.Client = MagicMock()

    fake_pkg = types.ModuleType("google")
    fake_cloud = types.ModuleType("google.cloud")
    fake_cloud.bigquery = fake_bq
    fake_pkg.cloud = fake_cloud

    monkeypatch.setitem(sys.modules, "google", fake_pkg)
    monkeypatch.setitem(sys.modules, "google.cloud", fake_cloud)
    monkeypatch.setitem(sys.modules, "google.cloud.bigquery", fake_bq)
    return fake_bq


def test_dry_run_success_returns_cost_metrics() -> None:
    from tools.gcp.bq_dry_run import bq_dry_run_query

    client = MagicMock()
    job = MagicMock()
    job.total_bytes_processed = 1024 ** 4  # 1 TiB
    client.query.return_value = job

    result = bq_dry_run_query("SELECT 1", project="p", client=client)

    assert result.ok is True
    assert result.evidence["valid"] is True
    assert result.evidence["total_bytes_processed"] == 1024 ** 4
    assert result.evidence["estimated_cost_usd"] == pytest.approx(6.25, rel=1e-3)
    assert result.evidence["error"] is None


def test_dry_run_syntax_error_surfaces_message() -> None:
    from tools.gcp.bq_dry_run import bq_dry_run_query

    client = MagicMock()
    client.query.side_effect = RuntimeError("Syntax error: Unexpected keyword SELEC")

    result = bq_dry_run_query("SELEC 1", project="p", client=client)

    assert result.ok is False
    assert result.evidence["valid"] is False
    assert "Syntax error" in result.evidence["error"]
    assert result.evidence["estimated_cost_usd"] == 0.0


def test_approval_payload_includes_dry_run_metrics() -> None:
    """The payload handed to approval_gate must carry dry-run cost data."""
    from tools.gcp.bq_dry_run import bq_dry_run_query

    client = MagicMock()
    job = MagicMock()
    job.total_bytes_processed = 5 * 1024 ** 3  # 5 GiB
    client.query.return_value = job

    dry = bq_dry_run_query("DELETE FROM ds.t WHERE TRUE", project="p", client=client)

    approval_payload = {
        "action": "bq_run_query",
        "sql": "DELETE FROM ds.t WHERE TRUE",
        "dry_run": dry.evidence,
    }

    assert approval_payload["dry_run"]["valid"] is True
    assert approval_payload["dry_run"]["total_bytes_processed"] == 5 * 1024 ** 3
    assert approval_payload["dry_run"]["estimated_cost_usd"] > 0
