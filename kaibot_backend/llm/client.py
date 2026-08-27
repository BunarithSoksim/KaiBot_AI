"""
LLM provider abstraction. Now language-aware: every generation method
takes a `language: str` ("km" | "en") and selects the matching system
prompt / fallback message.
"""
from dataclasses import dataclass
import os

from config import settings
from llm.prompts import (
    SYSTEM_PROMPT_KM,
    SYSTEM_PROMPT_EN,
    SYSTEM_PROMPT_SMALLTALK_KM,
    SYSTEM_PROMPT_SMALLTALK_EN,
    SYSTEM_PROMPT_OFFTOPIC_CHECK,
    build_user_turn,
)
from rag.retriever import RetrievedChunk


@dataclass
class LLMResponse:
    text: str
    used_fallback: bool


def _system_prompt(language: str) -> str:
    return SYSTEM_PROMPT_EN if language == "en" else SYSTEM_PROMPT_KM


def _smalltalk_prompt(language: str) -> str:
    return SYSTEM_PROMPT_SMALLTALK_EN if language == "en" else SYSTEM_PROMPT_SMALLTALK_KM


def _low_confidence_message(language: str) -> str:
    return settings.low_confidence_message_en if language == "en" else settings.low_confidence_message_km


def _greeting_response(language: str) -> str:
    return settings.greeting_response_en if language == "en" else settings.greeting_response_km


class BaseLLMClient:
    def generate(self, question: str, chunks: list[RetrievedChunk], language: str = "km") -> LLMResponse:
        raise NotImplementedError

    def generate_smalltalk(self, text: str, language: str = "km") -> str:
        raise NotImplementedError

    def classify_offtopic(self, question: str) -> bool:
        raise NotImplementedError


class MockLLMClient(BaseLLMClient):
    def generate(self, question: str, chunks: list[RetrievedChunk], language: str = "km") -> LLMResponse:
        if not chunks:
            return LLMResponse(text=_low_confidence_message(language), used_fallback=True)
        top = chunks[0]
        preview = top.text[:120]
        return LLMResponse(
            text=f"[MOCK ANSWER based on '{top.source}']: {preview}...",
            used_fallback=False,
        )

    def generate_smalltalk(self, text: str, language: str = "km") -> str:
        return f"[MOCK SMALLTALK REPLY to '{text}']"

    def classify_offtopic(self, question: str) -> bool:
        return False


class GeminiLLMClient(BaseLLMClient):
    def __init__(self) -> None:
        from google import genai  # local import: only needed when this provider is active
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file "
                "before using KAIBOT_LLM_PROVIDER=gemini."
            )
        self._client = genai.Client(api_key=api_key)

    def generate(self, question: str, chunks: list[RetrievedChunk], language: str = "km") -> LLMResponse:
        user_turn = build_user_turn(question, chunks, language=language)
        interaction = self._client.interactions.create(
            model=settings.llm_model,
            system_instruction=_system_prompt(language),
            input=user_turn,
        )
        return LLMResponse(text=interaction.output_text, used_fallback=False)

    def generate_smalltalk(self, text: str, language: str = "km") -> str:
        interaction = self._client.interactions.create(
            model=settings.llm_model,
            system_instruction=_smalltalk_prompt(language),
            input=text,
        )
        return interaction.output_text

    def classify_offtopic(self, question: str) -> bool:
        interaction = self._client.interactions.create(
            model=settings.llm_model,
            system_instruction=SYSTEM_PROMPT_OFFTOPIC_CHECK,
            input=question,
        )
        return interaction.output_text.strip().lower().startswith("offtopic")


class ClaudeLLMClient(BaseLLMClient):
    """Stub: wire up the Anthropic SDK here if Claude is chosen instead of Gemini."""

    def generate(self, question: str, chunks: list[RetrievedChunk], language: str = "km") -> LLMResponse:
        raise NotImplementedError(
            "Wire up anthropic.Anthropic().messages.create(...) here, passing "
            "the language-appropriate system prompt and build_user_turn(..., language=language)."
        )

    def generate_smalltalk(self, text: str, language: str = "km") -> str:
        raise NotImplementedError("Wire up the Anthropic SDK here, passing the language-appropriate smalltalk prompt.")

    def classify_offtopic(self, question: str) -> bool:
        raise NotImplementedError("Wire up the Anthropic SDK here, passing SYSTEM_PROMPT_OFFTOPIC_CHECK as `system`.")


def get_llm_client() -> BaseLLMClient:
    provider = settings.llm_provider
    if provider == "mock":
        return MockLLMClient()
    if provider == "gemini":
        return GeminiLLMClient()
    if provider == "claude":
        return ClaudeLLMClient()
    raise ValueError(f"Unknown LLM provider: {provider}")


def answer_question(
    question: str,
    chunks: list[RetrievedChunk],
    low_confidence: bool,
    language: str = "km",
) -> LLMResponse:
    """
    Enforces the fallback rule at the boundary: a low-confidence retrieval
    never reaches the LLM. `language` only affects wording, never this gate.
    """
    if low_confidence:
        return LLMResponse(text=_low_confidence_message(language), used_fallback=True)
    client = get_llm_client()
    return client.generate(question, chunks, language=language)


def answer_smalltalk(text: str, language: str = "km") -> str:
    """
    Falls back to the static greeting message (in the requested language)
    if the API call fails for any reason.
    """
    try:
        client = get_llm_client()
        return client.generate_smalltalk(text, language=language)
    except Exception as e:  # noqa: BLE001 -- external API call, must degrade safely
        print(f"[answer_smalltalk] falling back to static message: {e}")
        return _greeting_response(language)


def is_offtopic(question: str) -> bool:
    """
    Only called when retrieval already returned low_confidence=True.
    Language-agnostic classifier — defaults to False (treat as farming,
    use the existing safety message) if the call itself fails.
    """
    try:
        client = get_llm_client()
        return client.classify_offtopic(question)
    except Exception as e:  # noqa: BLE001 -- external API call, must degrade safely
        print(f"[is_offtopic] defaulting to False (farming) due to error: {e}")
        return False