"""Dangerous action guard.

A decorator-style helper that any tool wrapper can use to ensure a function
cannot run for a destructive verb without going through approval first.
"""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable

from tools.reducers.policy_guard import evaluate
from tools.safety.approval_gate import ApprovalDenied, require_approval


def guard(
    *,
    action: str,
    target_arg: str = "target",
    environment_arg: str = "environment",
    reason: str = "Tool-level guard",
    rollback_plan: str = "Manual revert required",
    validation_plan: str = "Smoke check after execution",
    blast_radius: str = "unknown",
    confirm: Callable | None = None,
) -> Callable:
    """Wrap a callable so it requires approval for destructive actions.

    The wrapped function MUST accept `target` and `environment` kwargs (or the
    names supplied via target_arg/environment_arg).
    """
    def _decorator(fn: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(fn)
        def _inner(*args: Any, **kwargs: Any) -> Any:
            target = kwargs.get(target_arg, "")
            environment = kwargs.get(environment_arg, "dev")
            decision = evaluate(action=action, target=target, environment=environment)
            if decision.requires_approval:
                # Will raise ApprovalDenied if the human says no.
                require_approval(
                    action=action,
                    target=target,
                    environment=environment,
                    reason=reason,
                    rollback_plan=rollback_plan,
                    validation_plan=validation_plan,
                    blast_radius=blast_radius,
                    confirm=confirm,
                )
            return fn(*args, **kwargs)
        return _inner
    return _decorator


__all__ = ["guard", "ApprovalDenied"]

