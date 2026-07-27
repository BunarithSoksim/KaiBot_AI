"""
Ingestion pipeline: raw agricultural documents -> chunks -> embeddings ->
ChromaDB collection.

Design notes for the Cambodia-specific knowledge base:
- Each chunk keeps metadata (source, crop, province, topic) so retrieval
  can be filtered later (e.g. "only Preah Vihear rice content") once the
  July 29 event tells us which filters actually matter.
- Chunk size is kept small (roughly one idea per chunk) because farmer
  questions tend to be narrow ("how much fertilizer for rice at 30 days")
  rather than broad, and small chunks retrieve more precisely for that.
"""
import json
import uuid
from pathlib import Path

import chromadb

from config import settings, CHROMA_PERSIST_DIR, SAMPLE_DOCS_DIR
from rag.embeddings import get_embedder

COLLECTION_NAME = "kaibot_agri_knowledge"


def chunk_text(text: str, max_chars: int = 400, overlap: int = 50) -> list[str]:
    """
    Simple sliding-window chunker by character count. Khmer has no
    whitespace word boundaries in the way English does, so naive
    word-splitting is unreliable -- character-window chunking with overlap
    is a safer default until a proper Khmer sentence/word segmenter
    (e.g. khmer-nltk, or a segmentation model) is wired in.
    """
    text = text.strip()
    if len(text) <= max_chars:
        return [text] if text else []

    chunks = []
    start = 0
    while start < len(text):
        end = min(start + max_chars, len(text))
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = end - overlap
    return [c for c in chunks if c]


def load_sample_documents() -> list[dict]:
    """
    Loads .json documents from data/sample_docs/. Each file is expected to
    look like:
    {
      "source": "GDAHP Poultry Newcastle Disease Vaccination Guide (sample)",
      "category": "livestock",          -> "crop" | "livestock" | "market"
      "product": "poultry",              -> e.g. "rice", "cashew", "poultry", "cattle", "general"
      "lifecycle_stage": "raise",         -> plant|grow|raise|harvest|process|sell|consume|plan
      "province": "national",
      "topic": "animal_health",
      "text": "..."
    }
    The category/lifecycle_stage fields cover the full farming cycle this
    knowledge base is meant to answer questions about -- not just crops:
    Plant -> Grow -> Raise (livestock) -> Harvest -> Process -> Sell
    (market access) -> Consume -> Plan -> back to Plant.
    Swap this loader for real ingestion of CARDI/GDA/GDAHP/FAO/NGO material
    once sourced -- the chunking/embedding/storage logic below doesn't change.
    """
    docs = []
    for path in sorted(SAMPLE_DOCS_DIR.glob("*.json")):
        with open(path, "r", encoding="utf-8") as f:
            docs.append(json.load(f))
    return docs


def build_index(reset: bool = True) -> chromadb.Collection:
    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    embedder = get_embedder()
    documents = load_sample_documents()

    ids, texts, metadatas, embeddings = [], [], [], []

    for doc in documents:
        for chunk in chunk_text(doc["text"]):
            ids.append(str(uuid.uuid4()))
            texts.append(chunk)
            metadatas.append(
                {
                    "source": doc.get("source", "unknown"),
                    "category": doc.get("category", "general"),
                    "product": doc.get("product", "general"),
                    "lifecycle_stage": doc.get("lifecycle_stage", "general"),
                    "province": doc.get("province", "national"),
                    "topic": doc.get("topic", "general"),
                }
            )

    if not texts:
        print("No sample documents found in data/sample_docs/. Nothing to index.")
        return collection

    embeddings = embedder.embed(texts)

    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Indexed {len(texts)} chunks from {len(documents)} source documents "
          f"into collection '{COLLECTION_NAME}'.")
    return collection


if __name__ == "__main__":
    build_index(reset=True)
