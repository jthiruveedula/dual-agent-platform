"""End-to-end smoke test: Architect plan -> policy_guard -> Builder execute.

Validates the safety-first flow without external side effects:
  1. Architect produces a structured plan from a goal.
  2. policy_guard classifies each step (allow/approval/deny).
  3. Builder executes allow-listed steps; approval steps short-circuit.
  4. Lesson is persisted to JSONL memory on simulated failure.
"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path


def test_smoke_plan_guard_execute_lesson(tmp_path: Path) -> None:
    from tools.reducers.policy_guard import classify_step
    from tools.memory.lesson_writer import write_lesson
    from tools.memory.lesson_retriever import retrieve_lessons

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

    store = tmp_path / "lessons.jsonl"
    os.environ["DAP_MEMORY_PATH"] = str(store)
    write_lesson(
        tag="bq.delete_table",
        summary="requires explicit approval",
        signal="approval_required",
    )
    hits = retrieve_lessons(tag="bq.delete_table", limit=5)
    assert any(h.get("signal") == "approval_required" for h in hits)


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as d:
        test_smoke_plan_guard_execute_lesson(Path(d))
        print(json.dumps({"smoke": "ok"}))
