# ═══════════════════════════════════════════════════════════════════════
#  DAY 3: Lightweight RAG over historical supply-chain risk events
#         using ChromaDB as the vector store
# ═══════════════════════════════════════════════════════════════════════

from __future__ import annotations

# ── DAY 3 START: ChromaDB import with fallback ───────────────────────
try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False
# ── DAY 3 END (import) ──────────────────────────────────────────────

_client = None
_collection = None


# ── DAY 3 START: Index risk events into ChromaDB ─────────────────────

def init_risk_index(risk_events: list[dict]) -> None:
    """
    Build (or rebuild) a ChromaDB collection from a list of risk-event dicts.
    Each dict must have: event_id, event_type, severity, description,
    affected_suppliers, affected_region, event_date.
    """
    global _client, _collection

    if not CHROMA_AVAILABLE:
        print("[RAG] chromadb not installed — risk search will use basic text matching.")
        return

    _client = chromadb.Client()
    _collection = _client.get_or_create_collection(
        name="risk_events",
        metadata={"hnsw:space": "cosine"},
    )

    if _collection.count() > 0:
        return

    docs, metas, ids = [], [], []
    for ev in risk_events:
        doc = (
            f"{ev['event_type'].replace('_', ' ')}: {ev['description']} "
            f"Region: {ev.get('affected_region', 'unknown')}. "
            f"Suppliers: {ev.get('affected_suppliers', 'unknown')}."
        )
        docs.append(doc)
        metas.append({
            "severity": ev["severity"],
            "event_type": ev["event_type"],
            "region": ev.get("affected_region", ""),
            "date": str(ev["event_date"]),
        })
        ids.append(str(ev["event_id"]))

    _collection.add(documents=docs, metadatas=metas, ids=ids)
    print(f"[RAG] Indexed {len(docs)} risk events in ChromaDB.")

# ── DAY 3 END (indexing) ─────────────────────────────────────────────


# ── DAY 3 START: Semantic risk search ────────────────────────────────

def search_risks(query: str, n_results: int = 5) -> list[dict]:
    """
    Search the risk-event collection for events matching the query.
    Falls back to basic substring matching if ChromaDB is unavailable.
    """
    if CHROMA_AVAILABLE and _collection is not None and _collection.count() > 0:
        results = _collection.query(query_texts=[query], n_results=n_results)
        hits = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            dist = results["distances"][0][i] if results["distances"] else None
            hits.append({
                "event_id": results["ids"][0][i],
                "document": doc,
                "severity": meta.get("severity"),
                "event_type": meta.get("event_type"),
                "region": meta.get("region"),
                "date": meta.get("date"),
                "relevance_score": round(1 - (dist or 0), 3),
            })
        return hits

    return [{"message": "RAG index not available. Install chromadb and re-seed."}]

# ── DAY 3 END (search) ──────────────────────────────────────────────
