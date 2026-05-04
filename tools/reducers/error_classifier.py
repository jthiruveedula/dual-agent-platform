"""Error classifier reducer.

Maps a raw exception or error message into a stable signature plus a coarse
category. Stable signatures let memory.lesson_retriever detect repeated
failures and block retries.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

_CATEGORY_RULES: tuple[tuple[str, str], ...] = (
    (r"permission|forbidden|403|iam", "auth"),
    (r"not\s*found|404|does not exist", "missing_resource"),
    (r"quota|rate.?limit|429", "quota"),
    (r"timeout|deadline", "timeout"),
    (r"syntax|parse|invalid query", "sql_syntax"),
    (r"schema|column .* not found|type mismatch", "schema"),
    (r"network|connection|dns", "network"),
)

# Strip volatile bits (timestamps, ids, hex) so the same bug yields the same
# signature across runs.
_VOLATILE = re.compile(
    r"(?:\b[0-9a-f]{8,}\b|\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\S*|\b\d{6,}\b)",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ClassifiedError:
    signature: str
    category: str
    normalized: str


def classify(message: str) -> ClassifiedError:
    msg = (message or "").strip()
    normalized = _VOLATILE.sub("<X>", msg).lower()
    category = "unknown"
    for pattern, cat in _CATEGORY_RULES:
        if re.search(pattern, normalized):
            category = cat
            break
    digest = hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:16]
    return ClassifiedError(
        signature=f"{category}:{digest}",
        category=category,
        normalized=normalized,
    )


__all__ = ["ClassifiedError", "classify"]

