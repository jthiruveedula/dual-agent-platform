"""Approval gate.

Wraps the policy_guard decision with a human-in-the-loop confirmation step.
No destructive action should ever be executed without first passing through
this gate and receiving explicit approval.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

from tools.reducers.policy_guard import PolicyDecision, evaluate
from tools.reducers.approval_comment_builder import build_approval_comment


@dataclass
class ApprovalRequest:
    action: str
    target: str
    environment: str
    blast_radius: str
    reason: str
    rollback_plan: str
    validation_plan: str
    decision: PolicyDecision
    comment: str


class ApprovalDenied(Exception):
    """Raised when a required approval is not granted."""


def require_approval(
    *,
    action: str,
    target: str,
    environment: str,
    reason: str,
    rollback_plan: str,
    validation_plan: str,
    blast_radius: str = "unknown",
    confirm: Optional[Callable[[ApprovalRequest], bool]] = None,
) -> ApprovalRequest:
    """Build an ApprovalRequest and, if needed, run the confirm callback.

    The confirm callback is the integration point with the human reviewer.
    In tests it can be set to a deterministic stub. In production it should
    surface the approval comment to the user and wait for an explicit yes.
    """
    decision = evaluate(action=action, target=target, environment=environment)
    comment = build_approval_comment(
        action=action,
        target=target,
        environment=environment,
        blast_radius=blast_radius,
        reason=reason,
        rollback_plan=rollback_plan,
        validation_plan=validation_plan,
        decision=decision,
    )
    request = ApprovalRequest(
        action=action,
        target=target,
        environment=environment,
        blast_radius=blast_radius,
        reason=reason,
        rollback_plan=rollback_plan,
        validation_plan=validation_plan,
        decision=decision,
        comment=comment,
    )

    # Fast path: action is intrinsically safe.
    if not decision.requires_approval:
        return request

    if confirm is None:
        # Without a confirm hook we MUST refuse rather than silently proceed.
        raise ApprovalDenied(
            "Action requires approval but no confirm callback was provided."
        )
    if not confirm(request):
        raise ApprovalDenied(f"Approval denied for action '{action}' on '{target}'.")
    return request


__all__ = ["ApprovalRequest", "ApprovalDenied", "require_approval"]

