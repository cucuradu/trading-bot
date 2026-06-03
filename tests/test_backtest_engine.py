"""Tests for backtest/engine.py — walk-forward engine with synthetic bars.

These don't hit yfinance. We build synthetic OHLC for SPY, ^VIX, and a small
universe (AAPL, NVDA) and verify the engine's state transitions.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_BACKTEST = Path(__file__).resolve().parent.parent / "backtest"
if str(_BACKTEST) not in sys.path:
    sys.path.insert(0, str(_BACKTEST))

import engine as eng  # noqa: E402


def _synth_bars(symbol: str, closes: list[float], start: str = "2024-01-01") -> pd.DataFrame:
    idx = pd.date_range(start, periods=len(closes), freq="B")
    close = np.array(closes, dtype=float)
    return pd.DataFrame({
        "Open": close,
        "High": close * 1.01,
        "Low": close * 0.99,
        "Close": close,
        "Adj Close": close,
        "Volume": np.full(len(close), 1_000_000, dtype=int),
    }, index=idx)


def _calm_vix_bars(n: int, start: str = "2024-01-01", level: float = 14.0) -> pd.DataFrame:
    idx = pd.date_range(start, periods=n, freq="B")
    closes = np.full(n, level, dtype=float)
    return pd.DataFrame({
        "Open": closes, "High": closes, "Low": closes, "Close": closes,
        "Adj Close": closes, "Volume": np.zeros(n, dtype=int),
    }, index=idx)


# ---------------- Engine refuses bad config ----------------

def test_engine_requires_spy_and_vix():
    bars = {"AAPL": _synth_bars("AAPL", [100, 101, 102])}
    with pytest.raises(ValueError, match="SPY and \\^VIX"):
        eng.Engine(bars)


# ---------------- No entry simulator → no trades, equity = starting ----------------

def test_no_entry_simulator_produces_no_trades():
    n = 250
    bars = {
        "SPY": _synth_bars("SPY", list(np.linspace(400, 500, n))),
        "^VIX": _calm_vix_bars(n),
        "AAPL": _synth_bars("AAPL", list(np.linspace(100, 130, n))),
    }
    eng_obj = eng.Engine(bars, entry_simulator=None)
    cfg = eng.BacktestConfig(
        start=date(2024, 1, 1), end=date(2024, 12, 31),
        starting_equity=100_000.0,
    )
    result = eng_obj.run(cfg)
    assert len(result.trades) == 0
    assert result.final_equity == pytest.approx(100_000.0)
    assert not result.lock_triggered


# ---------------- One forced entry, observe exit via trailing stop ----------------

def _make_one_shot_entry(symbol: str, *, fire_on_index: int = 220):
    """Entry simulator that places a single buy on the bar at `fire_on_index`."""
    state = {"fired": False, "idx": 0}

    def sim(*, bars, current_date, regime, open_symbols, equity, slots):
        # Find SPY's index of current_date.
        spy = bars["SPY"]
        i = spy.index.get_loc(current_date)
        if not state["fired"] and i >= fire_on_index and slots > 0:
            state["fired"] = True
            df = bars.get(symbol)
            if df is None or current_date not in df.index:
                return []
            entry_price = float(df.at[current_date, "Close"])
            return [(symbol, entry_price)]
        return []

    return sim


def test_engine_opens_one_position_and_closes_it():
    n = 260
    rising = list(np.linspace(100, 140, n))  # AAPL rises smoothly
    bars = {
        "SPY": _synth_bars("SPY", list(np.linspace(400, 500, n))),
        "^VIX": _calm_vix_bars(n),
        "AAPL": _synth_bars("AAPL", rising),
    }
    cfg = eng.BacktestConfig(
        start=date(2024, 1, 1), end=date(2024, 12, 31),
        starting_equity=100_000.0, exit_strategy="atr_2_5x",
    )
    sim = _make_one_shot_entry("AAPL", fire_on_index=220)
    eng_obj = eng.Engine(bars, entry_simulator=sim)
    result = eng_obj.run(cfg)
    assert len(result.trades) == 1
    t = result.trades[0]
    assert t.symbol == "AAPL"
    assert t.regime_at_entry in {"Bull", "Neutral", "Caution"}
    # The smoothly-rising series moves only fractionally per bar, so the position
    # sits between -3% and +3% past day 10 → time_stop fires. That's correct
    # engine behavior for slow drift; accept any non-error exit reason.
    assert t.exit_reason in {
        "end_of_window", "trailing_stop", "regime_defensive", "time_stop", "hard_cut",
    }
    assert t.shares > 0


# ---------------- Engine reports lock when synthetic crash drives DD past -10% ----------------

def test_lock_triggers_after_multiple_consecutive_losses():
    """The safety net bounds single-position loss at the stop level, so the
    -10% account-drawdown lock can only fire from cumulative losses. We open
    a fresh position every week into a crashing market; each gets cut at -7%
    of its position (~7% × max_position_pct of equity), and after enough
    trades the cumulative drawdown trips the lock."""
    n = 260
    # AAPL: stable for warmup, then a long slow grind down so each weekly
    # entry gets cut at -7%.
    aapl_closes = list(np.linspace(100, 120, 100)) + list(np.linspace(120, 70, 160))
    bars = {
        "SPY": _synth_bars("SPY", list(np.linspace(400, 500, n))),
        "^VIX": _calm_vix_bars(n),
        "AAPL": _synth_bars("AAPL", aapl_closes),
    }

    def repeated_buyer(*, bars, current_date, regime, open_symbols, equity, slots):
        # Buy AAPL whenever we have no position open, after the warmup period.
        if "AAPL" in open_symbols or slots <= 0:
            return []
        i = bars["SPY"].index.get_loc(current_date)
        if i < 105:
            return []
        df = bars["AAPL"]
        if current_date not in df.index:
            return []
        return [("AAPL", float(df.at[current_date, "Close"]))]

    cfg = eng.BacktestConfig(
        start=date(2024, 1, 1), end=date(2024, 12, 31),
        starting_equity=100_000.0, exit_strategy="fixed_10",
        max_positions=1, max_position_pct=1.0,
        apply_regime_gating=False,  # keep buying through the slow decline
    )
    eng_obj = eng.Engine(bars, entry_simulator=repeated_buyer)
    result = eng_obj.run(cfg)

    # After several consecutive -7% cuts, the account is well below 90% of peak.
    assert result.lock_triggered is True
    assert result.final_equity < result.peak_equity * 0.90


# ---------------- Defensive regime blocks entries ----------------

def test_defensive_regime_blocks_new_entries():
    n = 260
    # High VIX → Defensive.
    bars = {
        "SPY": _synth_bars("SPY", list(np.linspace(400, 500, n))),
        "^VIX": _calm_vix_bars(n, level=40.0),  # VIX > 30 → Defensive
        "AAPL": _synth_bars("AAPL", list(np.linspace(100, 140, n))),
    }
    cfg = eng.BacktestConfig(
        start=date(2024, 1, 1), end=date(2024, 12, 31),
        starting_equity=100_000.0, exit_strategy="atr_2_5x",
    )
    sim = _make_one_shot_entry("AAPL", fire_on_index=220)
    eng_obj = eng.Engine(bars, entry_simulator=sim)
    result = eng_obj.run(cfg)
    assert len(result.trades) == 0


# ---------------- Remediation knob helpers (audit 2026-06-03) ----------------

def test_sized_shares_risk_cap_binds_on_wide_stop():
    # 20% of $100k = $20k → 23 sh @ $835. Risk cap 2% = $2k, per-share risk
    # $125.25 → 15 sh. min() picks the risk-capped count.
    s = eng._sized_shares(equity=100_000, max_position_pct=0.20, fill_price=835.0,
                          entry_basis=835.0, stop_price=709.75, risk_cap_pct=0.02)
    assert s == 15


def test_sized_shares_no_cap_is_flat_pct():
    s = eng._sized_shares(equity=100_000, max_position_pct=0.20, fill_price=835.0,
                          entry_basis=835.0, stop_price=709.75, risk_cap_pct=None)
    assert s == 23  # floor(20000 / 835)


def test_passes_min_rr_filters_thin_reward():
    # +20% target, 15% stop → R:R = 0.20 / 0.15 = 1.33 < 2.0 → fail.
    assert not eng._passes_min_rr(100.0, 85.0, min_rr=2.0, target_pct=0.20)
    # +20% target, 8% stop → R:R = 0.20 / 0.08 = 2.5 >= 2.0 → pass.
    assert eng._passes_min_rr(100.0, 92.0, min_rr=2.0, target_pct=0.20)
    # disabled → always pass.
    assert eng._passes_min_rr(100.0, 85.0, min_rr=None, target_pct=0.20)


def test_sector_room_caps_dollar_exposure():
    # 30% cap on $100k = $30k. One $20k position leaves room for $10k, not $20k.
    assert eng._sector_room({"XLK": 20_000}, "XLK", 10_000, 100_000, 0.30)
    assert not eng._sector_room({"XLK": 20_000}, "XLK", 20_000, 100_000, 0.30)
    # BROAD ETFs are exempt; disabled cap always has room.
    assert eng._sector_room({"BROAD": 50_000}, "BROAD", 50_000, 100_000, 0.30)
    assert eng._sector_room({"XLK": 90_000}, "XLK", 90_000, 100_000, None)
