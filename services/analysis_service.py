"""
Provides market analysis:
- Rule-based analysis (always available)
- AI-powered analysis via OpenAI (if OPENAI_API_KEY is set)
"""

from __future__ import annotations

import logging

from services.market_data import MarketData
from utils.config import OPENAI_API_KEY

logger = logging.getLogger(__name__)


# ── Rule-based analysis ──────────────────────────────────────────────────────

def rule_based_analysis(data: MarketData) -> tuple[str, str]:
    """
    Returns (tech_signal, overall_conclusion).
    """
    signals: list[str] = []
    score = 0  # positive = bullish, negative = bearish

    # SMA cross
    if data.sma20 > data.sma50:
        signals.append("✅ SMA20 выше SMA50 — краткосрочный тренд позитивный.")
        score += 1
    else:
        signals.append("⚠️ SMA20 ниже SMA50 — краткосрочный тренд под давлением.")
        score -= 1

    # 30-day price change
    if data.change_30d > 15:
        signals.append(
            f"📈 Цена выросла на {data.change_30d:.1f}% за 30 дней — "
            "возможен риск коррекции после сильного роста."
        )
        score -= 0.5
    elif data.change_30d < -15:
        signals.append(
            f"📉 Цена упала на {abs(data.change_30d):.1f}% за 30 дней — "
            "возможна перепроданность, стоит следить за разворотом."
        )
        score += 0.5
    elif data.change_30d > 5:
        signals.append(f"📈 Умеренный рост за 30 дней: {data.change_30d:.1f}%.")
        score += 0.3
    elif data.change_30d < -5:
        signals.append(f"📉 Умеренное снижение за 30 дней: {data.change_30d:.1f}%.")
        score -= 0.3

    # Volatility
    if data.volatility_30d > 50:
        signals.append(
            f"⚡ Волатильность очень высокая ({data.volatility_30d:.0f}% годовых) — повышенный риск."
        )
        score -= 0.5
    elif data.volatility_30d > 30:
        signals.append(
            f"⚡ Волатильность умеренно высокая ({data.volatility_30d:.0f}% годовых)."
        )
    else:
        signals.append(
            f"📊 Волатильность умеренная ({data.volatility_30d:.0f}% годовых)."
        )

    # RSI
    if data.rsi is not None:
        if data.rsi > 70:
            signals.append(f"🔴 RSI = {data.rsi:.0f} — зона перекупленности, возможна коррекция.")
            score -= 0.5
        elif data.rsi < 30:
            signals.append(f"🟢 RSI = {data.rsi:.0f} — зона перепроданности, возможен отскок.")
            score += 0.5
        else:
            signals.append(f"🟡 RSI = {data.rsi:.0f} — нейтральная зона.")

    tech_signal = "\n".join(signals)

    # Overall conclusion
    if score >= 1:
        conclusion = "📗 <b>Скорее позитивный сценарий</b> — технические индикаторы указывают на умеренный оптимизм."
    elif score <= -1:
        conclusion = "📕 <b>Осторожный / негативный сценарий</b> — ряд индикаторов сигнализирует о рисках."
    else:
        conclusion = "📘 <b>Нейтральный сценарий</b> — рынок в состоянии неопределённости."

    return tech_signal, conclusion


# ── AI analysis via OpenAI ───────────────────────────────────────────────────

def ai_analysis(data: MarketData, news_text: str) -> str | None:
    """
    Send market data and news to OpenAI and return analytical summary.
    Returns None if OPENAI_API_KEY is not set or request fails.
    """
    if not OPENAI_API_KEY:
        return None

    try:
        from openai import OpenAI

        client = OpenAI(api_key=OPENAI_API_KEY)

        prompt = _build_ai_prompt(data, news_text)

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Ты опытный финансовый аналитик. "
                        "Дай краткий аналитический обзор акции на русском языке. "
                        "Не более 200 слов. "
                        "Обязательно упомяни, что это не инвестиционная рекомендация."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=400,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()

    except ImportError:
        logger.warning("openai package not installed. Falling back to rule-based analysis.")
        return None
    except Exception as exc:
        logger.error("OpenAI API error: %s", exc)
        return None


def _build_ai_prompt(data: MarketData, news_text: str) -> str:
    rsi_str = f"{data.rsi:.1f}" if data.rsi is not None else "н/д"
    return (
        f"Акция: {data.company_name} ({data.ticker})\n"
        f"Последняя цена: {data.last_price:.2f} {data.currency}\n"
        f"Изменение за 7 дней: {data.change_7d:+.2f}%\n"
        f"Изменение за 30 дней: {data.change_30d:+.2f}%\n"
        f"Изменение за 180 дней: {data.change_180d:+.2f}%\n"
        f"Волатильность (30д, годовая): {data.volatility_30d:.1f}%\n"
        f"SMA20: {data.sma20:.2f}\n"
        f"SMA50: {data.sma50:.2f}\n"
        f"RSI(14): {rsi_str}\n\n"
        f"Последние новости:\n{news_text}\n\n"
        "Дай краткий аналитический обзор с учётом всех данных."
    )


# ── Main entry point ─────────────────────────────────────────────────────────

def get_analysis(data: MarketData, news_text: str) -> tuple[str, str]:
    """
    Returns (tech_signal, overall_conclusion).
    Uses AI if available, otherwise rule-based.
    """
    tech_signal, rule_conclusion = rule_based_analysis(data)

    ai_result = ai_analysis(data, news_text)
    if ai_result:
        return tech_signal, f"🤖 <b>AI-анализ:</b>\n{ai_result}"

    return tech_signal, rule_conclusion
