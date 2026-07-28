from rag.retriever import Retriever

r = Retriever()
# Khmer: "How should nitrogen fertilizer be split for wet-season rice?"
result = r.retrieve("ការដាក់ជីអាសូតសម្រាប់ស្រូវវស្សាគួរបែងចែកយ៉ាងដូចម្តេច", top_k=10)
for c in result.chunks:
    print(f"{c.similarity:.3f}  {c.source[:60]}  | {c.text[:60]}")
