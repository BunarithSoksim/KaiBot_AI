"""Thin HTTP client that forwards questions to the KaiBot backend.

This is the "adapter" piece described in the Jul 14 decision log:
Telegram sends a message -> this client forwards it to the same /chat
(or /chat/voice) endpoint the website already calls -> the backend's
answer is relayed back to the farmer on Telegram. No RAG/LLM logic
lives here -- that all stays in the FastAPI backend.

NOTE: If your actual /chat request/response schema differs from what's
assumed below (e.g. the request key isn't "question", or the response
doesn't include "answer"/"sources"/"low_confidence"), only this file
needs to change -- adjust the payload in `ask_text`/`ask_voice` and the
field names in `_parse_response` to match your real FastAPI route.
"""
from __future__ import annotations

from dataclasses import dataclass

import httpx


class KaiBotClientError(Exception):
    """Raised when the KaiBot backend can't be reached or returns an error."""


@dataclass(frozen=True)
class ChatResponse:
    answer: str
    sources: list[str]
    low_confidence: bool


class KaiBotClient:
    """Calls the KaiBot FastAPI backend's /chat and /chat/voice endpoints."""

    def __init__(self, base_url: str, timeout_seconds: float = 30.0) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    async def ask_text(self, question: str, language: str = "km") -> ChatResponse:
        """Send a text question to /chat and return the parsed answer.

        `language` is "km" or "en" -- forwarded to the backend's
        ChatRequest.language field so it picks the matching system
        prompt and fallback messages instead of defaulting to Khmer.
        """
        url = f"{self._base_url}/chat"
        payload = {"question": question, "language": language}
        data = await self._post_json(url, payload)
        return self._parse_response(data)

    async def ask_voice(
        self, audio_bytes: bytes, filename: str = "voice.ogg", language: str = "km"
    ) -> ChatResponse:
        """Send a voice clip to /chat/voice and return the parsed answer.

        `language` selects the STT/TTS language on the backend (km-KH vs
        en-US) -- sent as a form field alongside the audio file, matching
        FastAPI's Form(...) parameter on /chat/voice.
        """
        url = f"{self._base_url}/chat/voice"
        files = {"audio": (filename, audio_bytes, "audio/ogg")}
        form_data = {"language": language}
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, files=files, data=form_data)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise KaiBotClientError("KaiBot backend timed out on voice request") from exc
        except httpx.HTTPStatusError as exc:
            raise KaiBotClientError(
                f"KaiBot backend returned {exc.response.status_code} for voice request"
            ) from exc
        except httpx.HTTPError as exc:
            raise KaiBotClientError("Could not reach KaiBot backend for voice request") from exc

        return self._parse_response(data)

    async def _post_json(self, url: str, payload: dict[str, object]) -> dict[str, object]:
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(url, json=payload)
                response.raise_for_status()
                return response.json()
        except httpx.TimeoutException as exc:
            raise KaiBotClientError("KaiBot backend timed out") from exc
        except httpx.HTTPStatusError as exc:
            raise KaiBotClientError(
                f"KaiBot backend returned {exc.response.status_code}"
            ) from exc
        except httpx.HTTPError as exc:
            raise KaiBotClientError("Could not reach KaiBot backend") from exc

    @staticmethod
    def _parse_response(data: dict[str, object]) -> ChatResponse:
        try:
            return ChatResponse(
                answer=data["answer"],  # type: ignore[arg-type]
                sources=data.get("sources", []),  # type: ignore[arg-type]
                low_confidence=bool(data.get("low_confidence", False)),
            )
        except KeyError as exc:
            raise KaiBotClientError(
                f"Unexpected response shape from KaiBot backend: missing {exc}"
            ) from exc
