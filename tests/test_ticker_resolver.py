"""
Tests for ticker_resolver module.
"""

import pytest
from services.ticker_resolver import resolve_ticker


class TestRussianCompanies:
    def test_sberbank_russian(self):
        result = resolve_ticker("сбербанк")
        assert result.ticker == "SBER.ME"
        assert result.is_private is False

    def test_sber_short(self):
        result = resolve_ticker("сбер")
        assert result.ticker == "SBER.ME"

    def test_gazprom_russian(self):
        result = resolve_ticker("газпром")
        assert result.ticker == "GAZP.ME"

    def test_lukoil_russian(self):
        result = resolve_ticker("лукойл")
        assert result.ticker == "LKOH.ME"

    def test_yandex_russian(self):
        result = resolve_ticker("яндекс")
        assert result.ticker == "YDEX.ME"

    def test_sberbank_direct_ticker(self):
        result = resolve_ticker("SBER.ME")
        # Direct ticker passes through as-is
        assert result.ticker == "SBER.ME"

    # Short MOEX tickers without .ME suffix
    def test_sber_moex_short(self):
        result = resolve_ticker("SBER")
        assert result.ticker == "SBER.ME"

    def test_gazp_moex_short(self):
        result = resolve_ticker("GAZP")
        assert result.ticker == "GAZP.ME"

    def test_lkoh_moex_short(self):
        result = resolve_ticker("LKOH")
        assert result.ticker == "LKOH.ME"

    def test_ydex_moex_short(self):
        result = resolve_ticker("YDEX")
        assert result.ticker == "YDEX.ME"

    def test_rosn_moex_short(self):
        result = resolve_ticker("ROSN")
        assert result.ticker == "ROSN.ME"

    def test_vtbr_moex_short(self):
        result = resolve_ticker("VTBR")
        assert result.ticker == "VTBR.ME"

    def test_gazp_me_direct(self):
        result = resolve_ticker("GAZP.ME")
        assert result.ticker == "GAZP.ME"


class TestUSCompanies:
    def test_apple(self):
        result = resolve_ticker("apple")
        assert result.ticker == "AAPL"
        assert result.is_private is False

    def test_tesla(self):
        result = resolve_ticker("tesla")
        assert result.ticker == "TSLA"

    def test_nvidia(self):
        result = resolve_ticker("nvidia")
        assert result.ticker == "NVDA"

    def test_microsoft(self):
        result = resolve_ticker("microsoft")
        assert result.ticker == "MSFT"

    def test_google(self):
        result = resolve_ticker("google")
        assert result.ticker == "GOOGL"

    def test_amazon(self):
        result = resolve_ticker("amazon")
        assert result.ticker == "AMZN"

    def test_direct_ticker_uppercase(self):
        result = resolve_ticker("AAPL")
        assert result.ticker == "AAPL"

    def test_direct_ticker_lowercase(self):
        result = resolve_ticker("tsla")
        assert result.ticker == "TSLA"


class TestPrivateCompanies:
    def test_spacex_is_private(self):
        result = resolve_ticker("spacex")
        assert result.is_private is True
        assert result.ticker is None
        assert result.found is True

    def test_openai_is_private(self):
        result = resolve_ticker("openai")
        assert result.is_private is True

    def test_anthropic_is_private(self):
        result = resolve_ticker("anthropic")
        assert result.is_private is True

    def test_private_message_not_empty(self):
        result = resolve_ticker("spacex")
        assert len(result.private_message) > 0

    def test_spacex_message_mentions_alternatives(self):
        result = resolve_ticker("spacex")
        # Message should suggest alternatives
        assert "TSLA" in result.private_message or "Boeing" in result.private_message or "LMT" in result.private_message


class TestCaseSensitivity:
    def test_mixed_case_apple(self):
        result = resolve_ticker("Apple")
        assert result.ticker == "AAPL"

    def test_uppercase_tesla(self):
        result = resolve_ticker("TESLA")
        # "TESLA" is not in the map as-is, but "tesla" is — after normalizing
        assert result.ticker == "TSLA"

    # Free-text input as users would type it (capital first letter)
    def test_capitalised_sberbank(self):
        result = resolve_ticker("Сбербанк")
        assert result.ticker == "SBER.ME"

    def test_capitalised_sber(self):
        result = resolve_ticker("Сбер")
        assert result.ticker == "SBER.ME"

    def test_capitalised_apple(self):
        result = resolve_ticker("Apple")
        assert result.ticker == "AAPL"

    def test_capitalised_tesla(self):
        result = resolve_ticker("Tesla")
        assert result.ticker == "TSLA"

    def test_direct_aapl(self):
        result = resolve_ticker("AAPL")
        assert result.ticker == "AAPL"


class TestUnknownTicker:
    def test_unknown_returns_as_ticker(self):
        result = resolve_ticker("XYZUNKNOWN123")
        assert result.ticker == "XYZUNKNOWN123"
        assert result.is_private is False


class TestIsKnownFlag:
    """is_known=True for map hits; False for raw passthrough."""

    def test_known_company_is_marked_known(self):
        assert resolve_ticker("сбербанк").is_known is True

    def test_short_russian_ticker_is_marked_known(self):
        assert resolve_ticker("SBER").is_known is True

    def test_english_name_is_marked_known(self):
        assert resolve_ticker("apple").is_known is True

    def test_index_is_marked_known(self):
        assert resolve_ticker("nasdaq").is_known is True

    def test_raw_passthrough_is_not_known(self):
        # AAPL is not in COMPANY_MAP by exact key; passes through as-is
        result = resolve_ticker("AAPL")
        assert result.is_known is False

    def test_completely_unknown_string_is_not_known(self):
        result = resolve_ticker("XYZGARBAGE999")
        assert result.is_known is False

    def test_private_company_has_no_is_known_requirement(self):
        # Private companies are recognised (is_private=True), is_known defaults to True
        result = resolve_ticker("spacex")
        assert result.is_private is True
