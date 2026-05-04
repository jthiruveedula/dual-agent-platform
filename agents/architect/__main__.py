"""Architect agent CLI entrypoint.

Usage:
  python -m agents.architect --goal "<goal>" [--out plan.json]

Produces a plan JSON to stdout (or to --out) using the Architect system prompt
and `plan_decomposition` skill. The actual LLM call is wired via core.contracts.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROMPT_PATH = Path(__file__).resolve().parents[2] / "prompts" / "system" / "architect.md"
SKILL_PATH = Path(__file__).resolve().parents[2] / "prompts" / "skills" / "plan_decomposition.md"


def _load_prompts() -> str:
  parts = []
  for p in (PROMPT_PATH, SKILL_PATH):
    if p.exists():
      parts.append(p.read_text(encoding="utf-8"))
  return "\n\n".join(parts)


def plan(goal: str) -> dict:
  """Return a stub plan structure. Replace `_call_llm` to wire a real model."""
  system = _load_prompts()
  # Stub plan — deterministic shape that downstream tools can validate.
  return {
    "goal": goal,
    "assumptions": [],
    "tasks": [
      {
        "id": "T1",
        "title": "Index repo and gather context",
        "agent": "builder",
        "tools": ["tools/reducers/repo_indexer.py"],
        "inputs": {"root": "."},
        "outputs": {"index": "output/index.json"},
        "requires_approval": False,
        "depends_on": [],
      }
    ],
    "risks": [],
    "approval_required": False,
    "success_criteria": ["plan validated against schema"],
    "_system_prompt_bytes": len(system),
  }


def main(argv: list[str] | None = None) -> int:
  ap = argparse.ArgumentParser(prog="agents.architect")
  ap.add_argument("--goal", required=True)
  ap.add_argument("--out", default="-")
  args = ap.parse_args(argv)
  result = plan(args.goal)
  text = json.dumps(result, indent=2)
  if args.out == "-":
    print(text)
  else:
    Path(args.out).write_text(text, encoding="utf-8")
  return 0


if __name__ == "__main__":
  sys.exit(main())
