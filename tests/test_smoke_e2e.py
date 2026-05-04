"""End-to-end smoke test: Architect plan -> policy_guard -> Builder execute.

Validates the safety-first flow without external side effects:
  1. policy_guard.classify_step labels each plan step (allow/approval/deny).
  2. Lessons round-trip via JSONL MemoryStore.
"""
from __future__ import annotations

from pathlib import Path

from tools.reducers.policy_guard import classify_step
from tools.memory.memory_store import MemoryStore
from tools.memory.lesson_writer import write_lesson
from tools.memory.lesson_retriever import retrieve_relevant


def test_smoke_plan_guard_execute_lesson(tmp_path: Path) -> None:
    plan = {
        "goal": "summarize bigquery dataset stats",
        "steps": [
            {"id": "s1", "tool": "bq.query", "args": {"sql": "SELECT 1"}},
            {"id": "s2", "tool": "bq.delete_table", "args": {"table": "x.y"}},
        ],
    }

    decisions = [classify_step(s) for s in plan["steps"]]
    assert decisions[0]["decision"] in {"allow", "approval"}
    assert decisions[1]["decision"] in {"approval", "deny"}

    store = MemoryStore(base_dir=tmp_path)
    write_lesson(
        title="bq.delete_table requires approval",
        context="safety/policy_guard",
        lesson="Always confirm before destructive BQ ops",
        tags=["bq", "approval"],
        store=store,
    )
    hits = retrieve_relevant(tags=["bq"], limit=5, store=store)
    assert any("approval" in h["title"].lower() for h in hits)
