"""Shared contracts for the dual-agent platform.

Defines the stable types exchanged between agents and tools so that the LLM
layer can pass structured, low-token observations instead of raw payloads.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


class RiskLevel(str, Enum):
    READ = "read"
    WRITE = "write"
    DEPLOY = "deploy"
    DELETE = "delete"


class Environment(str, Enum):
    LOCAL = "local"
    DEV = "dev"
    QA = "qa"
    LOWER = "lower"
    PROD = "prod"


@dataclass(frozen=True)
class OperationRequest:
    """Canonical request passed to any tool wrapper."""

    name: str
    params: Mapping[str, Any]
    environment: Environment = Environment.DEV
    risk: RiskLevel = RiskLevel.READ
    confirmed: bool = False


@dataclass
class ToolResult:
    """Compact, structured tool result.

    Keep `summary` short (<=2 sentences) and put bulky data behind `evidence`
    references (paths, URIs, log links) rather than inlining content.
    """

    action: str
    ok: bool
    summary: str
    resources: Sequence[str] = field(default_factory=list)
    evidence: Mapping[str, str] = field(default_factory=dict)
    next_steps: Sequence[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "action": self.action,
            "ok": self.ok,
            "summary": self.summary,
            "resources": list(self.resources),
            "evidence": dict(self.evidence),
            "next_steps": list(self.next_steps),
            "error": self.error,
        }
