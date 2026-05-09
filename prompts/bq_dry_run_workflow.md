# BigQuery Dry-Run & Pre-Validation Workflow

This instruction is binding for both the **Architect** and the **Builder**
agents in the GCP Data Engineering track.

## Rule

If a task involves any BigQuery SQL operation (read or mutation), you MUST:

1. Call the prebuilt tool `tools.gcp.bq_dry_run.bq_dry_run_query` first.
2. Capture the dry-run evidence: `valid`, `total_bytes_processed`,
   `estimated_cost_usd`, and the exact `error` (if invalid).
3. If the dry-run is invalid, do NOT submit to `approval_gate`. Repair the
   SQL and re-run the dry-run.
4. For valid mutations (DML/DDL) or high-cost reads (>= 10 GiB scanned),
   route through `tools.safety.bq_pre_validate.bq_pre_validate_and_request_approval`.
   This embeds dry-run metrics into the approval payload's
   `validation_plan` so the reviewer sees:
   - validity
   - total bytes processed
   - estimated cost in USD
   - whether the action is mutating
   - whether it is a high-cost read
5. Only after approval is granted may the executing tool (e.g.
   `bq_run_query`) be invoked.

## Tool-First Reminder

Do not generate ad-hoc Python or shell to validate SQL. Use the
prebuilt dry-run tool. Generated code is the last resort and must still
pass `policy_guard`, `approval_gate`, and `dangerous_action_guard`.

## Approval Request Content

When presenting an approval request to a human or system reviewer,
include a one-line summary of the dry-run, e.g.:

> Dry-run OK: 1.0 TiB scanned, ~$6.25 USD estimated. Action: DELETE on
> `project.dataset.table`. Mutating: true.
