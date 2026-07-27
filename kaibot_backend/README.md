# KaiBot Backend — Coding / Model Integration / RAG Skeleton

This is a working, tested skeleton for the pieces defined in Week 1 (architecture)
and Week 3 (build) of the plan: RAG pipeline, LLM integration, and voice
provider wiring. Everything runs fully offline right now behind "mock"
providers so it can be built and tested before API keys, a chosen LLM, or a
chosen STT/TTS vendor are finalized — swap providers via `.env` without
touching business logic.

## Scope: the full farming cycle, not just crops

The knowledge base schema covers the whole cycle a farmer actually lives:

**Plant → Grow → Raise (livestock) → Harvest → Process → Sell (market access) → Consume → Plan → back to Plant**

Every knowledge chunk is tagged with:
- `category`: `"crop"` | `"livestock"` | `"market"`
- `product`: e.g. `"rice"`, `"cashew"`, `"poultry"`, `"cattle"`, `"general"`
- `lifecycle_stage`: `"plant"` | `"grow"` | `"raise"` | `"harvest"` | `"process"` | `"sell"` | `"consume"` | `"plan"`
- `province`, `topic`, `source`

This means a farmer asking about a sick chicken, a fair cashew price, or
rice fertilizer timing all hit the same pipeline — the API supports an
optional `category` filter (`crop`/`livestock`/`market`) alongside the
existing `province` filter.

## Structure

```
kaibot_backend/
├── app.py                  # FastAPI endpoints (/chat, /chat/voice, /health)
├── config.py                # all tunables in one place (models, thresholds, paths)
├── rag/
│   ├── embeddings.py         # pluggable embedding providers (mock/Gemini/Cohere)
│   ├── ingest.py              # chunk + embed + store docs into ChromaDB
│   └── retriever.py           # top-k retrieval, province + category filtering, low-confidence detection
├── llm/
│   ├── prompts.py              # Khmer system prompt + context/user turn builder
│   └── client.py                 # pluggable LLM providers (mock/Gemini/Claude)
├── voice/
│   └── stt_tts.py                 # pluggable STT/TTS providers (mock/Google)
├── data/sample_docs/                # 6 sample Cambodia-specific knowledge docs
│   ├── rice_fertilizer.json           # crop / rice / grow
│   ├── cashew_pest.json                # crop / cashew / grow (Preah Vihear)
│   ├── cassava_postharvest.json         # crop / cassava / process
│   ├── poultry_newcastle_disease.json    # livestock / poultry / raise
│   ├── livestock_feed_quality.json        # livestock / cattle / raise
│   └── cashew_market_access.json           # market / cashew / sell
└── tests/test_rag_pipeline.py         # end-to-end smoke test (passing)
```

## How the pieces fit together

```
farmer question (text or voice)
        │
   [voice/stt_tts.py]  (if voice: audio -> Khmer text)
        │
   [rag/retriever.py]  embed question -> query ChromaDB (optional province/category filter)
        │                              -> top-k chunks -> similarity below threshold?
        │                                      │
        │                          yes ────────┴──── no
        │                           │                  │
        │                  low_confidence=True     pass chunks to LLM
        │                  return fallback msg           │
        │                  (config.settings.              │
        │                   low_confidence_message_km)     │
        │                                                    │
        └──────────────────────────────  [llm/client.py] build prompt
                                          (llm/prompts.py: SYSTEM_PROMPT_KM +
                                           context block + question)
                                          -> call LLM -> Khmer answer
                                                    │
                                          [voice/stt_tts.py] (if voice: text -> audio)
```

The important architectural decision baked in here: **the fallback check
happens in code, before the LLM is ever called**, not as an instruction the
LLM might ignore. If retrieval confidence is below
`config.settings.min_similarity_score`, `llm/client.answer_question()`
returns the fixed Khmer fallback message and never invokes the model. This
is the concrete implementation of the "don't let the AI improvise on
pesticide dosages" risk flagged in the project scope — and the same rule
now protects livestock and market-access answers too (e.g. don't let the
model improvise on medicine dosages for a sick animal).

## Running it

```bash
pip install -r requirements.txt
python -m rag.ingest              # builds the ChromaDB index from data/sample_docs/
python -m tests.test_rag_pipeline  # end-to-end smoke test (already verified passing)
uvicorn app:app --reload           # starts the API on http://127.0.0.1:8000
```

Try it (crop question):
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What pest is damaging my cashew shoots?", "province": "Preah Vihear"}'
```

Try it (livestock question, filtered):
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "What should I feed my cattle in the dry season?", "category": "livestock"}'
```

Try it (market access question):
```bash
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question": "Where can I get a better price for my cashew nuts?", "category": "market"}'
```

**Note on the mock embedder's limits:** it's a crude lexical-overlap hash
with no concept of synonyms, so a question about "chickens" won't
necessarily match a document written using "poultry"/"birds" — this is
expected and demonstrated (not hidden) in the test output. A real
embedding model resolves this. What *is* fully reliable regardless of
embedding quality is the `category`/`province` metadata filtering, since
that's a deterministic database filter, not a similarity guess — see the
"Category filter check" section of the test output.

## What must change before the July 29 Preah Vihear demo

1. **Embeddings**: `KAIBOT_EMBEDDING_PROVIDER=mock` → a real multilingual model
   (Gemini `text-embedding-004` or Cohere `embed-multilingual-v3` are the two
   worth benchmarking first — Week 1 Friday task). The mock is a crude
   lexical hash purely for offline pipeline testing; it is not semantically
   meaningful and will not reliably tell relevant from irrelevant questions,
   or resolve synonyms (chicken/poultry, cow/cattle, etc.).
2. **LLM**: `KAIBOT_LLM_PROVIDER=mock` → `gemini` or `claude`. The stub
   classes in `llm/client.py` show exactly where the real API call goes;
   the prompt (`llm/prompts.py`) doesn't need to change when you do this.
   Note: Google's Gemini API/SDK changed in 2026 (new `interactions` API,
   `google-genai` client) — check current docs before wiring this up.
3. **STT/TTS**: `KAIBOT_STT_PROVIDER`/`KAIBOT_TTS_PROVIDER` → `google` (or
   add a Whisper/Coqui provider class). Benchmark against real farmer audio
   with background noise and regional accent before locking this in —
   this was flagged as a Week 1 task.
4. **Re-tune `settings.min_similarity_score`** once a real embedding model
   is in place — the current default (0.35) was chosen for a real
   embedding model's similarity distribution, not the mock's. For local
   testing with the mock, override via `KAIBOT_MIN_SIMILARITY_SCORE=0.1`
   (env var) rather than editing code.
5. **Replace/expand `data/sample_docs/`** with real CARDI/GDA/GDAHP/FAO/NGO
   sourced material across all three categories — the six sample docs here
   are illustrative, not a real knowledge base. Good real leads to start
   from: `elibrary.maff.gov.kh` and `gda.maff.gov.kh`'s Publications page
   for crop/GDA material, GDAHP (General Directorate of Animal Health and
   Production) for livestock/animal health material, and the HEKS/EPER
   Cambodian Cashew Value Chain Assessment for market-access content
   specific to Preah Vihear.
6. **Add an offline/low-connectivity fallback path** for the event itself
   (e.g. a pre-built local ChromaDB + local LLM or cached Q&A set) — this
   codebase already runs entirely locally with `mock`/no network calls
   except when a real provider is switched on, which is a good starting
   point for an offline demo mode.
