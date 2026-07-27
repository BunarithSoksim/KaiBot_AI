"""
Threshold-tuning helper: run this AFTER `python3 -m rag.ingest` has built the
real (Gemini-embedded) index. It does NOT modify config.py or the live
similarity threshold — it just reports what score each query WOULD get,
so you can pick a real min_similarity_score based on evidence instead of
a guess.

Why this exists: the Jul 21 test_rag_pipeline run showed every question,
including a totally off-topic one ("Should I buy Bitcoin this year?"),
scoring ABOVE the current threshold (0.35). That means the code-level
fallback (retriever.py's low_confidence gate) never actually fires in
practice right now -- only the LLM's own system-prompt instruction caught
it. This script exists to find a threshold where the gate itself does its
job, without accidentally cutting off real matches (which sat at 0.65-0.79
in that same run).

Usage:
    python3 tune_threshold.py
"""
from __future__ import annotations

from rag.retriever import Retriever

# Known-relevant questions (should stay ABOVE whatever threshold we pick)
ON_TOPIC_QUERIES: list[str] = [
    "How should I split fertilizer for wet-season rice?",
    "What pest is damaging my cashew shoots in Preah Vihear?",
    "How long can I keep harvested cassava before it spoils?",
    "My chickens are dying suddenly with green diarrhea, what could it be?",
    "What should I feed my cattle in the dry season?",
    "Where can I get a better price for my cashew nuts?",
]

# Known-irrelevant questions (should drop BELOW whatever threshold we pick)
OFF_TOPIC_QUERIES: list[str] = [
    "Should I buy Bitcoin this year?",
    "What's the weather like on Mars?",
    "Can you help me write a resignation letter?",
    "តើផ្កាយអង្គារមានទំហំធំប៉ុនណា?",  # Khmer: "How big is the planet Mars?"
]


def report(label: str, queries: list[str], retriever: Retriever) -> None:
    print(f"\n--- {label} ---")
    for q in queries:
        # top_k=1 since we only care about the single best match's score
        result = retriever.retrieve(q, top_k=1)
        best = result.chunks[0].similarity if result.chunks else 0.0
        print(f"  {best:.3f}  {q}")


def main() -> None:
    retriever = Retriever()
    report("ON-TOPIC (want these to stay HIGH)", ON_TOPIC_QUERIES, retriever)
    report("OFF-TOPIC (want these to drop LOW)", OFF_TOPIC_QUERIES, retriever)
    print(
        "\nLook for the biggest gap between the lowest on-topic score and the "
        "highest off-topic score -- set KAIBOT_MIN_SIMILARITY_SCORE somewhere "
        "in that gap."
    )


if __name__ == "__main__":
    main()
