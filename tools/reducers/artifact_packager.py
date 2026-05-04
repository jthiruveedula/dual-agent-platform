"""Artifact packager: bundle agent run outputs into a compact JSON manifest.

Produces a token-efficient summary artifact for downstream agents instead of
passing raw verbose outputs around.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any


def _digest(text: str) -> str:
  return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def package_artifact(
  run_id: str,
  agent: str,
  outputs: dict[str, Any],
  out_dir: str | Path = "output/artifacts",
) -> dict:
  """Persist a compact manifest and return its summary.

  outputs may contain large strings; we store them as files and keep digests
  + sizes in the manifest to keep the in-memory representation small.
  """
  out_root = Path(out_dir) / run_id
  out_root.mkdir(parents=True, exist_ok=True)
  files: list[dict] = []
  for name, value in outputs.items():
    if isinstance(value, (dict, list)):
      payload = json.dumps(value, indent=2)
      ext = "json"
    else:
      payload = str(value)
      ext = "txt"
    fpath = out_root / f"{name}.{ext}"
    fpath.write_text(payload, encoding="utf-8")
    files.append({
      "name": name,
      "path": str(fpath),
      "bytes": len(payload.encode("utf-8")),
      "sha256_12": _digest(payload),
    })
  manifest = {
    "run_id": run_id,
    "agent": agent,
    "created_at": int(time.time()),
    "files": files,
  }
  (out_root / "manifest.json").write_text(
    json.dumps(manifest, indent=2), encoding="utf-8"
  )
  return manifest
