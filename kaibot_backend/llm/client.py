"""
LLM provider abstraction. Same pattern as rag/embeddings.py: swap the
backing model without touching app.py or the RAG layer.
"""
from dataclasses import dataclass
import os

from config import settings
from llm.prompts import (
    SYSTEM_PROMPT_KM,
    SYSTEM_PROMPT_SMALLTALK_KM,
    SYSTEM_PROMPT_OFFTOPIC_CHECK_KM,
    build_user_turn,
)
from rag.retriever import RetrievedChunk


@dataclass
class LLMResponse:
    text: str
    used_fallback: bool


class BaseLLMClient:
    def generate(self, question: str, chunks: list[RetrievedChunk]) -> LLMResponse:
        raise NotImplementedError

    def generate_smalltalk(self, text: str) -> str:
        raise NotImplementedError
    
    def classify_offtopic(self, question: str) -> bool:
        raise NotImplementedError


class MockLLMClient(BaseLLMClient):
    """
    Offline stand-in used until an API key/provider is wired up. Echoes
    back which chunks it would have used, so the rest of the pipeline
    (API layer, TTS, event demo rehearsal) can be built and tested before
    a real model call exists.
    """

    def generate(self, question: str, chunks: list[RetrievedChunk]) -> LLMResponse:
        if not chunks:
            return LLMResponse(text=settings.low_confidence_message_km, used_fallback=True)
        top = chunks[0]
        preview = top.text[:120]
        return LLMResponse(
            text=f"[MOCK ANSWER based on '{top.source}']: {preview}...",
            used_fallback=False,
        )

    def generate_smalltalk(self, text: str) -> str:
        return f"[MOCK SMALLTALK REPLY to '{text}']"
    
    def classify_offtopic(self, question: str) -> bool:
        return False


class GeminiLLMClient(BaseLLMClient):
    """
    Real Gemini integration via the Interactions API (GA as of June 2026,
    the currently recommended interface -- see
    ai.google.dev/gemini-api/docs/interactions-overview).
    Requires GEMINI_API_KEY set in .env.
    """

    def __init__(self):
        from google import genai  # local import: only needed when this provider is active
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to your .env file "
                "(copy from .env.example) before using KAIBOT_LLM_PROVIDER=gemini."
            )
        self._client = genai.Client(api_key=api_key)

    def generate(self, question: str, chunks: list[RetrievedChunk]) -> LLMResponse:
        user_turn = build_user_turn(question, chunks)
        interaction = self._client.interactions.create(
            model=settings.llm_model,
            system_instruction=SYSTEM_PROMPT_KM,
            input=user_turn,
        )
        return LLMResponse(text=interaction.output_text, used_fallback=False)

    def generate_smalltalk(self, text: str) -> str:
        interaction = self._client.interactions.create(
            model=settings.llm_model,
            system_instruction=SYSTEM_PROMPT_SMALLTALK_KM,
            input=text,
        )
        return interaction.output_text
    
    def classify_offtopic(self, question: str) -> bool:
        interaction = self._client.interactions.create(
            model=settings.llm_model,
            system_instruction=SYSTEM_PROMPT_OFFTOPIC_CHECK_KM,
            input=question,
        )
        return interaction.output_text.strip().lower().startswith("offtopic")


class ClaudeLLMClient(BaseLLMClient):
    """Stub: wire up the Anthropic SDK here if Claude is chosen instead of Gemini."""

    def generate(self, question: str, chunks: list[RetrievedChunk]) -> LLMResponse:
        raise NotImplementedError(
            "Wire up anthropic.Anthropic().messages.create(...) here, passing "
            "SYSTEM_PROMPT_KM as `system` and build_user_turn(...) as the user message."
        )

    def generate_smalltalk(self, text: str) -> str:
        raise NotImplementedError(
            "Wire up anthropic.Anthropic().messages.create(...) here, passing "
            "SYSTEM_PROMPT_SMALLTALK_KM as `system`."
        )

    def classify_offtopic(self, question: str) -> bool:
        raise NotImplementedError(
            "Wire up anthropic.Anthropic().messages.create(...) here, passing "
            "SYSTEM_PROMPT_OFFTOPIC_CHECK_KM as `system`."
        )

def get_llm_client() -> BaseLLMClient:
    provider = settings.llm_provider
    if provider == "mock":
        return MockLLMClient()
    if provider == "gemini":
        return GeminiLLMClient()
    if provider == "claude":
        return ClaudeLLMClient()
    raise ValueError(f"Unknown LLM provider: {provider}")


def answer_question(question: str, chunks: list[RetrievedChunk], low_confidence: bool) -> LLMResponse:
    """
    Single entry point used by the API layer. Enforces the fallback rule
    at the boundary so no code path can accidentally let a low-confidence
    retrieval reach the LLM and get an improvised answer.
    """
    if low_confidence:
        return LLMResponse(text=settings.low_confidence_message_km, used_fallback=True)
    client = get_llm_client()
    return client.generate(question, chunks)


def answer_smalltalk(text: str) -> str:
    """
    Generates a natural small-talk reply via the LLM (no RAG context, so
    it structurally cannot give ungrounded farming advice -- there's
    nothing for it to draw from). Falls back to the static greeting
    message if the API call fails for any reason (network, quota, bad
    key), so a "hi" can never crash or hang the demo -- real farming
    questions still go through the untouched answer_question() safety path.
    """
    try:
        client = get_llm_client()
        return client.generate_smalltalk(text)
    except Exception as e:
        print(f"[answer_smalltalk] falling back to static message: {e}")
        return settings.greeting_response_km

def is_offtopic(question: str) -> bool:
    """
    Only called when retrieval already returned low_confidence=True.
    Distinguishes "real farming question, we just lack data" from
    "not about farming at all" so the fallback message can be more
    specific. Defaults to False (treat as farming-related, use the
    existing safety message) if the classification call itself fails --
    never let a classifier error produce a wrong/misleading label.
    """
    try:
        client = get_llm_client()
        return client.classify_offtopic(question)
    except Exception as e:  # noqa: BLE001 -- external API call, must degrade safely
        print(f"[is_offtopic] defaulting to False (farming) due to error: {e}")
        return False