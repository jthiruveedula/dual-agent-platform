"""Tests for policy_guard reducer.

These tests rely only on the standard library and assert the public contract
of `evaluate_action`: deny > require_approval > allow.
"""
from __future__ import annotations

import importlib

import pytest

pg = importlib.import_module("tools.reducers.policy_guard")


def test_deny_action_is_blocked():
  result = pg.evaluate_action({"type": "bq.delete_dataset", "target": "x.y"})
  assert result["decision"] == "deny"


def test_require_approval_action():
  result = pg.evaluate_action({"type": "bq.delete_table", "target": "x.y.z"})
  assert result["decision"] == "allow"
  assert result["requires_approval"] is True


def test_allow_read_action():
  result = pg.evaluate_action({"type": "bq.read", "target": "x.y.z"})
  assert result["decision"] == "allow"
  assert result["requires_approval"] is False


def test_unknown_action_defaults_to_approval():
  result = pg.evaluate_action({"type": "unknown.weird_action", "target": ""})
  # Unknown actions should not be silently allowed
  assert result["decision"] in ("deny", "allow")
  if result["decision"] == "allow":
    assert result["requires_approval"] is True
