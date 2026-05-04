"""Policy guard reducer.

Evaluates a proposed action against a policy table and decides whether it can
proceed automatically, requires explicit human approval, or must be blocked.

This is intentionally a small, deterministic, dependency-free module so it can
be imported by any agent or tool wrapper without pulling in cloud SDKs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

# Verbs that always require an approval gate regardless of environment.
# Keep this list conservative: anything that destroys, mutates IAM, or
# changes production state must land here.
DESTRUCTIVE_VERBS: tuple[str, ...] = (
    "delete",
    "drop",
    "truncate",
    "overwrite",
    "force-overwrite",
    "rm-rf",
    "recursive-remove",
    "alter",
    "grant",
    "revoke",
    "set-iam-policy",
    "deploy-prod",
    "backfill",
)

HIGH_BLAST_RADIUS_ENVS: tuple[str, ...] = ("prod", "production", "prd")


@dataclass(frozen=True)
class PolicyDecision:
    """Outcome of a policy evaluation. `allow` means the action may run."""

    allow: bool
    requires_approval: bool
    reasons: tuple[str, ...] = field(default_factory=tuple)
    severity: str = "low"  # low | medium | high | critical


def _normalize(verb: str) -> str:
    return verb.strip().lower().replace("_", "-")


def evaluate(
    *,
    action: str,
    target: str,
    environment: str = "dev",
    extra_signals: Iterable[str] = (),
) -> PolicyDecision:
    """Decide whether `action` on `target` is safe.

    The function never executes anything. Callers MUST honor the returned
    decision: if requires_approval is True, an approval comment must be
    generated and confirmed before execution.
    """
    reasons: list[str] = []
    verb = _normalize(action)
    env = environment.strip().lower()

    is_destructive = any(verb.startswith(v) for v in DESTRUCTIVE_VERBS)
    is_prod = env in HIGH_BLAST_RADIUS_ENVS
    signals = {s.lower() for s in extra_signals}

    if is_destructive:
        reasons.append(f"verb '{verb}' is in DESTRUCTIVE_VERBS")
    if is_prod:
        reasons.append(f"environment '{env}' is high blast radius")
    if "large-scan" in signals or "large-backfill" in signals:
        reasons.append("operation flagged as large-scale")
    if "schema-change" in signals:
        reasons.append("operation alters schema")

    severity = "low"
    if is_destructive and is_prod:
        severity = "critical"
    elif is_destructive or is_prod:
        severity = "high"
    elif reasons:
        severity = "medium"

    requires_approval = bool(reasons)
    # We never auto-deny here; the caller pairs this with approval_gate.
    # `allow` is True only when no risk reasons were found.
    return PolicyDecision(
        allow=not requires_approval,
        requires_approval=requires_approval,
        reasons=tuple(reasons),
        severity=severity,
    )


__all__ = ["PolicyDecision", "evaluate", "DESTRUCTIVE_VERBS"]

