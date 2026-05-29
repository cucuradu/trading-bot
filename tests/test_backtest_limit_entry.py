"""Tests for the Phase G1 limit-entry path through the backtest engine.

The engine should:
  - hold an EntryIntent across bars until a bar covers the planned price,
    then fill at the planned price (or better, on a gap-down),
  - drop the intent after `ttl_bars` if no fill,
  - respect the same sector cap and max_positions as legacy fills,
  - leave the legacy (sym, price) tuple path unchanged.
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from backtest.engine import BacktestConfig, Engine  # noqa: E402
from backtest.entry_simulator import EntryIntent  # noqa: E402


def _make_constant_bars(symbols, n_days=300, start=date(2024, 1, 2)):
    """Synthesize OHLCV frames with controllable bar ranges.

    Each symbol gets `n_days` weekdays starting at `start`, Close = 100.0,
    High/Low straddle close by ±0.5%, Open = Close. SPY and ^VIX use stable
    values that classify the regime as Neutral.
    """
    idx = pd.bdate_range(start=start, periods=n_days)
    bars: dict[str, pd.DataFrame] = {}
    for sym in symbols:
        df = pd.DataFrame({
            "Open": 100.0, "High": 100.5, "Low": 99.5,
            "Close": 100.0, "Volume": 1_000_000,
        }, index=idx)
        bars[sym] = df
    # SPY / VIX needed for regime classification.
    bars["SPY"] = pd.DataFrame({
        "Open": 500.0, "High": 502.0, "Low": 498.0,
        "Close": 500.0, "Volume": 50_000_000,
    }, index=idx)
    bars["^VIX"] = pd.DataFrame({
        "Open": 18.0, "High": 18.5, "Low": 17.5,
        "Close": 18.0, "Volume": 0,
    }, index=idx)
    return bars


def test_limit_entry_fills_when_bar_low_touches_planned_price():
    """Simulator emits a single PULLBACK at planned=95.0. The next bar
    dips to 94.0 — the limit should fill at 95.0."""
    bars = _make_constant_bars(["AAPL"], n_days=60)
    # Make day-2 a dip that touches the limit price.
    aapl = bars["AAPL"].copy()
    aapl.iloc[1, aapl.columns.get_loc("Low")] = 94.0
    aapl.iloc[1, aapl.columns.get_loc("Open")] = 100.0  # opens at 100, dips to 94 intra-bar
    bars["AAPL"] = aapl

    emitted = {"count": 0}
    def sim(**kwargs):
        emitted["count"] += 1
        # Emit only on day 0 — then sit on the pending order
        if emitted["count"] == 1:
            return [EntryIntent(symbol="AAPL", planned_entry=95.0,
                                setup_type="PULLBACK", ttl_bars=3)]
        return []

    eng = Engine(bars, entry_simulator=sim)
    cfg = BacktestConfig(start=bars["SPY"].index[0].date(),
                         end=bars["SPY"].index[-1].date(),
                         apply_regime_gating=False)
    result = eng.run(cfg)

    # Expect exactly one position opened (on bar 1 when low touched 95).
    # It'll close at end-of-window via the force-close logic.
    assert len(result.trades) == 1
    t = result.trades[0]
    assert t.symbol == "AAPL"
    # Fill at min(open=100, limit=95) = 95
    assert t.entry_price == pytest.approx(95.0, rel=1e-6)


def test_limit_entry_fills_at_open_on_gap_down():
    """Bar opens at 92 (below the 95 limit) — fill at the open, not the limit."""
    bars = _make_constant_bars(["AAPL"], n_days=60)
    aapl = bars["AAPL"].copy()
    aapl.iloc[1, aapl.columns.get_loc("Open")] = 92.0
    aapl.iloc[1, aapl.columns.get_loc("Low")] = 90.0
    aapl.iloc[1, aapl.columns.get_loc("High")] = 93.0
    aapl.iloc[1, aapl.columns.get_loc("Close")] = 92.5
    bars["AAPL"] = aapl

    state = {"count": 0}
    def sim(**kwargs):
        state["count"] += 1
        if state["count"] == 1:
            return [EntryIntent(symbol="AAPL", planned_entry=95.0,
                                setup_type="PULLBACK", ttl_bars=3)]
        return []

    eng = Engine(bars, entry_simulator=sim)
    cfg = BacktestConfig(start=bars["SPY"].index[0].date(),
                         end=bars["SPY"].index[-1].date(),
                         apply_regime_gating=False)
    result = eng.run(cfg)
    assert len(result.trades) == 1
    # Fill at min(open=92, limit=95) = 92
    assert result.trades[0].entry_price == pytest.approx(92.0, rel=1e-6)


def test_limit_entry_expires_after_ttl_without_fill():
    """All bars stay at 99.5–100.5; the 95 limit never gets hit. ttl=2 → drop."""
    bars = _make_constant_bars(["AAPL"], n_days=60)
    state = {"count": 0}
    def sim(**kwargs):
        state["count"] += 1
        if state["count"] == 1:
            return [EntryIntent(symbol="AAPL", planned_entry=95.0,
                                setup_type="PULLBACK", ttl_bars=2)]
        return []

    eng = Engine(bars, entry_simulator=sim)
    cfg = BacktestConfig(start=bars["SPY"].index[0].date(),
                         end=bars["SPY"].index[-1].date(),
                         apply_regime_gating=False)
    result = eng.run(cfg)
    assert len(result.trades) == 0  # never filled


def test_breakout_intent_fills_when_bar_high_crosses_stop_price():
    bars = _make_constant_bars(["AAPL"], n_days=60)
    aapl = bars["AAPL"].copy()
    # bar 1 opens at 100, ranges up to 105 → triggers the 102 buy-stop
    aapl.iloc[1, aapl.columns.get_loc("High")] = 105.0
    aapl.iloc[1, aapl.columns.get_loc("Open")] = 100.0
    bars["AAPL"] = aapl

    state = {"count": 0}
    def sim(**kwargs):
        state["count"] += 1
        if state["count"] == 1:
            return [EntryIntent(symbol="AAPL", planned_entry=102.0,
                                setup_type="BREAKOUT", ttl_bars=3)]
        return []

    eng = Engine(bars, entry_simulator=sim)
    cfg = BacktestConfig(start=bars["SPY"].index[0].date(),
                         end=bars["SPY"].index[-1].date(),
                         apply_regime_gating=False)
    result = eng.run(cfg)
    assert len(result.trades) == 1
    # Fill at max(open=100, stop=102) = 102
    assert result.trades[0].entry_price == pytest.approx(102.0, rel=1e-6)


def test_legacy_tuple_simulator_still_works():
    """An old-style simulator returning (sym, price) tuples must continue
    to fill at the proposed price on the same bar."""
    bars = _make_constant_bars(["AAPL"], n_days=60)
    state = {"count": 0}
    def sim(**kwargs):
        state["count"] += 1
        if state["count"] == 1:
            return [("AAPL", 100.0)]
        return []

    eng = Engine(bars, entry_simulator=sim)
    cfg = BacktestConfig(start=bars["SPY"].index[0].date(),
                         end=bars["SPY"].index[-1].date(),
                         apply_regime_gating=False)
    result = eng.run(cfg)
    assert len(result.trades) == 1
    assert result.trades[0].entry_price == pytest.approx(100.0, rel=1e-6)


def test_pending_intent_does_not_consume_position_slot():
    """A pending order should not count toward max_positions until it fills."""
    bars = _make_constant_bars(["AAA", "BBB"], n_days=60)
    state = {"count": 0}
    def sim(*, open_symbols, **kwargs):
        state["count"] += 1
        # On day 0, propose AAA as a pending order (never fills).
        # On day 1, simulator sees AAA in open_symbols (because engine merges
        # positions + pending_orders) and proposes BBB instead.
        if state["count"] == 1:
            return [EntryIntent(symbol="AAA", planned_entry=50.0,
                                setup_type="PULLBACK", ttl_bars=10)]
        if state["count"] == 2:
            assert "AAA" in open_symbols  # pending blocks duplicate proposals
            return [("BBB", 100.0)]
        return []

    eng = Engine(bars, entry_simulator=sim)
    cfg = BacktestConfig(start=bars["SPY"].index[0].date(),
                         end=bars["SPY"].index[-1].date(),
                         max_positions=2,
                         apply_regime_gating=False)
    result = eng.run(cfg)
    # BBB filled; AAA pending forever and never filled.
    assert {t.symbol for t in result.trades} == {"BBB"}
