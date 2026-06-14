"""
Tests for rule-based analysis logic.
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock

from services.market_data import MarketData
from services.analysis_service import rule_based_analysis


def make_market_data(**kwargs) -> MarketData:
    """Helper to create a MarketData with sensible defaults."""
    defaults = dict(
        ticker="TEST",
        company_name="Test Company",
        currency="USD",
        last_price=100.0,
        change_7d=1.0,
        change_30d=3.0,
        change_180d=10.0,
        volatility_30d=25.0,
        sma20=102.0,
        sma50=98.0,
        rsi=55.0,
        history=pd.DataFrame(),
    )
    defaults.update(kwargs)
    return MarketData(**defaults)


class TestRuleBasedAnalysis:
    def test_positive_scenario_sma20_above_sma50(self):
        data = make_market_data(sma20=110.0, sma50=100.0, change_30d=5.0, volatility_30d=20.0, rsi=55.0)
        tech, conclusion = rule_based_analysis(data)
        assert "позитив" in conclusion.lower() or "нейтральн" in conclusion.lower()
        assert "SMA20 выше SMA50" in tech

    def test_negative_scenario_sma20_below_sma50(self):
        data = make_market_data(sma20=90.0, sma50=100.0, change_30d=-10.0, volatility_30d=55.0, rsi=65.0)
        tech, conclusion = rule_based_analysis(data)
        assert "SMA20 ниже SMA50" in tech

    def test_high_volatility_warning(self):
        data = make_market_data(volatility_30d=65.0)
        tech, _ = rule_based_analysis(data)
        assert "высокая" in tech.lower() or "высокий риск" in tech.lower()

    def test_overbought_rsi(self):
        data = make_market_data(rsi=75.0)
        tech, _ = rule_based_analysis(data)
        assert "перекупленност" in tech.lower()

    def test_oversold_rsi(self):
        data = make_market_data(rsi=25.0)
        tech, _ = rule_based_analysis(data)
        assert "перепроданност" in tech.lower()

    def test_strong_growth_correction_risk(self):
        data = make_market_data(change_30d=25.0)
        tech, _ = rule_based_analysis(data)
        assert "коррекц" in tech.lower()

    def test_strong_decline_oversold_mention(self):
        data = make_market_data(change_30d=-20.0)
        tech, _ = rule_based_analysis(data)
        assert "перепроданност" in tech.lower()

    def test_no_rsi_still_works(self):
        data = make_market_data(rsi=None)
        tech, conclusion = rule_based_analysis(data)
        assert isinstance(tech, str)
        assert isinstance(conclusion, str)
        assert len(tech) > 0

    def test_conclusion_is_one_of_three_types(self):
        data = make_market_data()
        _, conclusion = rule_based_analysis(data)
        assert any(
            phrase in conclusion
            for phrase in ["позитивный", "нейтральный", "негативный", "осторожный"]
        )

    def test_returns_tuple_of_two_strings(self):
        data = make_market_data()
        result = rule_based_analysis(data)
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert all(isinstance(s, str) for s in result)
