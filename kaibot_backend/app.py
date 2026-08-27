"""
SmartKasekor API layer.
"""
import traceback

from fastapi import FastAPI, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from pydantic import BaseModel

from config import settings
from llm.client import answer_question, answer_smalltalk, is_offtopic
from llm.intent import is_greeting
from llm.offline_fallback import find_offline_answer
from rag.retriever import Retriever

app = FastAPI(title="SmartKasekor API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = Retriever()


def _normalize_language(language: str | None) -> str:
    """Only 'km' and 'en' are supported; anything else defaults to Khmer."""
    return "en" if language == "en" else "km"


def _no_internet_message(language: str) -> str:
    return settings.no_internet_message_en if language == "en" else settings.no_internet_message_km


def _offtopic_message(language: str) -> str:
    return settings.offtopic_message_en if language == "en" else settings.offtopic_message_km


class ChatRequest(BaseModel):
    question: str
    province: str | None = None
    category: str | None = None  # "crop" | "livestock" | "market"
    language: str = "km"  # "km" | "en"


class TTSRequest(BaseModel):
    text: str
    language: str = "km"


class ChatResponse(BaseModel):
    answer: str
    low_confidence: bool
    sources: list[str]
    transcript: str | None = None


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    language = _normalize_language(req.language)

    if is_greeting(req.question):
        return ChatResponse(answer=answer_smalltalk(req.question, language=language), low_confidence=False, sources=[])

    try:
        result = retriever.retrieve(req.question, province_filter=req.province, category_filter=req.category)

        if result.low_confidence and is_offtopic(req.question):
            return ChatResponse(answer=_offtopic_message(language), low_confidence=False, sources=[])

        response = answer_question(req.question, result.chunks, result.low_confidence, language=language)
        return ChatResponse(
            answer=response.text,
            low_confidence=response.used_fallback,
            sources=[] if response.used_fallback else sorted({c.source for c in result.chunks}),
        )
    except Exception as e:  # noqa: BLE001 -- Gemini unreachable (network/quota/etc), degrade to offline cache
        print(f"[chat] pipeline unreachable, falling back to offline cache: {e}")
        traceback.print_exc()
        cached = find_offline_answer(req.question)
        if cached:
            return ChatResponse(answer=cached, low_confidence=False, sources=["(offline cache)"])
        return ChatResponse(answer=_no_internet_message(language), low_confidence=True, sources=[])


@app.post("/chat/voice", response_model=ChatResponse)
async def chat_voice(
    audio: UploadFile,
    province: str | None = Form(None),
    category: str | None = Form(None),
    language: str | None = Form(None),
) -> ChatResponse:
    from voice.stt_tts import get_stt  # local import keeps startup light

    lang = _normalize_language(language)
    audio_bytes = await audio.read()
    transcription = get_stt().transcribe(audio_bytes, language=lang)

    if is_greeting(transcription.text):
        return ChatResponse(
            answer=answer_smalltalk(transcription.text, language=lang),
            low_confidence=False,
            sources=[],
            transcript=transcription.text,
        )

    try:
        result = retriever.retrieve(transcription.text, province_filter=province, category_filter=category)

        if result.low_confidence and is_offtopic(transcription.text):
            return ChatResponse(
                answer=_offtopic_message(lang),
                low_confidence=False,
                sources=[],
                transcript=transcription.text,
            )

        response = answer_question(transcription.text, result.chunks, result.low_confidence, language=lang)
        return ChatResponse(
            answer=response.text,
            low_confidence=response.used_fallback,
            sources=[] if response.used_fallback else sorted({c.source for c in result.chunks}),
            transcript=transcription.text,
        )
    except Exception as e:  # noqa: BLE001 -- Gemini unreachable (network/quota/etc), degrade to offline cache
        traceback.print_exc()
        print(f"[chat_voice] pipeline unreachable, falling back to offline cache: {e}")
        cached = find_offline_answer(transcription.text)
        if cached:
            return ChatResponse(answer=cached, low_confidence=False, sources=["(offline cache)"], transcript=transcription.text)
        return ChatResponse(answer=_no_internet_message(lang), low_confidence=True, sources=[], transcript=transcription.text)


@app.post("/tts")
def text_to_speech(req: TTSRequest) -> Response:
    from voice.stt_tts import get_tts  # local import keeps startup light

    if not req.text.strip():
        return Response(status_code=400)

    try:
        audio_bytes = get_tts().synthesize(req.text, language=_normalize_language(req.language))
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:  # noqa: BLE001 -- Google TTS unreachable/failed, degrade to empty response
        print(f"[tts] synthesis failed: {e}")
        return Response(status_code=503)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}