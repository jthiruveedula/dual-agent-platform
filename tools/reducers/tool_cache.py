"""Tool cache reducer.

A tiny TTL cache for tool outputs. Keeps repeated discovery / metadata calls
out of the LLM context and out of the wire to GCP.
"""
from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Any


@dataclass
class _Entry:
    value: Any
    expires_at: float


class ToolCache:
    def __init__(self, default_ttl: float = 300.0) -> None:
        self._store: dict[str, _Entry] = {}
        self.default_ttl = default_ttl

    @staticmethod
    def key_for(tool: str, params: dict) -> str:
        payload = json.dumps({"tool": tool, "params": params}, sort_keys=True, default=str)
        return hashlib.sha1(payload.encode("utf-8")).hexdigest()[:20]

    def get(self, key: str) -> Any | None:
        e = self._store.get(key)
        if not e:
            return None
        if e.expires_at < time.time():
            self._store.pop(key, None)
            return None
        return e.value

    def set(self, key: str, value: Any, ttl: float | None = None) -> None:
        self._store[key] = _Entry(value=value, expires_at=time.time() + (ttl or self.default_ttl))

    def clear(self) -> None:
        self._store.clear()


__all__ = ["ToolCache"]

