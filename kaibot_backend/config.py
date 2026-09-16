"""
Central configuration for KaiBot/SmartKasekor.
"""
import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

CHROMA_PERSIST_DIR = BASE_DIR / "chroma_store"
KNOWLEDGE_BASE_DIR = BASE_DIR / "data" / "knowledge_base"


@dataclass
class Settings:
    # --- LLM ---
    llm_provider: str = os.getenv("KAIBOT_LLM_PROVIDER", "mock")
    llm_model: str = os.getenv("KAIBOT_LLM_MODEL", "gemini-3.6-flash")
    max_output_tokens: int = 1000
    # Without this, a stalled network call to the Gemini API blocks forever
    # (observed: a single hung request stuck a process for 1h49m with the
    # client never timing out or raising). Applies to both the LLM and
    # embedding Gemini clients.
    gemini_request_timeout_ms: int = int(os.getenv("KAIBOT_GEMINI_TIMEOUT_MS", "30000"))
    # The SDK's own default (5 attempts, up to 60s max delay between
    # retries) means a single call can still balloon to several minutes
    # under quota pressure even with the per-request timeout above
    # (observed: a 13-minute stall on one call). Capping attempts bounds
    # worst-case latency to roughly attempts * timeout, which matters
    # because app.py has no request-level timeout of its own -- a hung
    # LLM call currently hangs the farmer's whole chat request.
    gemini_max_retry_attempts: int = int(os.getenv("KAIBOT_GEMINI_MAX_RETRY_ATTEMPTS", "2"))

    # --- Embeddings ---
    embedding_provider: str = os.getenv("KAIBOT_EMBEDDING_PROVIDER", "mock")
    embedding_dim: int = int(os.getenv("KAIBOT_EMBEDDING_DIM", "768"))

    # --- RAG retrieval ---
    top_k: int = int(os.getenv("KAIBOT_TOP_K", "4"))
    min_similarity_score: float = float(os.getenv("KAIBOT_MIN_SIMILARITY_SCORE", "0.665"))

    # Lower bar used when the query's crop/livestock name was matched
    # directly against chunk metadata (see rag.retriever.detect_product).
    # A correctly product-filtered chunk can legitimately score lower than
    # min_similarity_score -- a short English query has less lexical/
    # semantic overlap with a narrow, specific Khmer passage than it does
    # with a generic "farming procedure" passage from an unrelated,
    # heavily-represented crop. The keyword match on the crop name is
    # already strong evidence of topical relevance, so this threshold only
    # needs to catch genuinely garbled/irrelevant chunks, not rank crops
    # against each other.
    min_similarity_score_product_match: float = float(
        os.getenv("KAIBOT_MIN_SIMILARITY_SCORE_PRODUCT_MATCH", "0.5")
    )

    # --- Confidence / safety (Khmer) ---
    low_confidence_message_km: str = (
        "ខ្ញុំមិនទាន់មានព័ត៌មានច្បាស់លាស់អំពីសំណួរនេះទេ។ "
        "សូមសាកសួរមន្ត្រីកសិកម្មក្នុងស្រុក ឬការិយាល័យកសិកម្មដើម្បីទទួលបានចម្លើយត្រឹមត្រូវ។"
    )
    greeting_response_km: str = (
        "សួស្តី! ខ្ញុំគឺ SmartKasekor ជំនួយការកសិកម្ម។ អ្នកអាចសួរខ្ញុំអំពីដំណាំ "
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

    # --- Confidence / safety (English) — NEW ---
    low_confidence_message_en: str = (
        "I don't have reliable information on this yet. Please check with a local "
        "agricultural officer or extension office for an accurate answer."
    )
    greeting_response_en: str = (
        "Hi! I'm SmartKasekor, a farming assistant. You can ask me about crops, "
        "livestock, or selling your harvest. If I'm not sure of an answer, I'll tell you honestly."
    )
    offtopic_message_en: str = (
        "That doesn't look like a farming question. I can help with crops, livestock, "
        "or selling your harvest — feel free to ask about those!"
    )
    no_internet_message_en: str = (
        "I can't reach the internet right now and don't have a saved answer for this. "
        "Please ask a local agricultural officer directly."
    )

    # --- Voice ---
    stt_provider: str = os.getenv("KAIBOT_STT_PROVIDER", "mock")
    tts_provider: str = os.getenv("KAIBOT_TTS_PROVIDER", "mock")
    khmer_language_code: str = "km-KH"
    english_language_code: str = "en-US"

    def language_code(self, language: str) -> str:
        """Maps our internal 'km'/'en' language flag to a BCP-47 code for STT/TTS."""
        return self.english_language_code if language == "en" else self.khmer_language_code


settings = Settings()