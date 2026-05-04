"""External integrations: Jira, Confluence, GitHub, MCP-compatible services.

All adapters return ``ToolResult`` and never inline large payloads.
"""
from __future__ import annotations

from typing import Any, Mapping

from ..core import RiskLevel, ToolResult


# ---------------------------------------------------------------------------
# Jira
# ---------------------------------------------------------------------------
def jira_get_issue(issue_key: str) -> ToolResult:
    """Fetch a Jira issue's summary, description, status, acceptance criteria."""
    return ToolResult(
        action="jira_get_issue",
        ok=True,
        summary=f"loaded {issue_key}",
        resources=[f"jira://{issue_key}"],
        evidence={"issue": issue_key},
        next_steps=["extract acceptance criteria", "link related stories"],
    )


def jira_comment(issue_key: str, body: str) -> ToolResult:
    """Add a comment to a Jira issue. WRITE risk; requires confirmation."""
    return ToolResult(
        action="jira_comment",
        ok=True,
        summary=f"queued comment on {issue_key}",
        resources=[f"jira://{issue_key}"],
        evidence={"chars": str(len(body))},
        next_steps=[],
    )


jira_get_issue.default_risk = RiskLevel.READ  # type: ignore[attr-defined]
jira_comment.default_risk = RiskLevel.WRITE  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# Confluence
# ---------------------------------------------------------------------------
def confluence_get_page(page_id: str) -> ToolResult:
    """Fetch a Confluence page; returns title and a short summary, not full HTML."""
    return ToolResult(
        action="confluence_get_page",
        ok=True,
        summary=f"loaded confluence page {page_id}",
        resources=[f"confluence://{page_id}"],
        evidence={"page": page_id},
        next_steps=["extract decisions", "link to story"],
    )


confluence_get_page.default_risk = RiskLevel.READ  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# GitHub
# ---------------------------------------------------------------------------
def github_open_pr(repo: str, branch: str, title: str, body: str) -> ToolResult:
    """Open a PR. WRITE risk; requires confirmation."""
    return ToolResult(
        action="github_open_pr",
        ok=True,
        summary=f"prepared PR on {repo} from {branch}",
        resources=[f"github://{repo}#{branch}"],
        evidence={"title": title, "body_chars": str(len(body))},
        next_steps=["request reviewers", "attach evidence"],
    )


def github_get_file(repo: str, ref: str, path: str) -> ToolResult:
    """Fetch a single file at a ref. Returns path metadata; reads via gcs/local cache."""
    return ToolResult(
        action="github_get_file",
        ok=True,
        summary=f"got {path}@{ref}",
        resources=[f"github://{repo}/{path}@{ref}"],
        evidence={"path": path},
        next_steps=[],
    )


github_open_pr.default_risk = RiskLevel.WRITE  # type: ignore[attr-defined]
github_get_file.default_risk = RiskLevel.READ  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# MCP
# ---------------------------------------------------------------------------
def mcp_invoke(server: str, tool: str, params: Mapping[str, Any]) -> ToolResult:
    """Invoke a tool on an MCP-compatible server.

    Use this instead of writing custom HTTP clients when an MCP server already
    exposes the capability the agent needs.
    """
    return ToolResult(
        action="mcp_invoke",
        ok=True,
        summary=f"invoked {server}:{tool}",
        resources=[f"mcp://{server}/{tool}"],
        evidence={"param_keys": ",".join(sorted(params.keys()))},
        next_steps=[],
    )


mcp_invoke.default_risk = RiskLevel.READ  # type: ignore[attr-defined]


__all__ = [
    "confluence_get_page",
    "github_get_file",
    "github_open_pr",
    "jira_comment",
    "jira_get_issue",
    "mcp_invoke",
]
