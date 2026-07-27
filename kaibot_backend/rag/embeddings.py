"""
Embedding provider abstraction.

Why pluggable: the July 6-24 build happens before real farmer data exists
and possibly before API keys/network access are finalized. Every part of
the RAG pipeline should be swappable without touching ingest.py or
retriever.py. Add a new provider by implementing `embed(texts) -> list[vector]`.
"""
import hashlib
import os
import numpy as np
from config import settings


class BaseEmbedder:
    dim: int = settings.embedding_dim

    def embed(self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
        """
        task_type distinguishes how a real embedding model orients the
        vector: "RETRIEVAL_DOCUMENT" when indexing knowledge base chunks,
        "RETRIEVAL_QUERY" when embedding a farmer's question. Google's
        gemini-embedding-001 uses this to produce better-aligned vectors
        for asymmetric search (short question -> long document). The
        MockEmbedder ignores it since it has no real notion of retrieval
        orientation.
        """
        raise NotImplementedError


class MockEmbedder(BaseEmbedder):
    """
    Deterministic, offline, dependency-free embedder for local dev/testing.
    NOT semantically meaningful across unrelated sentences beyond crude
    lexical overlap -- replace before the July 29 demo. Its only job here
    is to let the rest of the pipeline (chunking, storage, retrieval,
    fallback logic) be built and tested without network access.
    """

    def embed(self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
        vectors = []
        for text in texts:
            vectors.append(self._hash_embed(text))
        return vectors

    def _hash_embed(self, text: str) -> list[float]:
        # Bag-of-words hashing trick: each token deterministically hashes
        # into a fixed-size vector bucket (positive count), giving a
        # lexical-overlap similarity signal that's good enough to validate
        # pipeline wiring end-to-end offline.
        vec = np.zeros(self.dim, dtype=np.float32)
        tokens = text.lower().split()
        if not tokens:
            return vec.tolist()
        for tok in tokens:
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            vec[idx] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec.tolist()


class GeminiEmbedder(BaseEmbedder):
    """
    Real embedding provider using gemini-embedding-001 (GA, supports 100+
    languages including Khmer). Requires GEMINI_API_KEY in .env.
    Output dimensionality is truncated to settings.embedding_dim (default
    768, one of Google's recommended sizes) via Matryoshka representation
    learning -- shrinks storage/compute cost with minimal quality loss.
    """

    def __init__(self):
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file "
                "before using KAIBOT_EMBEDDING_PROVIDER=gemini."
            )
        self._client = genai.Client(api_key=api_key)

    def embed(self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
        from google.genai import types
        result = self._client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts,
            config=types.EmbedContentConfig(
                task_type=task_type,
                output_dimensionality=self.dim,
            ),
        )
        return [e.values for e in result.embeddings]


class CohereMultilingualEmbedder(BaseEmbedder):
    """Stub: Cohere embed-multilingual-v3 has strong Southeast Asian language
    coverage and is worth benchmarking against Khmer agricultural text."""

    def embed(self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> list[list[float]]:
        raise NotImplementedError("Wire up Cohere embed-multilingual-v3 here.")


def get_embedder() -> BaseEmbedder:
    provider = settings.embedding_provider
    if provider == "mock":
        return MockEmbedder()
    if provider == "gemini":
        return GeminiEmbedder()
    if provider == "cohere":
        return CohereMultilingualEmbedder()
    raise ValueError(f"Unknown embedding provider: {provider}")
