"""
Fetches and processes market data.
Uses yfinance for US stocks; falls back to MOEX ISS API for Russian tickers (*.ME).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

import pandas as pd

logger = logging.getLogger(__name__)


@dataclass
class MarketData:
    ticker: str
    company_name: str
    currency: str
    last_price: float
    change_7d: float       # percent
    change_30d: float      # percent
    change_180d: float     # percent
    volatility_30d: float  # annualised percent
    sma20: float
    sma50: float
    rsi: float | None
    history: pd.DataFrame = field(repr=False)


def fetch_market_data(ticker: str) -> MarketData | None:
    """
    Download 1-year OHLCV data and compute indicators.

    For US tickers uses yfinance.
    For Russian tickers (*.ME) tries yfinance first, then falls back to MOEX ISS API.
    Returns None if ticker is invalid or data is unavailable from both sources.
    """
    data = _from_yfinance(ticker)
    if data is not None:
        return data

    moex_short = _moex_ticker(ticker)
    if moex_short:
        logger.info(
            "yfinance returned no data for %s; trying MOEX ISS (ticker: %s)",
            ticker, moex_short,
        )
        return _from_moex(ticker, moex_short)

    return None


# ── Source-specific fetchers ─────────────────────────────────────────────────

def _from_yfinance(ticker: str) -> MarketData | None:
    try:
        import yfinance as yf
    except ImportError:
        logger.error("yfinance is not installed. Run: pip install yfinance")
        return None

    try:
        tkr = yf.Ticker(ticker)
        hist = tkr.history(period="1y")

        if hist is None or hist.empty:
            logger.debug("yfinance: empty history for %s", ticker)
            return None

        info: dict = {}
        try:
            info = tkr.info or {}
        except Exception:
            pass

        company_name = info.get("longName") or info.get("shortName") or ticker
        currency = info.get("currency", "")

        return _build_market_data(ticker, company_name, currency, hist)

    except Exception as exc:
        logger.error("yfinance error for %s: %s", ticker, exc)
        return None


def _from_moex(ticker: str, moex_ticker: str) -> MarketData | None:
    try:
        from services.moex_data import fetch_moex_history
        hist = fetch_moex_history(moex_ticker)
    except Exception as exc:
        logger.error("MOEX fetch error for %s: %s", moex_ticker, exc)
        return None

    if hist is None or hist.empty:
        logger.warning("MOEX ISS: no data for %s", moex_ticker)
        return None

    company_name = hist.attrs.get("company_name", moex_ticker)
    return _build_market_data(ticker, company_name, "RUB", hist)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _moex_ticker(ticker: str) -> str | None:
    """Return bare MOEX ticker from *.ME form (e.g. SBER.ME → SBER), else None."""
    if ticker.upper().endswith(".ME"):
        return ticker[:-3].upper()
    return None


def _build_market_data(
    ticker: str,
    company_name: str,
    currency: str,
    hist: pd.DataFrame,
) -> MarketData | None:
    """Compute indicators from an OHLCV DataFrame and return MarketData."""
    close = hist["Close"].dropna()

    if len(close) < 20:
        logger.warning("Too few data points for %s (%d rows)", ticker, len(close))
        return None

    last_price = float(close.iloc[-1])

    def pct_change_n(n: int) -> float:
        if len(close) < n:
            return 0.0
        past = float(close.iloc[-n])
        return (last_price - past) / past * 100 if past else 0.0

    change_7d = pct_change_n(7)
    change_30d = pct_change_n(30)
    change_180d = pct_change_n(180)

    daily_returns = close.pct_change().dropna()
    vol_window = min(30, len(daily_returns))
    volatility = float(daily_returns.tail(vol_window).std() * (252 ** 0.5) * 100)

    sma20 = float(close.rolling(20).mean().iloc[-1])
    sma50 = float(close.rolling(50).mean().iloc[-1])

    rsi = _compute_rsi(close)

    return MarketData(
        ticker=ticker,
        company_name=company_name,
        currency=currency,
        last_price=last_price,
        change_7d=change_7d,
        change_30d=change_30d,
        change_180d=change_180d,
        volatility_30d=volatility,
        sma20=sma20,
        sma50=sma50,
        rsi=rsi,
        history=hist,
    )


def _compute_rsi(close: pd.Series, period: int = 14) -> float | None:
    """Compute RSI using the Wilder smoothing method."""
    try:
        delta = close.diff().dropna()
        gain = delta.clip(lower=0)
        loss = (-delta).clip(lower=0)

        avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()

        rs = avg_gain / avg_loss.replace(0, float("nan"))
        rsi = 100 - (100 / (1 + rs))
        return float(rsi.iloc[-1])
    except Exception:
        return None
