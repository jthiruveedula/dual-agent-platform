"""Google Cloud Storage tool wrappers."""
from __future__ import annotations

from ..core import RiskLevel, ToolResult


def gcs_list(bucket: str, prefix: str = "") -> ToolResult:
    """List object names under a prefix. Returns counts and a small sample."""
    # TODO: integrate google.cloud.storage.Client.list_blobs
    return ToolResult(
        action="gcs_list",
        ok=True,
        summary=f"listed gs://{bucket}/{prefix}",
        resources=[f"gs://{bucket}/{prefix}"],
        evidence={"bucket": bucket, "prefix": prefix},
        next_steps=["open object", "filter by suffix"],
    )


def gcs_read_text(bucket: str, object_path: str, max_bytes: int = 65536) -> ToolResult:
    """Read up to ``max_bytes`` of a text object. Truncates to keep tokens low."""
    # TODO: integrate google.cloud.storage.Blob.download_as_text
    uri = f"gs://{bucket}/{object_path}"
    return ToolResult(
        action="gcs_read_text",
        ok=True,
        summary=f"read {uri} (truncated to {max_bytes}B)",
        resources=[uri],
        evidence={"uri": uri},
        next_steps=[],
    )


gcs_list.default_risk = RiskLevel.READ  # type: ignore[attr-defined]
gcs_read_text.default_risk = RiskLevel.READ  # type: ignore[attr-defined]
