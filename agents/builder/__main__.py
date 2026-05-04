"""Builder agent CLI entrypoint.

Usage:
  python -m agents.builder --plan plan.json [--out report.json]

Reads a plan produced by the Architect, executes tasks through the safety stack,
and emits a per-task report.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.reducers.policy_guard import evaluate_action


def execute_task(task: dict) -> dict:
  action = {"type": task.get("action_type", "repo.read"), "target": task.get("id")}
  decision = evaluate_action(action)
  if decision["decision"] == "deny":
    return {"task_id": task["id"], "status": "denied", "reason": decision.get("reason")}
  if decision.get("requires_approval") and not task.get("approved"):
    return {"task_id": task["id"], "status": "awaiting_approval"}
  # Stub execution — real implementations should dispatch on tools[].
  return {
    "task_id": task["id"],
    "status": "completed",
    "tool_calls": task.get("tools", []),
    "artifacts": [],
    "next_action": None,
    "lessons": [],
  }


def run(plan: dict) -> dict:
  reports = [execute_task(t) for t in plan.get("tasks", [])]
  return {"goal": plan.get("goal"), "reports": reports}


def main(argv: list[str] | None = None) -> int:
  ap = argparse.ArgumentParser(prog="agents.builder")
  ap.add_argument("--plan", required=True)
  ap.add_argument("--out", default="-")
  args = ap.parse_args(argv)
  plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
  result = run(plan)
  text = json.dumps(result, indent=2)
  if args.out == "-":
    print(text)
  else:
    Path(args.out).write_text(text, encoding="utf-8")
  return 0


if __name__ == "__main__":
  sys.exit(main())
