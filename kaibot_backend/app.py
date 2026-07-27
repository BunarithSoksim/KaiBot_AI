"""
KaiBot API layer.

Endpoints:
  POST /chat        - text in, text out (+ metadata about confidence/sources)
  POST /chat/voice   - audio in, transcribes, runs the same pipeline as /chat,
                       returns text + (eventually) synthesized audio

Kept deliberately thin: this file should only ever orchestrate calls to
rag/retriever.py, llm/client.py, and voice/stt_tts.py -- no business logic
lives here, so any of those layers can be swapped or unit-tested alone.
"""
from fastapi import FastAPI, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
from llm.client import answer_question, answer_smalltalk, is_offtopic
from llm.intent import is_greeting
from llm.offline_fallback import find_offline_answer
from rag.retriever import Retriever

app = FastAPI(title="KaiBot API")
# Allow CORS for local development so browser preflight (OPTIONS)
# requests succeed when the frontend is served from a different origin.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

retriever = Retriever()


class ChatRequest(BaseModel):
    question: str
    province: str | None = None  # optional filter, e.g. "Preah Vihear"
    category: str | None = None  # optional filter: "crop" | "livestock" | "market"


class ChatResponse(BaseModel):
    answer: str
    low_confidence: bool
    sources: list[str]


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    if is_greeting(req.question):
        return ChatResponse(answer=answer_smalltalk(req.question), low_confidence=False, sources=[])

    try:
        result = retriever.retrieve(req.question, province_filter=req.province,
                                     category_filter=req.category)

        if result.low_confidence and is_offtopic(req.question):
            return ChatResponse(answer=settings.offtopic_message_km, low_confidence=False, sources=[])

        response = answer_question(req.question, result.chunks, result.low_confidence)
        return ChatResponse(
            answer=response.text,
            low_confidence=response.used_fallback,
            sources=[] if response.used_fallback else sorted({c.source for c in result.chunks}),
        )
    except Exception as e:  # noqa: BLE001 -- Gemini unreachable (network/quota/etc), degrade to offline cache
        print(f"[chat] pipeline unreachable, falling back to offline cache: {e}")
        cached = find_offline_answer(req.question)
        if cached:
            return ChatResponse(answer=cached, low_confidence=False, sources=["(offline cache)"])
        return ChatResponse(answer=settings.no_internet_message_km, low_confidence=True, sources=[])


@app.post("/chat/voice", response_model=ChatResponse)
async def chat_voice(audio: UploadFile, province: str | None = None,
                      category: str | None = None) -> ChatResponse:
    from voice.stt_tts import get_stt  # local import keeps startup light

    audio_bytes = await audio.read()
    transcription = get_stt().transcribe(audio_bytes)

    if is_greeting(transcription.text):
        return ChatResponse(answer=answer_smalltalk(transcription.text), low_confidence=False, sources=[])

    try:
        result = retriever.retrieve(transcription.text, province_filter=province,
                                     category_filter=category)

        if result.low_confidence and is_offtopic(transcription.text):
            return ChatResponse(answer=settings.offtopic_message_km, low_confidence=False, sources=[])

        response = answer_question(transcription.text, result.chunks, result.low_confidence)
        return ChatResponse(
            answer=response.text,
            low_confidence=response.used_fallback,
            sources=[] if response.used_fallback else sorted({c.source for c in result.chunks}),
        )
    except Exception as e:  # noqa: BLE001 -- Gemini unreachable (network/quota/etc), degrade to offline cache
        print(f"[chat_voice] pipeline unreachable, falling back to offline cache: {e}")
        cached = find_offline_answer(transcription.text)
        if cached:
            return ChatResponse(answer=cached, low_confidence=False, sources=["(offline cache)"])
        return ChatResponse(answer=settings.no_internet_message_km, low_confidence=True, sources=[])


@app.get("/health")
def health():
    return {"status": "ok"}