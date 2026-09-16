from __future__ import annotations

import pytest

from src.telegram_bot.config import ConfigError, load_config


def test_load_config_raises_when_token_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)
    monkeypatch.setenv("KAIBOT_API_BASE_URL", "http://localhost:8000")

    with pytest.raises(ConfigError, match="TELEGRAM_BOT_TOKEN"):
        load_config()


def test_load_config_raises_when_base_url_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "dummy-token")
    monkeypatch.delenv("KAIBOT_API_BASE_URL", raising=False)

    with pytest.raises(ConfigError, match="KAIBOT_API_BASE_URL"):
        load_config()


def test_load_config_strips_trailing_slash(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "dummy-token")
    monkeypatch.setenv("KAIBOT_API_BASE_URL", "http://localhost:8000/")
    monkeypatch.delenv("KAIBOT_REQUEST_TIMEOUT_SECONDS", raising=False)

    config = load_config()

    assert config.kaibot_api_base_url == "http://localhost:8000"


def test_load_config_rejects_non_numeric_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "dummy-token")
    monkeypatch.setenv("KAIBOT_API_BASE_URL", "http://localhost:8000")
    monkeypatch.setenv("KAIBOT_REQUEST_TIMEOUT_SECONDS", "not-a-number")

    with pytest.raises(ConfigError, match="KAIBOT_REQUEST_TIMEOUT_SECONDS"):
        load_config()
