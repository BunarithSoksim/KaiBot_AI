"""Configuration for the KaiBot Telegram adapter.

Loads required settings from environment variables. Never hard-code
tokens or URLs here -- set them via a `.env` file (not committed) or
your deployment platform's environment variable settings.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")

class ConfigError(Exception):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class TelegramBotConfig:
    telegram_token: str
    kaibot_api_base_url: str
    request_timeout_seconds: float = 30.0


def load_config() -> TelegramBotConfig:
    """Load and validate configuration from environment variables.

    Required env vars:
        TELEGRAM_BOT_TOKEN   - token issued by @BotFather on Telegram
        KAIBOT_API_BASE_URL  - base URL of the KaiBot FastAPI backend,
                                e.g. http://localhost:8000 or the hosted URL

    Optional env vars:
        KAIBOT_REQUEST_TIMEOUT_SECONDS - HTTP timeout for backend calls
                                          (default: 30)

    Raises:
        ConfigError: if a required variable is missing/empty or an
            optional numeric variable can't be parsed.
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    base_url = os.environ.get("KAIBOT_API_BASE_URL", "").strip()

    if not token:
        raise ConfigError("TELEGRAM_BOT_TOKEN is not set")
    if not base_url:
        raise ConfigError("KAIBOT_API_BASE_URL is not set")

    timeout_raw = os.environ.get("KAIBOT_REQUEST_TIMEOUT_SECONDS", "30")
    try:
        timeout = float(timeout_raw)
    except ValueError as exc:
        raise ConfigError(
            f"KAIBOT_REQUEST_TIMEOUT_SECONDS must be a number, got {timeout_raw!r}"
        ) from exc

    return TelegramBotConfig(
        telegram_token=token,
        kaibot_api_base_url=base_url.rstrip("/"),
        request_timeout_seconds=timeout,
    )
