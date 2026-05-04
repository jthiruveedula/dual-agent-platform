"""Tests for tools.core.contracts and policy."""
from __future__ import annotations

import pytest

from tools.core.contracts import ToolResult, RiskLevel
from tools.core.policy import PolicyDecision, evaluate


def test_tool_result_basic():
    r = ToolResult(
        action="bigquery.query",
        resources=["project.dataset.table"],
        summary="ok",
        evidence={"job_id": "abc"},
        next_steps=["validate"],
    )
    assert r.action == "bigquery.query"
    assert "project.dataset.table" in r.resources
    assert r.evidence["job_id"] == "abc"


@pytest.mark.parametrize("risk,expected", [
    (RiskLevel.READ, True),
    (RiskLevel.WRITE, False),
    (RiskLevel.DELETE, False),
])
def test_policy_requires_confirmation(risk, expected):
    decision = evaluate(risk=risk, confirmed=False)
    assert isinstance(decision, PolicyDecision)
    assert decision.allowed is expected


def test_policy_allows_when_confirmed():
    decision = evaluate(risk=RiskLevel.DELETE, confirmed=True)
    assert decision.allowed is True

