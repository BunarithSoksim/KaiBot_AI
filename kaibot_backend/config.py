"""
Central configuration for KaiBot.

Keep every tunable (model names, thresholds, paths) here so swapping a
provider (e.g. Gemini -> Claude, or the demo embedding stub -> a real
multilingual embedding API) never means hunting through the codebase.
"""
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")  # loads .env if present; safe no-op if it doesn't exist

CHROMA_PERSIST_DIR = BASE_DIR / "chroma_store"
SAMPLE_DOCS_DIR = BASE_DIR / "data" / "sample_docs"


@dataclass
class Settings:
    # --- LLM ---
    llm_provider: str = os.getenv("KAIBOT_LLM_PROVIDER", "mock")  # "mock" | "gemini" | "claude"
    # NOTE: Google's Gemini API/SDK changed in 2026 (new `interactions` API,
    # `google-genai` client library replacing the older `google-generativeai`).
    # Check ai.google.dev/gemini-api/docs for the current model name/SDK
    # before wiring this up -- gemini-1.5-pro may be deprecated by the time
    # you get to this step.
    llm_model: str = os.getenv("KAIBOT_LLM_MODEL", "gemini-3.6-flash")
    max_output_tokens: int = 1000

    # --- Embeddings ---
    # "mock" is a deterministic offline stand-in used for local dev/testing
    # without network access. Swap to a real multilingual embedding model
    # before the July 29 field demo (e.g. Gemini text-embedding-004,
    # OpenAI text-embedding-3-large, or Cohere embed-multilingual-v3).
    embedding_provider: str = os.getenv("KAIBOT_EMBEDDING_PROVIDER", "mock")
    # 768 is one of Google's recommended output sizes for gemini-embedding-001
    # (via Matryoshka representation learning -- good quality/cost tradeoff).
    # The MockEmbedder also respects this as its hash-bucket count, so
    # switching providers doesn't require touching this value.
    embedding_dim: int = int(os.getenv("KAIBOT_EMBEDDING_DIM", "768"))

    # --- RAG retrieval ---
    top_k: int = int(os.getenv("KAIBOT_TOP_K", "4"))
    # Below this similarity score, the retrieved context is considered too
    # weak to answer confidently -> trigger the low-confidence fallback.
    # NOTE: 0.35 is tuned for a REAL embedding model. The mock hash embedder
    # (KAIBOT_EMBEDDING_PROVIDER=mock) produces much lower absolute scores,
    # so for local testing with mock, override via env, e.g.:
    #   KAIBOT_MIN_SIMILARITY_SCORE=0.1
    min_similarity_score: float = float(os.getenv("KAIBOT_MIN_SIMILARITY_SCORE", "0.665"))

    # --- Confidence / safety ---
    low_confidence_message_km: str = (
        "ខ្ញុំមិនទាន់មានព័ត៌មានច្បាស់លាស់អំពីសំណួរនេះទេ។ "
        "សូមសាកសួរមន្ត្រីកសិកម្មក្នុងស្រុក ឬការិយាល័យកសិកម្មដើម្បីទទួលបានចម្លើយត្រឹមត្រូវ។"
    )

    greeting_response_km: str = (
        "សួស្តី! ខ្ញុំគឺ KaiBot ជំនួយការកសិកម្ម។ អ្នកអាចសួរខ្ញុំអំពីដំណាំ "
        "សត្វចិញ្ចឹម ឬការលក់ដុះដាល។ ប្រសិនបើខ្ញុំមិនប្រាកដចម្លើយ ខ្ញុំនឹងប្រាប់អ្នកត្រង់ៗ។"
    )

    offtopic_message_km: str = (
        "សំណួរនេះហាក់ដូចជាមិនទាក់ទងនឹងកសិកម្មទេ។ ខ្ញុំអាចជួយអំពីដំណាំ សត្វចិញ្ចឹម "
        "ឬការលក់ដុះដាលបាន សូមសាកសួរអំពីប្រធានបទទាំងនេះមើល៍!"
    )

    no_internet_message_km: str = (
        "ខ្ញុំមិនអាចភ្ជាប់អ៊ីនធឺណិតបានទេ ហើយមិនមានចម្លើយដែលបានរក្សាទុកសម្រាប់សំណួរនេះឡើយ។ "
        "សូមសាកសួរមន្ត្រីកសិកម្មក្នុងស្រុកជាមួយផ្ទាល់។"
    )

    # --- Voice ---
    stt_provider: str = os.getenv("KAIBOT_STT_PROVIDER", "mock")  # "mock" | "google" | "whisper"
    tts_provider: str = os.getenv("KAIBOT_TTS_PROVIDER", "mock")  # "mock" | "google" | "coqui"
    khmer_language_code: str = "km-KH"


settings = Settings()
