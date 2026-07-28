from llm.offline_fallback import find_offline_answer

# Mix of near-exact and realistic messy farmer phrasing
test_queries = [
    "What pest is damaging my cashew shoots?",   # near-exact match to seed
    "cashew pest",                                 # terse
    "What should I feed my cattle in the dry season?",  # near-exact
    "cow food dry season",                         # paraphrased
    "សត្វល្អិតបំផ្លាញស្វាយចន្ទី",                    # Khmer, on-topic
    "should I buy bitcoin",                        # should NOT match anything
]

for q in test_queries:
    answer = find_offline_answer(q)
    status = "MATCHED" if answer else "no match"
    preview = answer[:50] if answer else ""
    print(f"[{status}] {q}\n    -> {preview}\n")
