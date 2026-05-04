# Release Process

This document describes how releases are produced for the dual-agent platform. The repository is currently **pre-release** and this process is intentionally lightweight.

## Status

- The platform is pre-release.
- No formal versioned releases or packages have been published yet.
- Public adoption requires a declared license, which is still pending.

## Versioning

When formal releases begin, the platform will follow semantic versioning:

| Bump | Trigger |
| --- | --- |
| MAJOR | Breaking changes to tool contracts, safety semantics, or agent APIs. |
| MINOR | New tools, agents, reducers, or capabilities without breaking changes. |
| PATCH | Bug fixes, documentation, and non-behavioral changes. |

## Release readiness checklist

Before cutting a release:

1. All tests pass locally and in CI: `pytest -q`.
2. Lint is clean: `ruff check .`.
3. Safety policies (`tools/safety/policies.json`) reviewed.
4. Memory store contract unchanged or migration documented.
5. Documentation in `docs/` reflects current behavior.
6. CHANGELOG entry drafted (when CHANGELOG is introduced).

## Cutting a release

1. Ensure `main` is green.
2. Tag the commit with the target version, e.g. `v0.1.0`.
3. Push the tag.
4. Create a GitHub Release referencing the tag with summarized notes.

```bash
git tag v0.1.0
git push origin v0.1.0
```

## Release notes

GitHub Release notes should cover:

- New agents, tools, reducers, or guards.
- Changes to the safety chain or default policies.
- Changes to tool contracts (`ToolResult`, `RiskLevel`).
- Memory format or location changes.
- Documentation updates of note.

## Post-release

- Verify the tag and release are visible on GitHub.
- Confirm CI status on the released commit.
- Open follow-up issues for any deferred items.

## Related docs

- [`development.md`](development.md)
- [`testing.md`](testing.md)
- [`safety.md`](safety.md)
