"""JSONL-backed memory store.

A tiny append-only store for lessons learned and error patterns.
This is the durable surface used by lesson_writer/lesson_retriever and by
agent self-correction modules.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Iterable, Iterator

from tools.memory.memory_models import ErrorPattern, Lesson

DEFAULT_MEMORY_DIR = Path(os.environ.get("DAP_MEMORY_DIR", "memory"))
LESSONS_FILE = "lessons_learned.jsonl"
ERRORS_FILE = "error_patterns.jsonl"


def _ensure(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()


def _append(path: Path, record: dict) -> None:
    _ensure(path)
    # Append-only writes keep the store crash-safe and easy to diff in git.
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def _read_all(path: Path) -> Iterator[dict]:
    if not path.exists():
        return iter(())
    def _gen() -> Iterator[dict]:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    yield json.loads(line)
                except json.JSONDecodeError:
                    # Skip malformed rows rather than crash the whole agent.
                    continue
    return _gen()


class MemoryStore:
    def __init__(self, base_dir: Path | str = DEFAULT_MEMORY_DIR) -> None:
        self.base_dir = Path(base_dir)
        self.lessons_path = self.base_dir / LESSONS_FILE
        self.errors_path = self.base_dir / ERRORS_FILE

    # --- Lessons ------------------------------------------------------
    def add_lesson(self, lesson: Lesson) -> None:
        _append(self.lessons_path, lesson.to_dict())

    def list_lessons(self) -> list[dict]:
        return list(_read_all(self.lessons_path))

    def search_lessons(self, *, tags: Iterable[str] = (), agent: str = "") -> list[dict]:
        wanted = {t.lower() for t in tags}
        out = []
        for row in _read_all(self.lessons_path):
            if agent and row.get("agent") != agent:
                continue
            if wanted and not wanted.intersection({t.lower() for t in row.get("tags", [])}):
                continue
            out.append(row)
        return out

    # --- Error patterns -----------------------------------------------
    def add_error(self, pattern: ErrorPattern) -> None:
        _append(self.errors_path, pattern.to_dict())

    def list_errors(self) -> list[dict]:
        return list(_read_all(self.errors_path))

    def find_error(self, signature: str) -> dict | None:
        latest: dict | None = None
        for row in _read_all(self.errors_path):
            if row.get("signature") == signature:
                latest = row
        return latest


__all__ = ["MemoryStore", "DEFAULT_MEMORY_DIR"]

