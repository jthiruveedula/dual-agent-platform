"""Memory data models.

Lightweight, JSON-serializable records used by the lessons learned and error
pattern stores. We avoid pydantic on purpose to keep the dependency surface
small.
"""
from __future__ import annotations

import time
import uuid
from dataclasses import asdict, dataclass, field
from typing import Any


def _now() -> float:
    return time.time()


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


@dataclass
class Lesson:
    """A single lesson learned, written after a run completes."""

    title: str
    context: str
    lesson: str
    tags: list[str] = field(default_factory=list)
    agent: str = ""
    id: str = field(default_factory=_new_id)
    created_at: float = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ErrorPattern:
    """A recurring error signature with a known fix."""

    signature: str
    description: str
    fix: str
    occurrences: int = 1
    agent: str = ""
    id: str = field(default_factory=_new_id)
    last_seen: float = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


__all__ = ["Lesson", "ErrorPattern"]

