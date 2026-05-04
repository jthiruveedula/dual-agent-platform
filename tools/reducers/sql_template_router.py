"""SQL template router.

Matches a free-form analytical request to a known parameterized SQL template.
Using templates instead of generated SQL keeps query shapes auditable and
lets policy_guard reason about whether DDL/DML is involved.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SqlTemplate:
    name: str
    description: str
    sql: str
    required_params: tuple[str, ...] = field(default_factory=tuple)
    is_ddl: bool = False


@dataclass(frozen=True)
class RouteResult:
    template: SqlTemplate
    sql: str
    missing_params: tuple[str, ...]


class SqlTemplateRouter:
    def __init__(self, templates: list[SqlTemplate] | None = None) -> None:
        self._templates: dict[str, SqlTemplate] = {}
        for t in templates or []:
            self.register(t)

    def register(self, template: SqlTemplate) -> None:
        self._templates[template.name] = template

    def list(self) -> list[SqlTemplate]:
        return list(self._templates.values())

    def route(self, name: str, params: dict[str, Any]) -> RouteResult:
        if name not in self._templates:
            raise KeyError(f"unknown SQL template: {name}")
        t = self._templates[name]
        missing = tuple(p for p in t.required_params if p not in params)
        # Format only when every required parameter is supplied.
        sql = t.sql.format(**params) if not missing else t.sql
        return RouteResult(template=t, sql=sql, missing_params=missing)


__all__ = ["SqlTemplate", "RouteResult", "SqlTemplateRouter"]

