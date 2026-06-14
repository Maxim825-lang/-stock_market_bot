"""
Bot setup and application entry point.
"""

from __future__ import annotations

import logging

from telegram import BotCommand
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

from bot.handlers import (
    cmd_start,
    cmd_help,
    cmd_analyze,
    cmd_unknown,
    callback_handler,
    handle_text_message,
)
from utils.config import TELEGRAM_BOT_TOKEN

logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Set bot commands visible in Telegram menu."""
    await application.bot.set_my_commands([
        BotCommand("start", "Главное меню"),
        BotCommand("help", "Помощь и список команд"),
        BotCommand("analyze", "Анализ акции: /analyze AAPL"),
    ])


def create_app() -> Application:
    if not TELEGRAM_BOT_TOKEN:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN не задан. "
            "Создайте файл .env и добавьте туда токен бота."
        )

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("analyze", cmd_analyze))
    app.add_handler(CallbackQueryHandler(callback_handler))
    # Plain text messages — treated as analysis queries (e.g. "Сбербанк", "AAPL")
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.add_handler(MessageHandler(filters.COMMAND, cmd_unknown))

    return app


def run_bot() -> None:
    logging.basicConfig(
        format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        level=logging.INFO,
    )
    # Prevent httpx from logging full URLs that contain the bot token
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logger.info("Starting Stock Market Bot…")
    app = create_app()
    app.run_polling(drop_pending_updates=True)
