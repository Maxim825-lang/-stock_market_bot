from datetime import datetime


def format_price(price: float, currency: str = "") -> str:
    """Format price with currency symbol."""
    if currency:
        return f"{price:,.2f} {currency}"
    return f"{price:,.2f}"


def format_percent(value: float) -> str:
    """Format percentage change with sign."""
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


def format_date(dt) -> str:
    """Format datetime to readable string."""
    if isinstance(dt, str):
        return dt
    try:
        return dt.strftime("%d.%m.%Y")
    except Exception:
        return str(dt)


def format_analysis_message(
    ticker: str,
    company_name: str,
    price: float,
    currency: str,
    change_7d: float,
    change_30d: float,
    change_180d: float,
    volatility: float,
    sma20: float,
    sma50: float,
    rsi: float | None,
    tech_signal: str,
    news_text: str,
    overall_conclusion: str,
) -> str:
    """Build the full analysis message for Telegram."""

    rsi_line = f"  • RSI(14): {rsi:.1f}\n" if rsi is not None else ""

    msg = (
        f"📊 <b>Анализ: {company_name} ({ticker})</b>\n\n"
        f"💰 <b>Последняя цена:</b> {format_price(price, currency)}\n\n"
        f"📈 <b>Изменение цены:</b>\n"
        f"  • За 7 дней: {format_percent(change_7d)}\n"
        f"  • За 30 дней: {format_percent(change_30d)}\n"
        f"  • За 180 дней: {format_percent(change_180d)}\n\n"
        f"⚡ <b>Волатильность (30д):</b> {volatility:.1f}%\n\n"
        f"📐 <b>Технические индикаторы:</b>\n"
        f"  • SMA20: {format_price(sma20)}\n"
        f"  • SMA50: {format_price(sma50)}\n"
        f"{rsi_line}\n"
        f"🔍 <b>Технический вывод:</b>\n{tech_signal}\n\n"
        f"📰 <b>Последние новости:</b>\n{news_text}\n\n"
        f"🧠 <b>Общий вывод:</b>\n{overall_conclusion}\n\n"
        f"⚠️ <i>Это не инвестиционная рекомендация, а аналитический обзор "
        f"на основе доступных данных. Все решения вы принимаете самостоятельно.</i>"
    )
    return msg


def format_news_item(title: str, source: str, published_at: str, url: str) -> str:
    """Format a single news item."""
    date_str = published_at[:10] if len(published_at) >= 10 else published_at
    return f"• <b>{title}</b>\n  {source} | {date_str}\n  <a href='{url}'>Читать →</a>"
