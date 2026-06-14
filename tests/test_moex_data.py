"""Tests for MOEX ISS data fetcher."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from services.moex_data import fetch_moex_history


# ── Helpers ──────────────────────────────────────────────────────────────────

_COLUMNS = [
    "BOARDID", "TRADEDATE", "SHORTNAME", "SECID",
    "OPEN", "HIGH", "LOW", "CLOSE", "VOLUME",
]


def _row(date: str, o: float, h: float, lo: float, c: float, v: int) -> list:
    return ["TQBR", date, "Сбербанк", "SBER", o, h, lo, c, v]


def _mock_response(rows: list[list], start: int = 0, total: int | None = None) -> MagicMock:
    if total is None:
        total = len(rows)
    payload = {
        "history": {"columns": _COLUMNS, "data": rows},
        "history.cursor": {
            "columns": ["INDEX", "TOTAL", "PAGESIZE"],
            "data": [[start, total, 100]],
        },
    }
    resp = MagicMock()
    resp.json.return_value = payload
    resp.raise_for_status.return_value = None
    return resp


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestFetchMoexHistory:
    def test_returns_dataframe_for_valid_data(self):
        rows = [_row("2024-01-10", 300.0, 310.0, 295.0, 305.0, 100_000)]
        with patch("services.moex_data.requests.get", return_value=_mock_response(rows)):
            df = fetch_moex_history("SBER")
        assert df is not None
        assert isinstance(df, pd.DataFrame)

    def test_has_required_ohlcv_columns(self):
        rows = [_row("2024-01-10", 300.0, 310.0, 295.0, 305.0, 100_000)]
        with patch("services.moex_data.requests.get", return_value=_mock_response(rows)):
            df = fetch_moex_history("SBER")
        for col in ("Open", "High", "Low", "Close", "Volume"):
            assert col in df.columns, f"Missing column: {col}"

    def test_index_is_datetimeindex(self):
        rows = [_row("2024-01-10", 300.0, 310.0, 295.0, 305.0, 100_000)]
        with patch("services.moex_data.requests.get", return_value=_mock_response(rows)):
            df = fetch_moex_history("SBER")
        assert pd.api.types.is_datetime64_any_dtype(df.index)

    def test_company_name_stored_in_attrs(self):
        rows = [_row("2024-01-10", 300.0, 310.0, 295.0, 305.0, 100_000)]
        with patch("services.moex_data.requests.get", return_value=_mock_response(rows)):
            df = fetch_moex_history("SBER")
        assert df.attrs.get("company_name") == "Сбербанк"

    def test_returns_none_on_empty_data(self):
        with patch("services.moex_data.requests.get", return_value=_mock_response([])):
            result = fetch_moex_history("UNKNOWN999")
        assert result is None

    def test_returns_none_on_network_error(self):
        with patch("services.moex_data.requests.get", side_effect=ConnectionError("timeout")):
            result = fetch_moex_history("SBER")
        assert result is None

    def test_rows_with_null_close_are_dropped(self):
        rows = [
            _row("2024-01-10", 300.0, 310.0, 295.0, 305.0, 100_000),
            ["TQBR", "2024-01-11", "Сбербанк", "SBER", None, None, None, None, 0],
        ]
        with patch("services.moex_data.requests.get", return_value=_mock_response(rows)):
            df = fetch_moex_history("SBER")
        assert df is not None
        assert len(df) == 1

    def test_rows_are_sorted_by_date_ascending(self):
        rows = [
            _row("2024-01-12", 302.0, 312.0, 297.0, 307.0, 120_000),
            _row("2024-01-10", 300.0, 310.0, 295.0, 305.0, 100_000),
            _row("2024-01-11", 301.0, 311.0, 296.0, 306.0, 110_000),
        ]
        with patch("services.moex_data.requests.get", return_value=_mock_response(rows)):
            df = fetch_moex_history("SBER")
        assert list(df.index) == sorted(df.index)

    def test_close_values_are_numeric(self):
        rows = [_row("2024-01-10", 300.0, 310.0, 295.0, 305.0, 100_000)]
        with patch("services.moex_data.requests.get", return_value=_mock_response(rows)):
            df = fetch_moex_history("SBER")
        assert pd.api.types.is_numeric_dtype(df["Close"])

    def test_multiple_rows_preserved(self):
        rows = [_row(f"2024-01-{10 + i:02d}", 300.0, 310.0, 295.0, 305.0, 100_000) for i in range(5)]
        with patch("services.moex_data.requests.get", return_value=_mock_response(rows)):
            df = fetch_moex_history("SBER")
        assert df is not None
        assert len(df) == 5

    def test_http_error_returns_none(self):
        resp = MagicMock()
        resp.raise_for_status.side_effect = Exception("HTTP 404")
        with patch("services.moex_data.requests.get", return_value=resp):
            result = fetch_moex_history("INVALID")
        assert result is None
