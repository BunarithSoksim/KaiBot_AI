from __future__ import annotations

import httpx
import pytest

from src.telegram_bot.kaibot_client import KaiBotClient, KaiBotClientError

pytestmark = pytest.mark.asyncio


async def test_ask_text_returns_parsed_response(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_post(self: httpx.AsyncClient, url: str, json: dict | None = None, **kwargs: object) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "answer": "Split nitrogen into two applications for wet-season rice.",
                "sources": ["rice_fertilizer.json"],
                "low_confidence": False,
            },
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    client = KaiBotClient(base_url="http://localhost:8000")
    result = await client.ask_text("how do I fertilize rice?")

    assert "nitrogen" in result.answer
    assert result.sources == ["rice_fertilizer.json"]
    assert result.low_confidence is False


async def test_ask_text_raises_on_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_post(self: httpx.AsyncClient, url: str, json: dict | None = None, **kwargs: object) -> httpx.Response:
        return httpx.Response(500, json={"detail": "boom"}, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    client = KaiBotClient(base_url="http://localhost:8000")

    with pytest.raises(KaiBotClientError):
        await client.ask_text("anything")


async def test_ask_text_raises_on_unexpected_response_shape(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_post(self: httpx.AsyncClient, url: str, json: dict | None = None, **kwargs: object) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "shape"}, request=httpx.Request("POST", url))

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    client = KaiBotClient(base_url="http://localhost:8000")

    with pytest.raises(KaiBotClientError, match="Unexpected response shape"):
        await client.ask_text("anything")


async def test_ask_voice_sends_multipart_and_parses_response(monkeypatch: pytest.MonkeyPatch) -> None:
    async def fake_post(self: httpx.AsyncClient, url: str, files: dict | None = None, **kwargs: object) -> httpx.Response:
        assert files is not None
        assert "audio" in files
        return httpx.Response(
            200,
            json={"answer": "offline cache answer", "sources": ["(offline cache)"], "low_confidence": False},
            request=httpx.Request("POST", url),
        )

    monkeypatch.setattr(httpx.AsyncClient, "post", fake_post)

    client = KaiBotClient(base_url="http://localhost:8000")
    result = await client.ask_voice(b"fake-ogg-bytes")

    assert result.answer == "offline cache answer"
