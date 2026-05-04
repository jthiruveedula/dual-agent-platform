"""Resource discovery reducer.

Compacts a verbose list of GCP resources (datasets, tables, buckets, services)
into a small decision packet for the agent.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class ResourceSummary:
    by_kind: dict[str, int]
    total: int
    samples: dict[str, list[str]]

    def to_text(self, max_samples: int = 5) -> str:
        lines = [f"total={self.total}"]
        for kind, count in sorted(self.by_kind.items(), key=lambda kv: -kv[1]):
            head = self.samples.get(kind, [])[:max_samples]
            lines.append(f"- {kind}: {count} (e.g. {', '.join(head)})")
        return "\n".join(lines)


def summarize(resources: Iterable[dict]) -> ResourceSummary:
    by_kind: Counter[str] = Counter()
    samples: dict[str, list[str]] = {}
    total = 0
    for r in resources:
        kind = str(r.get("kind", r.get("type", "unknown")))
        name = str(r.get("name", r.get("id", "")))
        by_kind[kind] += 1
        samples.setdefault(kind, []).append(name)
        total += 1
    return ResourceSummary(by_kind=dict(by_kind), total=total, samples=samples)


__all__ = ["ResourceSummary", "summarize"]

