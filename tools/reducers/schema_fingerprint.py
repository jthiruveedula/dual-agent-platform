"""Schema fingerprint reducer.

Reduces a verbose schema (e.g. a BigQuery table.schema) to a compact, stable
fingerprint plus a small structural summary the LLM can read cheaply.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class SchemaFingerprint:
    fingerprint: str
    column_count: int
    columns: tuple[tuple[str, str], ...]  # (name, type)

    def to_summary(self, max_cols: int = 25) -> str:
        head = self.columns[:max_cols]
        more = "" if len(self.columns) <= max_cols else f" (+{len(self.columns) - max_cols} more)"
        body = ", ".join(f"{n}:{t}" for n, t in head)
        return f"[{self.fingerprint}] cols={self.column_count} {body}{more}"


def _normalize(field: dict[str, Any]) -> tuple[str, str]:
    name = str(field.get("name", "")).strip().lower()
    ftype = str(field.get("type", field.get("field_type", ""))).strip().upper()
    mode = str(field.get("mode", "")).strip().upper()
    if mode and mode != "NULLABLE":
        ftype = f"{ftype}:{mode}"
    return name, ftype


def fingerprint(fields: Iterable[dict[str, Any]]) -> SchemaFingerprint:
    cols = tuple(sorted(_normalize(f) for f in fields if f.get("name")))
    payload = json.dumps(cols, sort_keys=True).encode("utf-8")
    digest = hashlib.sha1(payload).hexdigest()[:16]
    return SchemaFingerprint(fingerprint=digest, column_count=len(cols), columns=cols)


__all__ = ["SchemaFingerprint", "fingerprint"]

