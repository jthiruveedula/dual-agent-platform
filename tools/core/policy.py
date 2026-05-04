"""Confirmation and environment policy enforcement.

The LLM proposes operations; this module decides whether they may execute
autonomously, must pause for explicit user confirmation, or must be refused
outright (e.g. prod access from a non-prod context).
"""
from __future__ import annotations

from dataclasses import dataclass

from .contracts import Environment, OperationRequest, RiskLevel

# Risk levels that must never auto-execute without explicit user confirmation.
_REQUIRES_CONFIRMATION: frozenset[RiskLevel] = frozenset(
    {RiskLevel.WRITE, RiskLevel.DEPLOY, RiskLevel.DELETE}
)

# Environments the agents are allowed to mutate without an extra escalation.
_AUTOMATABLE_ENVS: frozenset[Environment] = frozenset(
    {Environment.LOCAL, Environment.DEV, Environment.QA, Environment.LOWER}
)


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    requires_confirmation: bool
    reason: str


def evaluate(request: OperationRequest) -> PolicyDecision:
    """Evaluate whether the operation may proceed."""
    if request.environment is Environment.PROD:
        return PolicyDecision(
            allowed=False,
            requires_confirmation=True,
            reason="prod access is never assumed; route via change management",
        )

    if request.risk in _REQUIRES_CONFIRMATION and not request.confirmed:
        return PolicyDecision(
            allowed=False,
            requires_confirmation=True,
            reason=f"risk={request.risk.value} requires explicit confirmation",
        )

    if request.environment not in _AUTOMATABLE_ENVS:
        return PolicyDecision(
            allowed=False,
            requires_confirmation=True,
            reason=f"environment={request.environment.value} is not automatable",
        )

    return PolicyDecision(allowed=True, requires_confirmation=False, reason="ok")
