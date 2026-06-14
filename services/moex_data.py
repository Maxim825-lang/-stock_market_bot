"""
Fetches OHLCV history for Moscow Exchange (MOEX) securities via the ISS REST API.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta

import pandas as pd
import requests

logger = logging.getLogger(__name__)

_ISS_HISTORY_URL = (
    "https://iss.moex.com/iss/history/engines/stock/markets/shares/"
    "boards/TQBR/securities/{ticker}.json"
)


def fetch_moex_history(ticker: str) -> pd.DataFrame | None:
    """
    Download 1-year daily OHLCV data from MOEX ISS API.

    Returns a DataFrame indexed by Date with columns Open, High, Low, Close, Volume,
    or None on failure / no data.  Company name (if available) is stored in df.attrs["company_name"].
    """
    till = datetime.now().date()
    from_date = till - timedelta(days=365)

    url = _ISS_HISTORY_URL.format(ticker=ticker)
    all_rows: list[list] = []
    columns: list[str] = []
    start = 0

    while True:
        params = {
            "from": from_date.isoformat(),
            "till": till.isoformat(),
            "start": start,
            "limit": 100,
        }
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            payload = resp.json()
        except Exception as exc:
            logger.error("MOEX ISS request failed for %s: %s", ticker, exc)
            return None

        history_block = payload.get("history", {})
        if not columns:
            columns = history_block.get("columns", [])
        rows = history_block.get("data", [])

        if not rows:
            break

        all_rows.extend(rows)

        # Use history.cursor to decide whether to paginate
        cursor_data = payload.get("history.cursor", {}).get("data", [])
        if cursor_data:
            idx, total, page_size = cursor_data[0][0], cursor_data[0][1], cursor_data[0][2]
            if idx + page_size >= total:
                break
            start = idx + page_size
        else:
            if len(rows) < 100:
                break
            start += 100

    if not all_rows or not columns:
        logger.warning("MOEX ISS returned no data for %s", ticker)
        return None

    raw_df = pd.DataFrame(all_rows, columns=columns)

    # Extract human-readable company name while we still have all columns
    company_name: str | None = None
    if "SHORTNAME" in raw_df.columns:
        valid = raw_df["SHORTNAME"].dropna()
        if not valid.empty:
            company_name = str(valid.iloc[0])

    # Prefer CLOSE; fall back to LEGALCLOSEPRICE if CLOSE is absent
    close_col = "CLOSE" if "CLOSE" in raw_df.columns else "LEGALCLOSEPRICE"

    col_map = {
        "TRADEDATE": "Date",
        "OPEN": "Open",
        "HIGH": "High",
        "LOW": "Low",
        close_col: "Close",
        "VOLUME": "Volume",
    }
    rename = {k: v for k, v in col_map.items() if k in raw_df.columns}
    df = raw_df.rename(columns=rename)

    needed = [c for c in ["Date", "Open", "High", "Low", "Close", "Volume"] if c in df.columns]
    if "Date" not in needed or "Close" not in needed:
        logger.error("MOEX response missing required columns for %s (got: %s)", ticker, list(raw_df.columns))
        return None

    df = df[needed].copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date").sort_index()

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.dropna(subset=["Close"])

    if df.empty:
        logger.warning("MOEX ISS: no valid OHLCV rows for %s after cleanup", ticker)
        return None

    if company_name:
        df.attrs["company_name"] = company_name

    return df
