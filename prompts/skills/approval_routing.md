# Skill: Approval Routing

Use before any mutating action. Goal: never mutate without explicit human approval.

## Procedure
1. Build an `Action` dict: `{type, target, payload, blast_radius}`.
2. Call `tools/reducers/policy_guard.py::evaluate_action(action)`.
   - If `decision == "deny"`: stop, surface reason.
   - If `decision == "allow"` and `requires_approval == false`: proceed.
   - Else: continue to step 3.
3. Call `tools/reducers/approval_comment_builder.py::build_comment(action, plan)` to format a concise human-readable approval request (≤ 200 words).
4. Call `tools/safety/approval_gate.py::request_approval(action, comment)` and **wait** for response.
5. If approved, call `tools/safety/dangerous_action_guard.py` decorator on the executor.
6. After execution, write outcome to `lesson_writer` with tag `approval_outcome`.

## Action types that ALWAYS require approval
- `bq.delete_table`, `bq.alter_schema`, `gcs.delete_object`, `iam.set_policy`
- `composer.deploy_dag`, `dataflow.cancel_job`, `billing.update`
- `git.push --force`, `git.delete_branch`, `pr.merge`
- Any `*.send`, `*.publish`, `*.email`, `*.post`

## Output
Return `{approved: bool, approver: str, reason: str, action_id: str}`.
