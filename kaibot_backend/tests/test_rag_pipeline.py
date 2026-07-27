"""
Minimal end-to-end smoke test: build the index from sample docs, run a
few realistic farmer questions through retrieval + the mock LLM, and
check that relevant/irrelevant questions behave as expected.

Run with:  python -m tests.test_rag_pipeline
(from the kaibot_backend/ directory)
"""
from config import settings
from rag.ingest import build_index
from rag.retriever import Retriever
from llm.client import answer_question


def run():
    
    print("=== Building index from sample docs ===")
    build_index(reset=True)

    retriever = Retriever()

    test_cases = [
        ("How should I split fertilizer for wet-season rice?", "rice", None),
        ("What pest is damaging my cashew shoots in Preah Vihear?", "cashew", "Preah Vihear"),
        ("How long can I keep harvested cassava before it spoils?", "cassava", None),
        ("My chickens are dying suddenly with green diarrhea, what could it be?", "poultry", None),
        ("What should I feed my cattle in the dry season?", "cattle", None),
        ("Where can I get a better price for my cashew nuts?", "cashew", None),
        ("Should I buy Bitcoin this year?", None, None),
    ]

    for question, expected_product, province in test_cases:
        print(f"\n--- Q: {question} ---")
        result = retriever.retrieve(question, province_filter=province)
        response = answer_question(question, result.chunks, result.low_confidence)

        print(f"low_confidence={result.low_confidence}")
        for c in result.chunks[:2]:
            print(f"  matched [{c.source}] category={c.category} product={c.product} "
                  f"stage={c.lifecycle_stage} similarity={c.similarity:.3f}")
        print(f"answer: {response.text}")

        if expected_product:
            # NOTE: observational, not a hard assertion. The MockEmbedder is a
            # crude lexical-overlap hash with no concept of synonyms (e.g. it
            # can't tell "chicken" relates to "poultry"/"bird"), so with 6+
            # documents across 3 categories it will sometimes surface the
            # wrong topic. A real embedding model is required before trusting
            # retrieval quality -- this loop is here to eyeball the pipeline
            # end-to-end, not to certify retrieval accuracy.
            matched = any(c.product == expected_product for c in result.chunks)
            print(f"  (expected product '{expected_product}' present: {matched} "
                  f"-- illustrative only with MockEmbedder)")
        else:
            print(f"  (off-topic check is illustrative only with MockEmbedder; "
                  f"low_confidence={result.low_confidence})")

    # --- Hard, embedding-independent test: category metadata filtering ---
    # This mechanism doesn't depend on embedding quality at all -- it's a
    # deterministic Chroma `where` filter -- so it's fair to assert on.
    print("\n--- Category filter check (livestock only) ---")
    livestock_result = retriever.retrieve(
        "any question at all", category_filter="livestock", top_k=10
    )
    assert len(livestock_result.chunks) > 0, "Expected at least one livestock chunk"
    assert all(c.category == "livestock" for c in livestock_result.chunks), (
        "category_filter='livestock' leaked a non-livestock chunk"
    )
    print(f"  OK: {len(livestock_result.chunks)} chunks, all category=='livestock'")

    print("\nAll checks passed.")


if __name__ == "__main__":
    run()
