from llm.offline_fallback import _score, _CACHE

test_queries = [
    "cashew pest",
    "cow food dry season",
    "សត្វល្អិតបំផ្លាញស្វាយចន្ទី",
]

for q in test_queries:
    print(f"\nQuery: {q}")
    scored = sorted(_CACHE, key=lambda e: _score(q, e), reverse=True)[:3]
    for e in scored:
        print(f"  {_score(q, e):.3f}  keywords={e.get('keywords', [])}  q='{e['question'][:50]}'")
