"""
Stress test for the re-tuned similarity threshold (0.665), run AFTER
`python3 -m rag.ingest` has built the real 33-doc index.

Unlike tune_threshold.py's clean, well-formed test sentences, these are
deliberately messier and more adversarial:
  - ON-TOPIC: short, fragmented, colloquial phrasing -- how a real farmer
    might actually type on a phone, not a polished test sentence.
  - OFF-TOPIC: chosen to deliberately share vocabulary with the knowledge
    base (fever, selling, sickness) to specifically probe for false
    positives that generic off-topic questions (Bitcoin, Mars) wouldn't catch.

Usage:
    python3 stress_test_threshold.py
"""
from __future__ import annotations

from rag.retriever import Retriever

THRESHOLD = 0.665  # keep in sync with .env / config.py for this test

# Short, fragmented, colloquial -- realistic messy farmer phrasing.
# Should stay ABOVE the threshold.
ON_TOPIC_MESSY: list[str] = [
    "ស្រូវ ជី",                          # "rice fertilizer" -- just two words
    "មាន់ងាប់",                          # "chicken died" -- terse
    "ជ្រូក ឈឺ",                          # "pig sick" -- terse, ASF-adjacent
    "គោ ស្គម",                           # "cow skinny" -- matches Q16
    "ស្វាយចន្ទី តម្លៃ",                    # "cashew price" -- terse
    "ចង់ចូលសហករណ៍",                      # "want to join cooperative" -- colloquial
    "ដំណាំខ្ញុំស្លឹកលឿង",                  # "my crop's leaves are yellow"
    "ត្រូវការទឹកប៉ុន្មានសម្រាប់ចេក",         # "how much water for banana" -- matches new doc
]

# Deliberately share vocabulary with the knowledge base (fever, selling,
# sickness) without actually being farming questions. These are the ones
# most likely to slip past a naive threshold.
OFF_TOPIC_TRICKY: list[str] = [
    "ជួយផង",                             # "help me" -- generic, no topic
    "តើខ្ញុំគួរជួសជុលឡានយ៉ាងម៉េច?",         # "how do I fix my car"
    "ចង់ដឹងអំពីនយោបាយ",                   # "want to know about politics"
    "កូនខ្ញុំឈឺក្តៅ",                      # "my child has a fever" -- shares "fever" with disease docs
    "លក់ម៉ូតូ",                          # "sell a motorbike" -- shares "sell" with market docs
]


def report(label: str, queries: list[str], retriever: Retriever) -> list[tuple[str, float]]:
    print(f"\n--- {label} ---")
    results = []
    for q in queries:
        result = retriever.retrieve(q, top_k=1)
        best = result.chunks[0].similarity if result.chunks else 0.0
        flag = ""
        results.append((q, best))
        print(f"  {best:.3f}  {q}{flag}")
    return results


def main() -> None:
    retriever = Retriever()
    on_topic = report("ON-TOPIC, MESSY (want ABOVE 0.665)", ON_TOPIC_MESSY, retriever)
    off_topic = report("OFF-TOPIC, VOCAB-OVERLAP (want BELOW 0.665)", OFF_TOPIC_TRICKY, retriever)

    print(f"\n--- Pass/fail against threshold={THRESHOLD} ---")
    on_fails = [(q, s) for q, s in on_topic if s < THRESHOLD]
    off_fails = [(q, s) for q, s in off_topic if s >= THRESHOLD]

    if on_fails:
        print("  ON-TOPIC questions that INCORRECTLY fell below threshold (false 'I don't know'):")
        for q, s in on_fails:
            print(f"    {s:.3f}  {q}")
    else:
        print("  All messy on-topic questions correctly stayed above threshold.")

    if off_fails:
        print("  OFF-TOPIC questions that INCORRECTLY passed threshold (false confident answer):")
        for q, s in off_fails:
            print(f"    {s:.3f}  {q}")
    else:
        print("  All tricky off-topic questions correctly stayed below threshold.")


if __name__ == "__main__":
    main()
