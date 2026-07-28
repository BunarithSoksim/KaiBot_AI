from rag.retriever import Retriever

r = Retriever()
result = r.retrieve("How should I split fertilizer for wet-season rice?", top_k=10)
for c in result.chunks:
    print(f"{c.similarity:.3f}  {c.source[:60]}  | {c.text[:60]}")
