"""Lesson writer.

Writes lessons learned and error patterns into the memory store. Called by
agent self-correction modules at the end of every run.
"""
from __future__ import annotations

from tools.memory.memory_models import ErrorPattern, Lesson
from tools.memory.memory_store import MemoryStore


def write_lesson(
    *,
    title: str,
    context: str,
    lesson: str,
    tags: list[str] | None = None,
    agent: str = "",
    store: MemoryStore | None = None,
) -> Lesson:
    rec = Lesson(
        title=title,
        context=context,
        lesson=lesson,
        tags=tags or [],
        agent=agent,
    )
    (store or MemoryStore()).add_lesson(rec)
    return rec


def record_error(
    *,
    signature: str,
    description: str,
    fix: str,
    agent: str = "",
    store: MemoryStore | None = None,
) -> ErrorPattern:
    rec = ErrorPattern(
        signature=signature,
        description=description,
        fix=fix,
        agent=agent,
    )
    (store or MemoryStore()).add_error(rec)
    return rec


__all__ = ["write_lesson", "record_error"]

