"""
src/rag/index_builder.py
─────────────────────────
Section 8 of the Implementation Guide: Embeddings and Vector Indexing.

Handles:
  - rebuild_collection()   : delete + recreate a named Chroma collection
  - upsert_documents()     : batch upsert from a list of document dicts
  - load_jsonl()           : load processed JSONL records into memory
  - save_jsonl()           : save document dicts to a JSONL file

These utilities are shared between build_rag_index.py (offline) and tests.
"""

from __future__ import annotations

import json
from pathlib import Path

import chromadb

BATCH_SIZE = 200


def rebuild_collection(
    chroma_client: chromadb.ClientAPI,
    collection_name: str,
    embedding_function,
) -> chromadb.Collection:
    """
    Delete a collection if it exists and recreate it.

    Called when processing rules change (guide Section 8, Step 4).
    """
    try:
        chroma_client.delete_collection(collection_name)
    except Exception:
        pass
    return chroma_client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function,
    )


def batch_items(items: list, batch_size: int = BATCH_SIZE):
    """Yield successive slices of `items` of size `batch_size`."""
    for start in range(0, len(items), batch_size):
        yield items[start : start + batch_size]


def upsert_documents(
    collection: chromadb.Collection,
    items: list[dict],
) -> None:
    """
    Batch-upsert document dicts into a Chroma collection.

    Each dict must have keys: id, document, metadata.
    """
    for batch in batch_items(items, BATCH_SIZE):
        collection.upsert(
            ids=[item["id"] for item in batch],
            documents=[item["document"] for item in batch],
            metadatas=[item["metadata"] for item in batch],
        )


def save_jsonl(records: list[dict], path: Path) -> None:
    """Persist a list of document dicts to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=True) + "\n")
    print(f"  Saved {len(records):,} records → {path}")


def load_jsonl(path: Path) -> list[dict]:
    """Load document dicts from a JSONL file."""
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records
