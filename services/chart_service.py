"""
Generates price chart with SMA overlays using matplotlib.
"""

from __future__ import annotations

import io
import logging

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd

logger = logging.getLogger(__name__)


def generate_chart(ticker: str, company_name: str, history: pd.DataFrame) -> bytes | None:
    """
    Generate a PNG chart with close price, SMA20, SMA50.
    Returns bytes of the PNG image, or None on failure.
    """
    try:
        close = history["Close"].dropna()
        sma20 = close.rolling(20).mean()
        sma50 = close.rolling(50).mean()

        fig, ax = plt.subplots(figsize=(10, 5))
        fig.patch.set_facecolor("#0d1117")
        ax.set_facecolor("#161b22")

        ax.plot(close.index, close.values, color="#58a6ff", linewidth=1.5,
                label="Цена закрытия", zorder=3)
        ax.plot(sma20.index, sma20.values, color="#f0c419", linewidth=1.2,
                linestyle="--", label="SMA20", alpha=0.85, zorder=2)
        ax.plot(sma50.index, sma50.values, color="#ff6b6b", linewidth=1.2,
                linestyle="--", label="SMA50", alpha=0.85, zorder=2)

        ax.fill_between(close.index, close.values, alpha=0.08, color="#58a6ff")

        ax.set_title(f"{company_name} ({ticker}) — Цена за 1 год",
                     color="white", fontsize=14, pad=12)
        ax.set_xlabel("Дата", color="#8b949e", fontsize=10)
        ax.set_ylabel("Цена", color="#8b949e", fontsize=10)

        ax.tick_params(colors="#8b949e", labelsize=9)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        fig.autofmt_xdate(rotation=30)

        for spine in ax.spines.values():
            spine.set_edgecolor("#30363d")

        ax.grid(True, color="#21262d", linewidth=0.7, linestyle="-", alpha=0.7)
        ax.legend(facecolor="#161b22", edgecolor="#30363d", labelcolor="white", fontsize=9)

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=130, facecolor=fig.get_facecolor())
        buf.seek(0)
        image_bytes = buf.read()
        plt.close(fig)

        return image_bytes

    except Exception as exc:
        logger.error("Chart generation failed for %s: %s", ticker, exc)
        return None
