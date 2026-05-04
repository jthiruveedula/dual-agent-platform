"""GCP tool wrappers.

Each module exposes idempotent, structured operations returning ``ToolResult``.
Replace mock adapters with real google-cloud SDK calls in the implementation
layer; agent code should never call SDKs directly.
"""
from .bigquery import bq_describe_table, bq_run_query
from .cloud_run import cloud_run_deploy
from .discovery_engine import discovery_engine_search
from .gcs import gcs_list, gcs_read_text
from .logging import log_search
from .vertex import vertex_infer

__all__ = [
    "bq_describe_table",
    "bq_run_query",
    "cloud_run_deploy",
    "discovery_engine_search",
    "gcs_list",
    "gcs_read_text",
    "log_search",
    "vertex_infer",
]
