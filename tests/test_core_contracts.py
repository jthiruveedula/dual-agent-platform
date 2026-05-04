"""Tests for tools.core.contracts and policy."""
from __future__ import annotations

import pytest

from tools.core.contracts import (
    Environment,
    OperationRequest,
    RiskLevel,
    ToolResult,
)
from tools.core.policy import PolicyDecision, evaluate


def test_tool_result_basic():
    r = ToolResult(
        action="bigquery.query",
        ok=True,
        summary="ok",
        resources=["project.dataset.table"],
        evidence={"job_id": "abc"},
        next_steps=["validate"],
    )
    assert r.action == "bigquery.query"
    assert r.ok is True
    assert "project.dataset.table" in r.resources
    assert r.evidence["job_id"] == "abc"
    d = r.to_dict()
    assert d["action"] == "bigquery.query"
    assert d["ok"] is True


def _req(risk: RiskLevel, confirmed: bool = False, env: Environment = Environment.DEV) -> OperationRequest:
    return OperationRequest(name="t", params={}, environment=env, risk=risk, confirmed=confirmed)


@pytest.mark.parametrize("risk,expected", [
    (RiskLevel.READ, True),
    (RiskLevel.WRITE, False),
    (RiskLevel.DELETE, False),
])
def test_policy_requires_confirmation(risk, expected):
    decision = evaluate(_req(risk=risk, confirmed=False))
    assert isinstance(decision, PolicyDecision)
    assert decision.allowed is expected


def test_policy_allows_when_confirmed():
    decision = evaluate(_req(risk=RiskLevel.DELETE, confirmed=True))
    assert decision.allowed is True


def test_policy_blocks_prod():
    decision = evaluate(_req(risk=RiskLevel.READ, confirmed=True, env=Environment.PROD))
    assert decision.allowed is False
    assert decision.requires_confirmation is True
