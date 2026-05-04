"""Lesson retriever.

Reads back relevant lessons before an agent executes. Designed to surface a
small, ranked subset to keep prompt tokens low.
"""
from __future__ import annotations

from tools.memory.memory_store import MemoryStore

MAX_LESSONS = 5


def retrieve_relevant(
    *,
    tags: list[str] | None = None,
    agent: str = "",
    limit: int = MAX_LESSONS,
    store: MemoryStore | None = None,
) -> list[dict]:
    """Return up to `limit` recent matching lessons, newest first."""
    s = store or MemoryStore()
    rows = s.search_lessons(tags=tags or [], agent=agent)
    rows.sort(key=lambda r: r.get("created_at", 0), reverse=True)
    return rows[:limit]


def should_block_repeat(
    signature: str,
    *,
    threshold: int = 3,
    store: MemoryStore | None = None,
) -> bool:
    """Return True if this error signature has been seen >= threshold times.

    Used by self-correction modules to refuse to retry a known-broken path
    until a human updates the recorded fix.
    """
    s = store or MemoryStore()
    count = sum(1 for r in s.list_errors() if r.get("signature") == signature)
    return count >= threshold


__all__ = ["retrieve_relevant", "should_block_repeat", "MAX_LESSONS"]

