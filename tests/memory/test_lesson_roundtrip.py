"""Round-trip test for lesson_writer + lesson_retriever using a temp JSONL store."""
from __future__ import annotations

from pathlib import Path

from tools.memory.memory_store import MemoryStore
from tools.memory.lesson_writer import write_lesson
from tools.memory.lesson_retriever import retrieve_relevant


def test_write_and_retrieve(tmp_path: Path) -> None:
    store = MemoryStore(base_dir=tmp_path)
    write_lesson(
        title="BQ delete table requires approval",
        context="safety/policy_guard",
        lesson="Always confirm before delete_table",
        tags=["bq", "approval"],
        store=store,
    )
    results = retrieve_relevant(tags=["bq"], limit=5, store=store)
    assert len(results) >= 1
    assert any("delete" in r["title"].lower() for r in results)
