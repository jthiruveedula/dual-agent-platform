"""Approval comment builder.

Produces the human-readable approval request that must accompany every
destructive or high-blast-radius action. The format is intentionally rigid
so reviewers can scan it quickly.
"""
from __future__ import annotations

from tools.reducers.policy_guard import PolicyDecision

_TEMPLATE = """\
## Approval Required

- **Action:** {action}
- **Target:** {target}
- **Environment:** {environment}
- **Severity:** {severity}
- **Blast radius:** {blast_radius}

### Reason
{reason}

### Rollback plan
{rollback_plan}

### Validation plan
{validation_plan}

### Policy reasons
{policy_reasons}

Reply `approve` to proceed or `deny` to abort.
"""


def build_approval_comment(
    *,
    action: str,
    target: str,
    environment: str,
    blast_radius: str,
    reason: str,
    rollback_plan: str,
    validation_plan: str,
    decision: PolicyDecision,
) -> str:
    policy_reasons = "\n".join(f"- {r}" for r in decision.reasons) or "- (none)"
    return _TEMPLATE.format(
        action=action,
        target=target,
        environment=environment,
        severity=decision.severity,
        blast_radius=blast_radius,
        reason=reason.strip(),
        rollback_plan=rollback_plan.strip(),
        validation_plan=validation_plan.strip(),
        policy_reasons=policy_reasons,
    )


__all__ = ["build_approval_comment"]

