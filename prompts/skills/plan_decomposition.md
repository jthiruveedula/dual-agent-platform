# Skill: Plan Decomposition

Use this skill to convert a high-level user goal into a dependency-ordered task graph.

## Steps
1. Restate the goal in one sentence; list explicit and implicit assumptions.
2. Call `repo_indexer` and (if cloud-related) `resource_discovery` to ground the plan.
3. Retrieve prior lessons via `lesson_retriever.search(goal_keywords)` and integrate.
4. Emit tasks of size ≤ 30 min each. Mark `requires_approval=true` for any of:
   - schema mutation, IAM change, resource create/delete, billing change
   - production data write, public publish, email/slack send, file delete
5. For each task, list `tools[]` with exact module paths from `tools/`.
6. Add `success_criteria` measurable per task (e.g., "row count matches", "dry-run plan empty").

## Output (JSON)
```json
{
  "goal": "...",
  "assumptions": ["..."],
  "tasks": [
    {"id": "T1", "title": "...", "agent": "builder", "tools": ["tools/gcp/bigquery.py"],
     "inputs": {}, "outputs": {}, "requires_approval": false, "depends_on": []}
  ],
  "risks": ["..."],
  "approval_required": false,
  "success_criteria": ["..."]
}
```

## Anti-patterns
- One mega-task that does everything
- Tasks that depend on undefined inputs
- Skipping approval flag on schema/IAM/billing changes
