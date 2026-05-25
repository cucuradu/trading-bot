"""Tests for scripts/market_data.py extensions: ATR, correlation, earnings parsing.

All math is exercised against synthetic DataFrames (no network). A single live
smoke test against AAPL is included at the bottom and can be skipped with -m.
"""
from __future__ import annotations

import sys
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import market_data as md  # noqa: E402


# ---------------- ATR math ----------------

def _make_ohlc(n: int, start: float = 100.0, daily_range: float = 2.0,
               drift: float = 0.0) -> pd.DataFrame:
    """Deterministic OHLC fixture: each bar has range=daily_range around a drifting close."""
    idx = pd.date_range("2026-01-01", periods=n, freq="B")
    closes = np.array([start + drift * i for i in range(n)], dtype=float)
    rows = []
    for i, c in enumerate(closes):
        prev = closes[i - 1] if i > 0 else c
        # Construct so that True Range == daily_range exactly:
        # high = max(close, prev) + daily_range/2
        # low  = min(close, prev) - daily_range/2
        high = max(c, prev) + daily_range / 2
        low = min(c, prev) - daily_range / 2
        rows.append((c, high, low))
    return pd.DataFrame(rows, index=idx, columns=["Close", "High", "Low"])


def test_atr_on_constant_range_equals_range():
    # A flat market where every bar has the same True Range = 2.0 should
    # converge to ATR == 2.0 after `period` bars of Wilder smoothing.
    df = _make_ohlc(n=40, start=100.0, daily_range=2.0, drift=0.0)
    result = md.compute_atr(df, period=14)
    assert result["atr"] == pytest.approx(2.0, abs=0.01)


def test_atr_pct_of_price_is_consistent():
    df = _make_ohlc(n=40, start=100.0, daily_range=2.0, drift=0.0)
    result = md.compute_atr(df, period=14)
    assert result["last_close"] == 100.0
    assert result["atr_pct_of_price"] == pytest.approx(2.0, abs=0.01)


def test_atr_multipliers_chain():
    df = _make_ohlc(n=40, start=100.0, daily_range=2.0, drift=0.0)
    result = md.compute_atr(df, period=14)
    assert result["stop_pct_2_5x"] == pytest.approx(result["atr_pct_of_price"] * 2.5, abs=0.01)
    assert result["stop_pct_1_75x"] == pytest.approx(result["atr_pct_of_price"] * 1.75, abs=0.01)
    assert result["stop_pct_1_25x"] == pytest.approx(result["atr_pct_of_price"] * 1.25, abs=0.01)


def test_atr_rejects_insufficient_history():
    df = _make_ohlc(n=5, start=100.0, daily_range=2.0)
    with pytest.raises(ValueError, match="insufficient history"):
        md.compute_atr(df, period=14)


def test_atr_period_7_is_more_reactive_than_14():
    # Higher-volatility regime in the tail should be picked up faster by ATR(7) than ATR(14).
    quiet = _make_ohlc(n=20, start=100.0, daily_range=1.0)
    loud = _make_ohlc(n=20, start=100.0, daily_range=4.0)
    loud.index = pd.date_range("2026-02-01", periods=20, freq="B")
    df = pd.concat([quiet, loud])
    atr_7 = md.compute_atr(df, period=7)["atr"]
    atr_14 = md.compute_atr(df, period=14)["atr"]
    assert atr_7 > atr_14  # ATR(7) reacts to the high-vol tail faster


# ---------------- stop_pct_for_entry clamping ----------------

def test_stop_clamps_to_floor_when_atr_is_low(monkeypatch):
    monkeypatch.setattr(md, "atr", lambda sym, p=14: {
        "symbol": sym.upper(),
        "atr": 0.5,
        "last_close": 100.0,
        "atr_pct_of_price": 0.5,
        "stop_pct_2_5x": 1.25,  # well below 7% floor
        "as_of": "2026-05-22",
    })
    r = md.stop_pct_for_entry("XLU")
    assert r["stop_pct"] == 7.0
    assert r["clamped"] is True
    assert r["stop_price"] == round(100.0 * 0.93, 2)


def test_stop_clamps_to_cap_when_atr_is_huge(monkeypatch):
    monkeypatch.setattr(md, "atr", lambda sym, p=14: {
        "symbol": sym.upper(),
        "atr": 12.0,
        "last_close": 100.0,
        "atr_pct_of_price": 12.0,
        "stop_pct_2_5x": 30.0,  # blows past 15% cap
        "as_of": "2026-05-22",
    })
    r = md.stop_pct_for_entry("TSLA")
    assert r["stop_pct"] == 15.0
    assert r["clamped"] is True
    assert r["stop_price"] == round(100.0 * 0.85, 2)


def test_stop_passes_through_when_in_band(monkeypatch):
    monkeypatch.setattr(md, "atr", lambda sym, p=14: {
        "symbol": sym.upper(),
        "atr": 3.5,
        "last_close": 100.0,
        "atr_pct_of_price": 3.5,
        "stop_pct_2_5x": 8.75,
        "as_of": "2026-05-22",
    })
    r = md.stop_pct_for_entry("NVDA")
    assert r["stop_pct"] == pytest.approx(8.75, abs=0.01)
    assert r["clamped"] is False


# ---------------- correlation math ----------------

def _make_returns(seed: int, n: int = 60) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return rng.normal(loc=0.0, scale=0.01, size=n)


def _series_from_returns(rets: np.ndarray, start: float = 100.0) -> pd.Series:
    return pd.Series((1 + rets).cumprod() * start)


def test_correlation_identical_streams_are_one():
    a = _series_from_returns(_make_returns(seed=1))
    df = pd.DataFrame({"A": a, "B": a.copy()})
    df.index = pd.date_range("2026-01-01", periods=len(a), freq="B")
    r = md.compute_correlation(df, lookback_days=30)
    assert r["matrix"]["A"]["B"] == pytest.approx(1.0, abs=0.0001)
    assert r["max_off_diagonal"] == pytest.approx(1.0, abs=0.0001)


def test_correlation_independent_streams_are_low():
    a = _series_from_returns(_make_returns(seed=1))
    b = _series_from_returns(_make_returns(seed=99))
    df = pd.DataFrame({"A": a, "B": b})
    df.index = pd.date_range("2026-01-01", periods=len(a), freq="B")
    r = md.compute_correlation(df, lookback_days=30)
    assert abs(r["matrix"]["A"]["B"]) < 0.4  # essentially uncorrelated


def test_correlation_finds_max_off_diagonal_pair():
    base = _make_returns(seed=1)
    df = pd.DataFrame({
        "A": _series_from_returns(base),
        "B": _series_from_returns(base + 0.0001),         # very close to A
        "C": _series_from_returns(_make_returns(seed=99)), # uncorrelated
    })
    df.index = pd.date_range("2026-01-01", periods=len(base), freq="B")
    r = md.compute_correlation(df, lookback_days=30)
    assert set(r["max_pair"]) == {"A", "B"}


def test_correlation_rejects_insufficient_history():
    df = pd.DataFrame({
        "A": [100.0, 101.0, 102.0],
        "B": [200.0, 201.0, 202.0],
    })
    df.index = pd.date_range("2026-01-01", periods=3, freq="B")
    with pytest.raises(ValueError, match="insufficient overlapping history"):
        md.compute_correlation(df, lookback_days=30)


# ---------------- earnings date coercion ----------------

def test_coerce_date_handles_datetime():
    assert md._coerce_date(datetime(2026, 7, 30, 12, 0)) == date(2026, 7, 30)


def test_coerce_date_handles_date():
    assert md._coerce_date(date(2026, 7, 30)) == date(2026, 7, 30)


def test_coerce_date_handles_iso_string():
    assert md._coerce_date("2026-07-30") == date(2026, 7, 30)


def test_coerce_date_handles_iso_with_time():
    assert md._coerce_date("2026-07-30 13:30:00") == date(2026, 7, 30)


def test_coerce_date_handles_pd_timestamp():
    assert md._coerce_date(pd.Timestamp("2026-07-30")) == date(2026, 7, 30)


def test_coerce_date_returns_none_for_unknown():
    assert md._coerce_date("not a date") is None
    assert md._coerce_date(None) is None
    assert md._coerce_date(12345) is None


# ---------------- live smoke (skipped by default; run with -m smoke) ----------------

@pytest.mark.smoke
def test_live_atr_returns_sensible_spy():
    result = md.atr("SPY")
    assert result["atr"] > 0
    assert 0 < result["atr_pct_of_price"] < 5  # SPY's ATR is typically well under 5%


@pytest.mark.smoke
def test_live_earnings_returns_future_date_for_aapl():
    result = md.earnings("AAPL")
    if result["next_earnings_date"]:
        assert result["days_until"] is not None
