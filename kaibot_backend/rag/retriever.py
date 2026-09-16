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
import re
from dataclasses import dataclass

import chromadb

from config import settings, CHROMA_PERSIST_DIR
from rag.embeddings import get_embedder
from rag.ingest import COLLECTION_NAME

# Every non-"general" value the ingested knowledge base uses for the
# "product" metadata field (data/knowledge_base/**/*.json). Kept as a
# static list rather than queried from Chroma at import time so retrieval
# doesn't depend on the collection already existing/being non-empty.
KNOWN_PRODUCTS = [
    "alfalfa", "angled_luffa", "banana", "black_gram", "broccoli", "cabbage",
    "carrot", "cashew", "cassava", "cattle", "cauliflower", "coconut", "corn",
    "cucumber", "durian", "jackfruit", "kale", "longan", "lychee", "mango",
    "mung_bean", "muskmelon", "mustard_greens", "ochna", "orange", "papaya",
    "peanut", "pig", "pineapple", "pomelo", "poultry", "pumpkin", "radish",
    "rice", "round_luffa", "soybean", "sweet_potato", "taro", "tomato",
    "watermelon", "wax_gourd", "wild_orchid", "yard_long_bean",
]


def _build_product_patterns(products: list[str]) -> list[tuple[str, re.Pattern]]:
    # "wax_gourd" -> r"\bwax\s+gourde?s?\b", so both "wax gourd" and
    # "wax gourds" match against an English query. This is a crude plural
    # heuristic (not real morphology) but covers the common case of a
    # farmer typing the plain English crop name.
    patterns = []
    for product in products:
        phrase = re.escape(product.replace("_", " ")).replace(r"\ ", r"\s+")
        patterns.append((product, re.compile(rf"\b{phrase}e?s?\b", re.IGNORECASE)))
    return patterns


_PRODUCT_PATTERNS = _build_product_patterns(KNOWN_PRODUCTS)


def detect_product(query: str) -> str | None:
    """
    Best-effort detection of which crop/livestock product a query names,
    by matching the English product keyword directly in the query text.

    Why this exists: the knowledge base text itself is written in Khmer,
    so an English query like "How do I grow wax gourd?" has no lexical
    overlap with the source documents -- the embedder has to bridge
    English<->Khmer purely on semantic similarity. In practice, generic
    Khmer farming-procedure language (planting spacing, harvest signs) is
    similar across crops, and heavily-represented crops (corn, watermelon,
    cucumber) can out-rank the correct, sparser crop even when it's
    tagged with the right product metadata. Matching the crop name
    directly against the query and filtering on it sidesteps that -- exact
    keyword match is a stronger signal than embedding similarity here.
    """
    lowered = query.lower()
    for product, pattern in _PRODUCT_PATTERNS:
        if pattern.search(lowered):
            return product
    return None


# Selling/market-intent keywords. Why this is needed in addition to
# detect_product: the "market" category has only ~32 docs total, spread
# thinly across 8 products, while the same products have far more "crop"
# (cultivation) docs. Filtering on product alone lets the numerous crop
# chunks crowd out the one relevant market chunk for a selling question
# (observed: "What is contract farming for rice?" returned 3 crop chunks
# and only 1 market chunk in the top 4, and the market chunk wasn't even
# about contract farming specifically).
_MARKET_INTENT_PATTERN = re.compile(
    r"\b(sell|selling|sold|buyer|market price|market access|cooperative|"
    r"negotiat|contract farming|grading standard|bulk selling|aggregation)\b",
    re.IGNORECASE,
)


def is_market_intent(query: str) -> bool:
    return bool(_MARKET_INTENT_PATTERN.search(query))


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

        base_conditions = []
        if province_filter:
            # Fall back gracefully: "national" content should always be
            # eligible even when filtering by a specific province.
            base_conditions.append({"province": {"$in": [province_filter, "national"]}})
        if category_filter:
            # category_filter is "crop" | "livestock" | "market" -- useful
            # once the UI lets a farmer say "this is about my chickens" vs.
            # "this is about my rice" vs. "where do I sell this".
            base_conditions.append({"category": {"$eq": category_filter}})

        # If the query names a known crop/livestock product, restrict to it
        # first -- an exact keyword match beats embedding similarity here
        # (see detect_product's docstring). Only fall back to the
        # unrestricted search if that turns up nothing, so a false-positive
        # keyword match can't make an otherwise-answerable question fail.
        detected_product = detect_product(query)
        if detected_product:
            product_conditions = base_conditions + [{"product": {"$eq": detected_product}}]

            # A selling/market question about a product that's also a crop
            # (e.g. rice, tomato) should prefer the sparse "market" chunks
            # over the far more numerous "crop" ones -- try that narrower
            # filter first, and only widen if it comes up empty.
            if is_market_intent(query) and not category_filter:
                market_conditions = product_conditions + [{"category": {"$eq": "market"}}]
                chunks = self._query(query_embedding, market_conditions, top_k)
                if chunks:
                    return self._to_result(chunks, threshold=settings.min_similarity_score_product_match)

            chunks = self._query(query_embedding, product_conditions, top_k)
            if chunks:
                return self._to_result(chunks, threshold=settings.min_similarity_score_product_match)

        chunks = self._query(query_embedding, base_conditions, top_k)
        return self._to_result(chunks, threshold=settings.min_similarity_score)

    def _query(self, query_embedding: list[float], conditions: list[dict], top_k: int) -> list[RetrievedChunk]:
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
        return chunks

    def _to_result(self, chunks: list[RetrievedChunk], threshold: float) -> RetrievalResult:
        best_score = max((c.similarity for c in chunks), default=0.0)
        low_confidence = best_score < threshold
        return RetrievalResult(chunks=chunks, low_confidence=low_confidence)
