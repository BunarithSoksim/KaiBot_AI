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
    """
    docs = []
    for path in sorted(SAMPLE_DOCS_DIR.glob("*.json")):
        with open(path, "r", encoding="utf-8") as f:
            docs.append(json.load(f))
    return docs


def build_index(reset: bool = True) -> chromadb.Collection:
    """
    Builds the ChromaDB index from data/sample_docs/.

    Order matters here: chunking and embedding happen FIRST, and the old
    collection is only deleted/replaced AFTER embedding succeeds. This way,
    if the embedding API call fails (rate limit, network, etc.), the
    existing working collection is left untouched instead of being wiped
    out and left empty -- learned this the hard way on Jul 27 when a 429
    mid-rebuild deleted the collection before the replacement data arrived.
    """
    client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))

    embedder = get_embedder()
    documents = load_sample_documents()

    ids, texts, metadatas = [], [], []

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
        return client.get_or_create_collection(COLLECTION_NAME)

    embeddings = embedder.embed(texts)  # if this raises, nothing below has run yet -- old collection is safe

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

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