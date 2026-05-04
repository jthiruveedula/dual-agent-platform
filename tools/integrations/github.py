"""GitHub integration helpers — read-only by default; mutations are guarded.

Uses environment variable GITHUB_TOKEN. Never logs the token.
Lazy-imports requests so unit tests don’t need network deps.
"""
from __future__ import annotations

import os
from typing import Any

from tools.safety.dangerous_action_guard import dangerous_action_guard

_API = "https://api.github.com"


def _headers() -> dict[str, str]:
  token = os.environ.get("GITHUB_TOKEN", "")
  return {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {token}" if token else "",
    "X-GitHub-Api-Version": "2022-11-28",
  }


def get_repo(owner: str, repo: str) -> dict[str, Any]:
  import requests
  r = requests.get(f"{_API}/repos/{owner}/{repo}", headers=_headers(), timeout=15)
  r.raise_for_status()
  return r.json()


def list_issues(owner: str, repo: str, state: str = "open") -> list[dict]:
  import requests
  r = requests.get(
    f"{_API}/repos/{owner}/{repo}/issues",
    headers=_headers(), params={"state": state}, timeout=15,
  )
  r.raise_for_status()
  return r.json()


@dangerous_action_guard(action_type="pr.merge")
def merge_pr(owner: str, repo: str, number: int, method: str = "squash") -> dict:
  import requests
  r = requests.put(
    f"{_API}/repos/{owner}/{repo}/pulls/{number}/merge",
    headers=_headers(), json={"merge_method": method}, timeout=30,
  )
  r.raise_for_status()
  return r.json()


@dangerous_action_guard(action_type="git.delete_branch")
def delete_branch(owner: str, repo: str, branch: str) -> dict:
  import requests
  r = requests.delete(
    f"{_API}/repos/{owner}/{repo}/git/refs/heads/{branch}",
    headers=_headers(), timeout=15,
  )
  r.raise_for_status()
  return {"deleted": branch}
