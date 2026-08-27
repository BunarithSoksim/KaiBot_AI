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
SAMPLE_DOCS_DIR = BASE_DIR / "data" / "sample_docs"


@dataclass
class Settings:
    # --- LLM ---
    llm_provider: str = os.getenv("KAIBOT_LLM_PROVIDER", "mock")
    llm_model: str = os.getenv("KAIBOT_LLM_MODEL", "gemini-3.6-flash")
    max_output_tokens: int = 1000

    # --- Embeddings ---
    embedding_provider: str = os.getenv("KAIBOT_EMBEDDING_PROVIDER", "mock")
    embedding_dim: int = int(os.getenv("KAIBOT_EMBEDDING_DIM", "768"))

    # --- RAG retrieval ---
    top_k: int = int(os.getenv("KAIBOT_TOP_K", "4"))
    min_similarity_score: float = float(os.getenv("KAIBOT_MIN_SIMILARITY_SCORE", "0.665"))

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