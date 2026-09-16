"""Telegram adapter for KaiBot.

Thin frontend only -- no RAG/LLM logic lives here. Every farmer message
is forwarded to the existing KaiBot FastAPI backend (the same one the
website calls) via KaiBotClient, and the backend's answer is relayed
back to the farmer on Telegram.

Run:
    python -m src.telegram_bot.bot

Requires (add to requirements.txt):
    python-telegram-bot>=20
    httpx
"""
from __future__ import annotations

import logging

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from .config import ConfigError, load_config
from .kaibot_client import KaiBotClient, KaiBotClientError
from .language import detect_language

logger = logging.getLogger(__name__)

# Matches the tone of the existing offline-fallback messages in the
# backend (see KaiBot_Decision_Log.md) -- honest, simple, Khmer-first.
FALLBACK_ERROR_MESSAGE_KM = (
    "សុំទោស ខ្ញុំមិនអាចភ្ជាប់ទៅម៉ាស៊ីនមេបានទេឥឡូវនេះ។ សូមព្យាយាមម្តងទៀតបន្តិចទៀត។"
)

_LANGUAGE_SET_REPLIES = {
    "km": "កំណត់ភាសាទៅជាខ្មែរ។ សំណួរសំឡេងបន្ទាប់ៗនឹងឆ្លើយជាភាសាខ្មែរ។",
    "en": "Language set to English. Future voice questions will be answered in English.",
}
_LANGUAGE_USAGE_MESSAGE = "Usage: /language km  or  /language en"


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle an incoming text message: forward to /chat, reply with the answer.

    Language is auto-detected per message from the script used (Khmer vs
    Latin) -- text doesn't need an explicit /language preference the way
    voice does, since we can read the actual characters typed.
    """
    if update.message is None or update.message.text is None:
        return

    client: KaiBotClient = context.bot_data["kaibot_client"]
    question = update.message.text
    language = detect_language(question)

    try:
        result = await client.ask_text(question, language=language)
    except KaiBotClientError:
        logger.exception("Failed to get answer for text question")
        await update.message.reply_text(FALLBACK_ERROR_MESSAGE_KM)
        return

    await update.message.reply_text(result.answer)


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle an incoming voice message: forward the audio to /chat/voice.

    Unlike text, we can't detect the spoken language from raw audio bytes
    without an extra transcription pass, so this uses the farmer's stored
    /language preference (default "km") rather than auto-detecting.
    """
    if update.message is None or update.message.voice is None:
        return

    client: KaiBotClient = context.bot_data["kaibot_client"]
    language = context.user_data.get("language", "km") if context.user_data is not None else "km"

    try:
        telegram_file = await update.message.voice.get_file()
        audio_bytes = bytes(await telegram_file.download_as_bytearray())
    except TelegramError:
        logger.exception("Failed to download voice message from Telegram")
        await update.message.reply_text(FALLBACK_ERROR_MESSAGE_KM)
        return

    try:
        result = await client.ask_voice(audio_bytes, language=language)
    except KaiBotClientError:
        logger.exception("Failed to get answer for voice question")
        await update.message.reply_text(FALLBACK_ERROR_MESSAGE_KM)
        return

    await update.message.reply_text(result.answer)


async def handle_language_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /language km|en -- sets the farmer's voice-question language.

    Text messages don't need this (auto-detected per message), but voice
    messages do, since the language can't be read off raw audio bytes.
    """
    if update.message is None:
        return

    args = context.args or []
    if not args or args[0].lower() not in ("km", "en"):
        await update.message.reply_text(_LANGUAGE_USAGE_MESSAGE)
        return

    language = args[0].lower()
    if context.user_data is not None:
        context.user_data["language"] = language

    await update.message.reply_text(_LANGUAGE_SET_REPLIES[language])


def build_application() -> Application:
    """Construct the Telegram Application with handlers wired up.

    Raises:
        ConfigError: if required environment variables are missing.
    """
    config = load_config()
    client = KaiBotClient(
        base_url=config.kaibot_api_base_url,
        timeout_seconds=config.request_timeout_seconds,
    )

    application = Application.builder().token(config.telegram_token).build()
    application.bot_data["kaibot_client"] = client

    application.add_handler(CommandHandler("language", handle_language_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))

    return application


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    try:
        application = build_application()
    except ConfigError:
        logger.exception("Configuration error -- check your .env / environment variables")
        raise

    logger.info("Starting KaiBot Telegram bot (polling mode)")
    application.run_polling()


if __name__ == "__main__":
    main()
