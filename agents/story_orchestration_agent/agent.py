"""Story Orchestration Agent.

Reads stories from Jira/Confluence, plans subtasks, delegates cloud/data
operations to the GCP Data Engineering Agent, implements code, runs tests,
collects evidence, and prepares PRs.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Sequence

from agents.gcp_data_engineering_agent import agent as gcp_agent
from tools.core import OperationRequest, ToolResult
from tools import integrations


class Phase(str, Enum):
    PLAN = "plan"
    IMPLEMENT = "implement"
    VALIDATE = "validate"
    EVIDENCE = "evidence"
    DELIVER = "deliver"


@dataclass(frozen=True)
class Subtask:
    phase: Phase
    title: str
    depends_on: tuple[str, ...] = ()


@dataclass
class Plan:
    story_key: str
    subtasks: list[Subtask] = field(default_factory=list)
    clarifications: list[str] = field(default_factory=list)


_REQUIRED_INPUTS = ("story_key", "repo")


def build_plan(story_key: str, repo: str | None = None) -> Plan:
    """Produce an ordered subtask plan or a list of clarification questions."""
    plan = Plan(story_key=story_key)
    if not story_key:
        plan.clarifications.append("Provide the Jira story key (e.g. ABC-123).")
    if not repo:
        plan.clarifications.append("Provide the target repository (org/name).")
    if plan.clarifications:
        return plan

    plan.subtasks = [
        Subtask(Phase.PLAN, "load story and acceptance criteria"),
        Subtask(Phase.PLAN, "gather code context", depends_on=("load story and acceptance criteria",)),
        Subtask(Phase.IMPLEMENT, "apply code changes", depends_on=("gather code context",)),
        Subtask(Phase.VALIDATE, "run unit tests", depends_on=("apply code changes",)),
        Subtask(Phase.VALIDATE, "run lower-env integration", depends_on=("run unit tests",)),
        Subtask(Phase.EVIDENCE, "collect logs and outputs", depends_on=("run lower-env integration",)),
        Subtask(Phase.DELIVER, "open PR with summary", depends_on=("collect logs and outputs",)),
    ]
    return plan


def intake(story_key: str) -> ToolResult:
    """Pull the story; the LLM uses the summary to seed planning."""
    return integrations.jira_get_issue(story_key)


def delegate_gcp(name: str, **params) -> ToolResult:
    """Delegate a single GCP operation to Agent 1."""
    return gcp_agent.execute(OperationRequest(name=name, params=params))


def status_report(story_key: str, results: Sequence[ToolResult]) -> dict:
    """Compact, dual-audience status payload."""
    ok = all(r.ok for r in results)
    return {
        "story": story_key,
        "status": "green" if ok else "red",
        "engineer": gcp_agent.summarize(list(results)),
        "business": (
            f"Story {story_key} is {'on track' if ok else 'blocked'}; "
            f"{len(results)} steps executed."
        ),
    }
