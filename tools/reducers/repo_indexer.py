"""Repo indexer reducer.

Walks the repository, classifies files (tools, agents, prompts, skills, tests)
and emits a compact JSON map. The output is what `indexes/repo_map.json` is
rebuilt from; agents read this map instead of scanning the filesystem.
"""
from __future__ import annotations

import json
from pathlib import Path

_KIND_RULES: tuple[tuple[str, str], ...] = (
    ("tools/reducers/", "reducer"),
    ("tools/memory/", "memory"),
    ("tools/safety/", "safety"),
    ("tools/gcp/", "gcp_tool"),
    ("tools/integrations/", "integration"),
    ("tools/core/", "core"),
    ("agents/", "agent"),
    ("prompts/", "prompt"),
    ("skills/", "skill"),
    ("tests/", "test"),
    (".cursor/rules/", "cursor_rule"),
)

_SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", "output"}


def _classify(rel: str) -> str:
    for prefix, kind in _KIND_RULES:
        if rel.startswith(prefix):
            return kind
    if rel.endswith(".md"):
        return "doc"
    if rel.endswith(".py"):
        return "python"
    return "other"


def build_index(root: str | Path = ".") -> dict:
    root_path = Path(root).resolve()
    files: list[dict] = []
    for path in root_path.rglob("*"):
        if not path.is_file():
            continue
        if any(part in _SKIP_DIRS for part in path.parts):
            continue
        rel = path.relative_to(root_path).as_posix()
        files.append({"path": rel, "kind": _classify(rel), "size": path.stat().st_size})
    files.sort(key=lambda r: r["path"])
    by_kind: dict[str, int] = {}
    for f in files:
        by_kind[f["kind"]] = by_kind.get(f["kind"], 0) + 1
    return {"root": str(root_path), "file_count": len(files), "by_kind": by_kind, "files": files}


def write_index(out_path: str | Path, index: dict) -> None:
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text(json.dumps(index, indent=2), encoding="utf-8")


__all__ = ["build_index", "write_index"]

