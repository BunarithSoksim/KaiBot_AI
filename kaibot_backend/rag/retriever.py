"""
Retrieval layer: takes a farmer's question, returns the top-k relevant
knowledge chunks plus a confidence signal the LLM layer and the API layer
both need.

This is where the "accuracy of AI responses" risk from the project scope
gets handled structurally: if nothing retrieved clears the similarity
threshold, we do NOT let the LLM improvise -- we return low_confidence=True
and the caller is expected to show config.settings.low_confidence_message_km
instead of a generated answer.
"""
from dataclasses import dataclass

import chromadb

from config import settings, CHROMA_PERSIST_DIR
from rag.embeddings import get_embedder
from rag.ingest import COLLECTION_NAME


@dataclass
class RetrievedChunk:
    text: str
    source: str
    category: str        # "crop" | "livestock" | "market"
    product: str          # e.g. "rice", "cashew", "poultry", "cattle", "general"
    lifecycle_stage: str   # "plant" | "grow" | "raise" | "harvest" | "process" | "sell" | "consume" | "plan"
    province: str
    topic: str
    similarity: float


@dataclass
class RetrievalResult:
    chunks: list[RetrievedChunk]
    low_confidence: bool


class Retriever:
    def __init__(self):
        self._client = chromadb.PersistentClient(path=str(CHROMA_PERSIST_DIR))
        self._collection = self._client.get_or_create_collection(COLLECTION_NAME)
        self._embedder = get_embedder()

    def retrieve(self, query: str, top_k: int | None = None,
                 province_filter: str | None = None,
                 category_filter: str | None = None) -> RetrievalResult:
        top_k = top_k or settings.top_k
        query_embedding = self._embedder.embed([query], task_type="RETRIEVAL_QUERY")[0]

        conditions = []
        if province_filter:
            # Fall back gracefully: "national" content should always be
            # eligible even when filtering by a specific province.
            conditions.append({"province": {"$in": [province_filter, "national"]}})
        if category_filter:
            # category_filter is "crop" | "livestock" | "market" -- useful
            # once the UI lets a farmer say "this is about my chickens" vs.
            # "this is about my rice" vs. "where do I sell this".
            conditions.append({"category": {"$eq": category_filter}})

        if len(conditions) == 0:
            where_filter = None
        elif len(conditions) == 1:
            where_filter = conditions[0]
        else:
            where_filter = {"$and": conditions}

        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter,
        )

        chunks: list[RetrievedChunk] = []
        docs = results.get("documents", [[]])[0]
        metas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for doc, meta, distance in zip(docs, metas, distances):
            # Chroma cosine "distance" -> similarity (1 - distance)
            similarity = 1.0 - distance
            chunks.append(
                RetrievedChunk(
                    text=doc,
                    source=meta.get("source", "unknown"),
                    category=meta.get("category", "general"),
                    product=meta.get("product", "general"),
                    lifecycle_stage=meta.get("lifecycle_stage", "general"),
                    province=meta.get("province", "national"),
                    topic=meta.get("topic", "general"),
                    similarity=similarity,
                )
            )

        best_score = max((c.similarity for c in chunks), default=0.0)
        low_confidence = best_score < settings.min_similarity_score

        return RetrievalResult(chunks=chunks, low_confidence=low_confidence)
