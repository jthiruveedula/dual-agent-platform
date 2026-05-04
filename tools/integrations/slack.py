"""Slack integration helper. Posting requires approval per policies.json."""
from __future__ import annotations

import os

from tools.safety.dangerous_action_guard import dangerous_action_guard


@dangerous_action_guard(action_type="slack.post")
def post_message(channel: str, text: str) -> dict:
  """Post a message to a Slack channel using SLACK_BOT_TOKEN.

  Token is read from env and never logged.
  """
  import requests
  token = os.environ.get("SLACK_BOT_TOKEN", "")
  if not token:
    raise RuntimeError("SLACK_BOT_TOKEN not set")
  r = requests.post(
    "https://slack.com/api/chat.postMessage",
    headers={"Authorization": f"Bearer {token}"},
    json={"channel": channel, "text": text},
    timeout=15,
  )
  r.raise_for_status()
  data = r.json()
  if not data.get("ok"):
    raise RuntimeError(f"slack error: {data.get('error')}")
  return {"channel": channel, "ts": data.get("ts")}
