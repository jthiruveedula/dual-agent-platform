"""Log clusterer reducer.

Groups noisy log lines (e.g. from Cloud Logging) into a small set of
templated buckets. Designed to fit a multi-thousand-line log dump into a
handful of summary rows safely consumable by the LLM.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass
from typing import Iterable

_PLACEHOLDERS = (
    (re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}\S*"), "<TS>"),
    (re.compile(r"\b[0-9a-f]{8,}\b", re.I), "<HEX>"),
    (re.compile(r"\b\d{4,}\b"), "<N>"),
    (re.compile(r"https?://\S+"), "<URL>"),
    (re.compile(r"/[\w\-./]+"), "<PATH>"),
)


@dataclass(frozen=True)
class LogCluster:
    template: str
    count: int
    sample: str


def _templatize(line: str) -> str:
    out = line.strip()
    for pattern, repl in _PLACEHOLDERS:
        out = pattern.sub(repl, out)
    return out


def cluster(lines: Iterable[str], *, top_k: int = 20) -> list[LogCluster]:
    samples: dict[str, str] = {}
    counts: Counter[str] = Counter()
    for raw in lines:
        if not raw:
            continue
        tmpl = _templatize(raw)
        counts[tmpl] += 1
        samples.setdefault(tmpl, raw.strip())
    return [
        LogCluster(template=t, count=c, sample=samples[t])
        for t, c in counts.most_common(top_k)
    ]


__all__ = ["LogCluster", "cluster"]

