"""Tests for scripts/regime.py — rule-based market + sector classifier.

Pure math, no network. Live smoke tests are marked `smoke`.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import regime as rg  # noqa: E402


# ---------------- classify_market truth table ----------------

def test_market_defensive_when_vix_above_30():
    # Defensive should override every other signal.
    assert rg.classify_market(vix=35, spy=500, spy_200sma=450, spy_20d_return_pct=5) == "Defensive"


def test_market_caution_when_vix_in_22_to_30_range():
    assert rg.classify_market(vix=25, spy=500, spy_200sma=450, spy_20d_return_pct=2) == "Caution"


def test_market_caution_when_spy_under_200sma_even_with_calm_vix():
    assert rg.classify_market(vix=12, spy=400, spy_200sma=450, spy_20d_return_pct=-1) == "Caution"


def test_market_bull_when_all_three_conditions_align():
    assert rg.classify_market(vix=13, spy=500, spy_200sma=450, spy_20d_return_pct=2) == "Bull"


def test_market_neutral_when_vix_in_15_to_22_and_spy_above_200sma():
    assert rg.classify_market(vix=18, spy=500, spy_200sma=450, spy_20d_return_pct=1) == "Neutral"


def test_market_neutral_when_bull_conditions_almost_met_but_vix_too_high():
    # VIX = 15 exactly is NOT < 15, so not Bull. Falls through to Neutral.
    assert rg.classify_market(vix=15, spy=500, spy_200sma=450, spy_20d_return_pct=2) == "Neutral"


def test_market_neutral_when_bull_conditions_almost_met_but_20d_flat():
    # 20d return = 0 is NOT > 0, so not Bull. Falls through to Neutral.
    assert rg.classify_market(vix=12, spy=500, spy_200sma=450, spy_20d_return_pct=0) == "Neutral"


def test_market_defensive_takes_precedence_over_caution_signals():
    assert rg.classify_market(vix=40, spy=400, spy_200sma=450, spy_20d_return_pct=-5) == "Defensive"


def test_market_vix_22_exact_is_caution():
    # Boundary: VIX >= 22 → Caution
    assert rg.classify_market(vix=22, spy=500, spy_200sma=450, spy_20d_return_pct=1) == "Caution"


def test_market_vix_30_exact_is_still_caution_not_defensive():
    # Defensive is strict: VIX > 30
    assert rg.classify_market(vix=30, spy=500, spy_200sma=450, spy_20d_return_pct=1) == "Caution"


# ---------------- classify_sector truth table ----------------

def test_sector_bear_when_price_below_50sma():
    assert rg.classify_sector(price=95, sma_50=100, return_10d_pct=1) == "Bear"


def test_sector_bear_when_10d_below_minus_4():
    assert rg.classify_sector(price=105, sma_50=100, return_10d_pct=-5) == "Bear"


def test_sector_trend_when_above_sma_and_strong_momentum():
    assert rg.classify_sector(price=105, sma_50=100, return_10d_pct=3) == "Trend"


def test_sector_choppy_when_above_sma_but_weak_momentum():
    assert rg.classify_sector(price=101, sma_50=100, return_10d_pct=1) == "Choppy"


def test_sector_choppy_when_above_sma_and_mild_negative_momentum():
    assert rg.classify_sector(price=101, sma_50=100, return_10d_pct=-3) == "Choppy"


def test_sector_choppy_at_2_pct_boundary():
    # 10d = 2.0 is NOT > 2.0, so Choppy not Trend
    assert rg.classify_sector(price=105, sma_50=100, return_10d_pct=2) == "Choppy"


def test_sector_bear_overrides_trend_when_below_sma_with_high_momentum():
    # price < 50SMA wins, even with positive 10d.
    assert rg.classify_sector(price=95, sma_50=100, return_10d_pct=5) == "Bear"


# ---------------- compute_persistence ----------------

def test_persistence_counts_only_trailing_matches():
    assert rg.compute_persistence(["A", "A", "B", "B", "B"]) == 3


def test_persistence_returns_full_length_when_all_match():
    assert rg.compute_persistence(["Bull", "Bull", "Bull"]) == 3


def test_persistence_returns_one_when_last_differs_from_prev():
    assert rg.compute_persistence(["A", "A", "A", "B"]) == 1


def test_persistence_empty_list_returns_zero():
    assert rg.compute_persistence([]) == 0


def test_persistence_single_element():
    assert rg.compute_persistence(["Bull"]) == 1


# ---------------- market_regime_from_history (synthetic data) ----------------

def _synthetic_spy(close_today: float, sma_value: float, change_20d_pct: float,
                  n_days: int = 260) -> pd.DataFrame:
    """Construct an SPY history that yields a known 200-SMA and 20d return.

    Strategy: hold price flat at sma_value for the first n-21 bars (so 200-SMA
    converges to sma_value), then ramp linearly to close_today over the final
    20 bars. Adjust the 20-day-ago price so that today/then - 1 == change.
    """
    idx = pd.date_range("2025-01-01", periods=n_days, freq="B")
    closes = np.full(n_days, sma_value, dtype=float)
    # Compute the price 20 days ago that gives the desired 20d return.
    price_20d_ago = close_today / (1 + change_20d_pct / 100)
    # Linear ramp from sma_value -> price_20d_ago over (n-21..n-21) — keep it simple:
    # last 20 closes interpolate price_20d_ago -> close_today.
    ramp = np.linspace(price_20d_ago, close_today, 21)
    closes[-21:] = ramp
    return pd.DataFrame(
        {"Close": closes, "High": closes, "Low": closes},
        index=idx,
    )


def _synthetic_vix(level: float, n_days: int = 10) -> pd.DataFrame:
    idx = pd.date_range("2025-12-01", periods=n_days, freq="B")
    closes = np.full(n_days, float(level))
    return pd.DataFrame({"Close": closes, "High": closes, "Low": closes}, index=idx)


def test_market_regime_from_history_bull_case():
    spy = _synthetic_spy(close_today=500, sma_value=450, change_20d_pct=2.0)
    vix = _synthetic_vix(level=13)
    r = rg.market_regime_from_history(spy, vix)
    assert r["regime"] == "Bull"
    assert r["deployment_target"] == 0.85
    assert r["trade_slots"] == 3
    assert r["stable"] is True
    assert r["persistence_bars"] == 3


def test_market_regime_from_history_defensive_case():
    spy = _synthetic_spy(close_today=500, sma_value=450, change_20d_pct=1.0)
    vix = _synthetic_vix(level=35)
    r = rg.market_regime_from_history(spy, vix)
    assert r["regime"] == "Defensive"
    assert r["deployment_target"] == 0.0
    assert r["trade_slots"] == 0


def test_market_regime_from_history_caution_below_200sma():
    spy = _synthetic_spy(close_today=400, sma_value=450, change_20d_pct=-1.0)
    vix = _synthetic_vix(level=18)
    r = rg.market_regime_from_history(spy, vix)
    assert r["regime"] == "Caution"
    assert r["deployment_target"] == 0.5


def test_market_regime_unstable_when_vix_flips_in_window():
    # Construct SPY with a flat 20d return so all 3 trailing bars classify on VIX alone:
    #   Day -2: VIX = 13 -> Bull (vix<15, spy>sma, 20d>0)
    #   Day -1: VIX = 13 -> Bull
    #   Day  0: VIX = 25 -> Caution
    # Expected: regime = Caution, persistence_bars = 1.
    n = 260
    spy_idx = pd.date_range("2025-01-01", periods=n, freq="B")
    # First (n - 21) bars flat at 450; last 21 bars also flat at 500.
    # The 20d return at every bar in the last 20 is fixed: 500/500 - 1 = 0 (>0? no)
    # We need 20d > 0 for Bull, so make the prior period 495 and the recent 500.
    closes = np.full(n, 495.0)
    closes[-21:] = 500.0  # so close_today=500, close_20d_ago=500 — 20d=0%. We want >0.
    # Adjust: closes[-21] (= 20 days before today) = 495, then closes[-20:] = 500.
    closes[-21] = 495.0
    closes[-20:] = 500.0
    # Now 20d return for the last bar = 500/495 - 1 ≈ 1.01% > 0  ✓
    # For day -1 (i = n-2), the 20-days-ago index is n-22 → close = 495.
    # Recent close on day -1 = 500. Return ≈ 1.01% > 0  ✓
    # For day -2 (i = n-3), 20-days-ago is n-23 → 495; today close 500. Same. ✓
    spy = pd.DataFrame({"Close": closes, "High": closes, "Low": closes}, index=spy_idx)

    # VIX aligned to SPY's last 3 dates.
    vix_idx = spy_idx[-3:]
    vix_closes = np.array([13.0, 13.0, 25.0])
    vix = pd.DataFrame({"Close": vix_closes, "High": vix_closes, "Low": vix_closes}, index=vix_idx)

    r = rg.market_regime_from_history(spy, vix, persistence_window=3)
    assert r["regime"] == "Caution"
    assert r["classifications_trailing"] == ["Bull", "Bull", "Caution"]
    assert r["persistence_bars"] == 1
    assert r["stable"] is False


def test_market_regime_rejects_short_history():
    spy = _synthetic_spy(close_today=500, sma_value=450, change_20d_pct=1.0, n_days=100)
    vix = _synthetic_vix(level=13)
    with pytest.raises(ValueError, match="too short"):
        rg.market_regime_from_history(spy, vix)


# ---------------- sector_regime_from_history (synthetic data) ----------------

def _synthetic_sector(close_today: float, sma_value: float, return_10d_pct: float,
                      n: int = 80) -> pd.DataFrame:
    idx = pd.date_range("2025-01-01", periods=n, freq="B")
    closes = np.full(n, sma_value, dtype=float)
    closes[-11] = close_today / (1 + return_10d_pct / 100)
    # Ramp the last 10 bars so SMA-50 stays at sma_value (50-day window includes the flat region).
    closes[-10:] = np.linspace(closes[-11], close_today, 11)[1:]
    return pd.DataFrame({"Close": closes, "High": closes, "Low": closes}, index=idx)


def test_sector_trend_classification():
    df = _synthetic_sector(close_today=110, sma_value=100, return_10d_pct=5)
    r = rg.sector_regime_from_history("XLK", df)
    assert r["regime"] == "Trend"
    assert r["score"] > 0


def test_sector_bear_classification():
    df = _synthetic_sector(close_today=85, sma_value=100, return_10d_pct=-6)
    r = rg.sector_regime_from_history("XLE", df)
    assert r["regime"] == "Bear"
    assert r["score"] < 0


def test_sector_choppy_classification():
    df = _synthetic_sector(close_today=101, sma_value=100, return_10d_pct=1)
    r = rg.sector_regime_from_history("XLP", df)
    assert r["regime"] == "Choppy"


def test_sector_rejects_short_history():
    df = _synthetic_sector(close_today=110, sma_value=100, return_10d_pct=5, n=30)
    with pytest.raises(ValueError, match="too short"):
        rg.sector_regime_from_history("XLK", df)


# ---------------- live smoke ----------------

@pytest.mark.smoke
def test_live_market_regime_returns_valid_enum():
    result = rg.market_regime()
    assert result["regime"] in rg.MARKET_REGIMES
    assert 0.0 <= result["deployment_target"] <= 1.0
    assert 0 <= result["trade_slots"] <= 3


@pytest.mark.smoke
def test_live_sector_regimes_covers_all_eleven():
    result = rg.sector_regimes()
    assert set(result["sectors"].keys()) == set(rg.SECTOR_ETFS)
