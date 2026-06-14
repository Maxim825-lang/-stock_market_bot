"""
Telegram command, text, and callback handlers.
"""

from __future__ import annotations

import io
import logging

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from bot.keyboards import main_menu_keyboard, back_to_menu_keyboard
from services.ticker_resolver import resolve_ticker
from services.market_data import fetch_market_data
from services.chart_service import generate_chart
from services.news_service import fetch_news, format_news
from services.analysis_service import get_analysis
from utils.formatters import format_analysis_message

logger = logging.getLogger(__name__)

WELCOME_TEXT = (
    "👋 <b>Привет! Я бот для анализа рынка акций.</b>\n\n"
    "Я умею анализировать акции российских и американских компаний:\n"
    "• Исторические данные и цену\n"
    "• Технические индикаторы (SMA20, SMA50, RSI)\n"
    "• Последние новости\n"
    "• График цены за год\n"
    "• Общий аналитический вывод\n\n"
    "✍️ <b>Просто напиши название акции или тикер:</b>\n"
    "<code>Сбербанк</code>  <code>Газпром</code>  <code>Apple</code>  <code>Tesla</code>\n"
    "<code>SBER</code>  <code>AAPL</code>  <code>TSLA</code>  <code>NVDA</code>\n\n"
    "📌 Или используй команду: <code>/analyze AAPL</code>\n\n"
    "Выбери компанию из меню ниже или напиши сам 👇"
)

HELP_TEXT = (
    "📖 <b>Справка</b>\n\n"
    "✍️ <b>Самый простой способ — просто написать:</b>\n"
    "<code>Сбербанк</code>  →  анализ Сбербанка\n"
    "<code>Apple</code>  →  анализ Apple\n"
    "<code>SBER</code>  →  анализ по тикеру\n"
    "<code>AAPL</code>  →  анализ по тикеру\n"
    "<code>Tesla</code>  →  анализ Tesla\n\n"
    "📌 <b>Команды:</b>\n"
    "<b>/start</b> — главное меню\n"
    "<b>/help</b> — эта справка\n"
    "<b>/analyze &lt;тикер&gt;</b> — анализ акции\n\n"
    "🇷🇺 <b>Российские акции:</b>\n"
    "<code>SBER</code> или <code>SBER.ME</code> — Сбербанк\n"
    "<code>GAZP</code> или <code>GAZP.ME</code> — Газпром\n"
    "<code>LKOH</code> или <code>LKOH.ME</code> — Лукойл\n"
    "<code>YDEX</code> или <code>YDEX.ME</code> — Яндекс\n"
    "<code>ROSN</code> или <code>ROSN.ME</code> — Роснефть\n"
    "<code>VTBR</code> или <code>VTBR.ME</code> — ВТБ\n\n"
    "🇺🇸 <b>Американские акции:</b>\n"
    "<code>AAPL</code> — Apple\n"
    "<code>TSLA</code> — Tesla\n"
    "<code>NVDA</code> — Nvidia\n"
    "<code>MSFT</code> — Microsoft\n"
    "<code>GOOGL</code> — Google\n"
    "<code>AMZN</code> — Amazon\n\n"
    "💡 Русские и английские названия тоже работают:\n"
    "<code>сбербанк</code>  <code>яндекс</code>  <code>газпром</code>\n"
    "<code>apple</code>  <code>tesla</code>  <code>nvidia</code>\n\n"
    "⚠️ <i>Это не инвестиционная рекомендация.</i>"
)

_UNKNOWN_INPUT_MSG = (
    "🤷 Не смог понять компанию или тикер.\n\n"
    "Попробуй написать, например:\n"
    "<code>Сбербанк</code>, <code>Газпром</code>, <code>Apple</code>, "
    "<code>Tesla</code>, <code>AAPL</code>, <code>SBER</code>"
)


# ── Command handlers ──────────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        WELCOME_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=main_menu_keyboard(),
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        HELP_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=back_to_menu_keyboard(),
    )


async def cmd_analyze(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /analyze <ticker or company name>."""
    args = context.args

    if not args:
        await update.message.reply_text(
            "❓ Укажите тикер или название компании.\n\n"
            "Примеры:\n"
            "<code>/analyze AAPL</code>\n"
            "<code>/analyze SBER</code>\n"
            "<code>/analyze сбербанк</code>",
            parse_mode=ParseMode.HTML,
        )
        return

    user_input = " ".join(args)
    await _run_analysis(update, context, user_input)


async def cmd_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "❓ Неизвестная команда. Попробуйте /help или /start.",
        parse_mode=ParseMode.HTML,
    )


# ── Free-text message handler ─────────────────────────────────────────────────

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle any plain text message as an analysis query.
    The user can type e.g. "Сбербанк", "Apple", "AAPL", "TSLA" directly.
    """
    text = (update.message.text or "").strip()
    if not text:
        return

    await _run_analysis(
        update,
        context,
        text,
        not_found_msg=_UNKNOWN_INPUT_MSG,
    )


# ── Callback query handler ────────────────────────────────────────────────────

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    data = query.data

    if data == "start":
        await query.message.reply_text(
            WELCOME_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=main_menu_keyboard(),
        )
    elif data == "help":
        await query.message.reply_text(
            HELP_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=back_to_menu_keyboard(),
        )
    elif data.startswith("analyze:"):
        ticker = data.split(":", 1)[1]
        await _run_analysis(update, context, ticker, message=query.message)


# ── Core analysis pipeline ────────────────────────────────────────────────────

async def _run_analysis(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_input: str,
    message=None,
    not_found_msg: str | None = None,
) -> None:
    """
    Shared analysis pipeline used by /analyze, free-text messages, and callbacks.

    not_found_msg: if set and the resolver didn't recognise the input AND market
    data is unavailable, reply with this text instead of the generic data error.
    """
    msg = message or update.message

    status_msg = await msg.reply_text(
        f"🔄 Анализирую <b>{user_input}</b>… Подождите немного.",
        parse_mode=ParseMode.HTML,
    )

    try:
        # 1. Resolve ticker
        resolution = resolve_ticker(user_input)

        if resolution.is_private:
            await status_msg.edit_text(
                f"🔒 <b>{resolution.company_name}</b>\n\n{resolution.private_message}",
                parse_mode=ParseMode.HTML,
                reply_markup=back_to_menu_keyboard(),
            )
            return

        ticker = resolution.ticker

        # 2. Fetch market data
        market_data = fetch_market_data(ticker)

        if market_data is None:
            # Show a friendlier "didn't understand" message when the input was not
            # a known company and we have a suitable fallback text to show.
            if not_found_msg and not resolution.is_known:
                await status_msg.edit_text(
                    not_found_msg,
                    parse_mode=ParseMode.HTML,
                    reply_markup=main_menu_keyboard(),
                )
            else:
                await status_msg.edit_text(
                    f"❌ Не удалось получить данные для <b>{ticker}</b>.\n\n"
                    "Возможные причины:\n"
                    "• Тикер не существует\n"
                    "• Нет подключения к интернету\n"
                    "• Сервис временно недоступен\n\n"
                    "Попробуйте другой тикер или воспользуйтесь /help.",
                    parse_mode=ParseMode.HTML,
                    reply_markup=back_to_menu_keyboard(),
                )
            return

        # Use resolved company name if the data source returned just the ticker symbol
        if market_data.company_name == ticker and resolution.company_name != ticker:
            market_data.company_name = resolution.company_name

        # 3. Fetch news
        news_items = fetch_news(market_data.company_name, ticker)
        news_text = format_news(news_items)

        # 4. Analysis
        tech_signal, overall_conclusion = get_analysis(market_data, news_text)

        # 5. Format message
        text = format_analysis_message(
            ticker=market_data.ticker,
            company_name=market_data.company_name,
            price=market_data.last_price,
            currency=market_data.currency,
            change_7d=market_data.change_7d,
            change_30d=market_data.change_30d,
            change_180d=market_data.change_180d,
            volatility=market_data.volatility_30d,
            sma20=market_data.sma20,
            sma50=market_data.sma50,
            rsi=market_data.rsi,
            tech_signal=tech_signal,
            news_text=news_text,
            overall_conclusion=overall_conclusion,
        )

        # 6. Generate chart
        chart_bytes = generate_chart(ticker, market_data.company_name, market_data.history)

        # 7. Send result
        await status_msg.delete()

        if chart_bytes:
            await msg.reply_photo(
                photo=io.BytesIO(chart_bytes),
                caption=text[:1024],
                parse_mode=ParseMode.HTML,
            )
            if len(text) > 1024:
                await msg.reply_text(
                    text,
                    parse_mode=ParseMode.HTML,
                    reply_markup=back_to_menu_keyboard(),
                )
        else:
            await msg.reply_text(
                text,
                parse_mode=ParseMode.HTML,
                reply_markup=back_to_menu_keyboard(),
            )

    except Exception as exc:
        logger.error("Unexpected error during analysis of '%s': %s", user_input, exc, exc_info=True)
        try:
            await status_msg.edit_text(
                "⚠️ Произошла непредвиденная ошибка. Попробуйте позже или введите другой тикер.",
                reply_markup=back_to_menu_keyboard(),
            )
        except Exception:
            pass
