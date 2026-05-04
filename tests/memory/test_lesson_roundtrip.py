"""Round-trip test for lesson_writer + lesson_retriever using a temp JSONL store."""
from __future__ import annotations

import importlib
from pathlib import Path

store_mod = importlib.import_module("tools.memory.memory_store")
writer_mod = importlib.import_module("tools.memory.lesson_writer")
retriever_mod = importlib.import_module("tools.memory.lesson_retriever")


def test_write_and_retrieve(tmp_path: Path):
  store_path = tmp_path / "lessons.jsonl"
  store = store_mod.MemoryStore(path=str(store_path))
  writer_mod.write_lesson(
    store,
    title="BQ delete table requires approval",
    body="Always confirm before delete_table",
    tags=["bq", "approval"],
  )
  results = retriever_mod.search(store, query="delete_table", limit=5)
  assert len(results) >= 1
  assert any("delete" in r["title"].lower() for r in results)
