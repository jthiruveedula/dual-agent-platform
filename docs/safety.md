# Safety

This document is the canonical source for the dangerous-action policy and approval semantics. Code in `tools/safety/*` and `tools/reducers/policy_guard.py` implements it; this doc explains it.

## Goals

- Make destructive blast radius explicit, predictable, and auditable.
- Fail closed on ambiguous verbs.
- Require human sign-off before any item-scope destructive operation.
- Deny dataset-scope destructive operations outright.

## The safety chain

Every mutating tool call passes through:

1. **`policy_guard`** (`tools/reducers/policy_guard.py`) - deterministic classifier that returns one of `allow`, `requires_approval`, or `deny`.
2. **`approval_gate`** (`tools/safety/approval_gate.py`) - if `requires_approval`, surfaces a structured approval payload and blocks until a token is supplied.
3. **`dangerous_action_guard`** (`tools/safety/dangerous_action_guard.py`) - decorator that enforces the presence of a valid approval token at call time.

If any link is missing, the call is rejected.

## Policy table

`tools/safety/policies.json` is the declarative source of truth. Default semantics:

| Verb class | Scope | Default |
|---|---|---|
| `read`, `list`, `get`, `describe`, `query` | any | allow |
| `delete_table`, `truncate`, `alter`, `set-iam-policy` | item | allow + requires_approval |
| `drop_dataset`, `delete_dataset` | dataset | deny |
| unknown verb | any | allow + requires_approval (fail-closed on intent) |

Any new destructive verb **must** be added explicitly. Do not rely on the unknown-verb fallback in production.

## Destructive operation definitions

- **Item-scope destructive:** affects a single addressable resource (one table, one bucket, one IAM binding).
- **Dataset-scope destructive:** affects a container of resources (a dataset, a project, a folder).
- **Irreversible:** cannot be rolled back without a backup or restore step. Treat as dataset-scope by default.

## Blast-radius awareness

Before any risky step, the Architect must include in the plan:

- The verb and target resource(s)
- Estimated affected count
- Reversibility (yes/no/partial)
- Pre-action evidence (counts, schema fingerprint, last-modified)
- Rollback procedure if applicable

## Rollback expectations

- Tools that perform reversible mutations should expose a complementary undo or document the manual rollback.
- Where rollback is not possible, the plan must capture pre-action evidence so the change is auditable.

## Environment boundaries

`DAP_ENV` tags the environment: `local`, `dev`, `qa`, `lower`, `prod`. Builders never assume `prod`. Production execution requires both `DAP_ENV=prod` and a valid approval token; local fixtures must not grant either.

## Evidence requirements

- **Before** a risky action: pre-state snapshot (counts, schema fingerprint, IAM, last-modified).
- **After** a risky action: post-state snapshot, diff vs pre-state, success/failure summary.
- Evidence is attached to the lesson on failure and to the PR/story on success.

## Approval format

An approval payload looks like:

```json
{
  "action": "delete_table",
  "resource": "projects/p/datasets/d/tables/t",
  "scope": "item",
  "reversible": false,
  "reason": "backfill replacement",
  "pre_evidence": {"row_count": 1234567, "schema_fp": "sha256:..."},
  "requested_by": "architect",
  "env": "qa"
}
```

A human reviewer issues an approval token referencing the payload hash. Tokens are single-use and bound to the action.

## What never bypasses the gate

- Test fixtures.
- Retries.
- "Just one more cleanup step" inside a tool.
- Composite tools that internally call destructive verbs.

If you find a path that bypasses the gate, file a security report (see [SECURITY.md](../SECURITY.md)).
