"""Tests for backtest/exit_engine.py — exit strategies + layered rule logic."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

_BACKTEST = Path(__file__).resolve().parent.parent / "backtest"
if str(_BACKTEST) not in sys.path:
    sys.path.insert(0, str(_BACKTEST))

import exit_engine as ee  # noqa: E402


def _position(*, entry_price: float = 100.0, initial_stop: float = 90.0,
              shares: int = 100, bars_held: int = 0, peak_close: float | None = None,
              current_stop_pct: float = 10.0,
              current_stop_price: float | None = None) -> ee.Position:
    return ee.Position(
        symbol="AAPL", entry_date=date(2026, 1, 1),
        entry_price=entry_price, initial_stop=initial_stop, shares=shares,
        sector="XLK", regime_at_entry="Bull", sizing_method="flat_20pct",
        current_stop_pct=current_stop_pct,
        current_stop_price=current_stop_price if current_stop_price is not None else initial_stop,
        peak_close=peak_close if peak_close is not None else entry_price,
        bars_held=bars_held,
    )


# ---------------- FixedTrail strategy ----------------

def test_fixed_trail_initial_stop_at_10_pct():
    s = ee.FixedTrail()
    pct, price = s.initial_stop(entry_price=100.0, atr_at_entry=None)
    assert pct == 10.0
    assert price == 90.0


def test_fixed_trail_never_moves_stop_down():
    s = ee.FixedTrail()
    pos = _position(peak_close=110.0, current_stop_price=99.0)
    # Bar close drops to 105; new computed stop = 105*0.9 = 94.5 (below current 99).
    pct, price = s.update_trail(pos, bar_high=106, bar_low=104, bar_close=105, atr_now=None)
    assert price >= 99.0


def test_fixed_trail_moves_stop_up_on_new_peak():
    s = ee.FixedTrail()
    pos = _position(peak_close=110.0, current_stop_price=99.0)
    pct, price = s.update_trail(pos, bar_high=121, bar_low=115, bar_close=120, atr_now=None)
    assert price == pytest.approx(120 * 0.9)


# ---------------- ATRTrail strategy ----------------

def test_atr_trail_clamps_to_floor_when_atr_low():
    s = ee.ATRTrail()
    # 2.5 × 1.0 / 100 = 2.5% → below 7% floor → clamped to 7%.
    pct, price = s.initial_stop(entry_price=100.0, atr_at_entry=1.0)
    assert pct == 7.0
    assert price == 93.0


def test_atr_trail_clamps_to_cap_when_atr_huge():
    s = ee.ATRTrail()
    # 2.5 × 8 / 100 = 20% → clamped to 15% cap.
    pct, price = s.initial_stop(entry_price=100.0, atr_at_entry=8.0)
    assert pct == 15.0
    assert price == 85.0


def test_atr_trail_passes_through_in_band():
    s = ee.ATRTrail()
    # 2.5 × 4 / 100 = 10% — within [7, 15].
    pct, price = s.initial_stop(entry_price=100.0, atr_at_entry=4.0)
    assert pct == pytest.approx(10.0)
    assert price == pytest.approx(90.0)


def test_atr_trail_falls_back_to_floor_when_atr_missing():
    s = ee.ATRTrail()
    pct, price = s.initial_stop(entry_price=100.0, atr_at_entry=None)
    assert pct == ee.ATR_FLOOR_PCT
    assert price == 93.0


# ---------------- ChandelierTrail strategy ----------------

def test_chandelier_initial_stop_uses_3x_atr():
    s = ee.ChandelierTrail()
    pct, price = s.initial_stop(entry_price=100.0, atr_at_entry=2.0)
    # 100 − 3*2 = 94 → stop_pct = 6% → clamped to floor 7% → price 93.
    assert pct == 7.0
    assert price == 93.0


def test_chandelier_initial_stop_anchors_to_high():
    s = ee.ChandelierTrail()
    # ATR=4 → 100 − 12 = 88 → 12% (in band) → price 88.
    pct, price = s.initial_stop(entry_price=100.0, atr_at_entry=4.0)
    assert pct == pytest.approx(12.0)
    assert price == pytest.approx(88.0)


# ---------------- Layered rule: trailing stop hit ----------------

def test_trail_stop_fires_when_low_breaks_through():
    pos = _position(current_stop_price=95.0)
    decision = ee.apply_post_strategy_rules(
        pos, bar_high=98, bar_low=94, bar_close=96,
        market_regime="Bull", strategy=ee.FixedTrail(), atr_now=None,
    )
    assert decision.close is True
    assert decision.reason == "trailing_stop"
    assert decision.exit_price == 95.0


# ---------------- Hard cut at R = -1 (close <= initial_stop) ----------------

def test_hard_cut_fires_when_close_at_or_below_initial_stop():
    # Initial stop at 88 (i.e., -12%, an ATR-widened stop). Bar gaps down through
    # the trail (no GTC fill) and closes at 87 (below initial_stop).
    # Use current_stop_price=80 so the trail check doesn't fire first.
    pos = _position(entry_price=100.0, initial_stop=88.0, current_stop_price=80.0)
    decision = ee.apply_post_strategy_rules(
        pos, bar_high=92, bar_low=86.5, bar_close=87,
        market_regime="Bull", strategy=ee.FixedTrail(), atr_now=None,
    )
    assert decision.close is True
    assert decision.reason == "hard_cut"


def test_hard_cut_does_not_fire_when_close_above_initial_stop():
    # ATR-widened initial stop at 88 (-12%). Close at 92 (-8%) is worse than the
    # old fixed -7% rule but still above the original planned risk; under the
    # new R<=-1 semantic, the position lives.
    pos = _position(entry_price=100.0, initial_stop=88.0, current_stop_price=80.0)
    decision = ee.apply_post_strategy_rules(
        pos, bar_high=95, bar_low=91, bar_close=92,
        market_regime="Bull", strategy=ee.FixedTrail(), atr_now=None,
    )
    assert decision.reason != "hard_cut"


# ---------------- Time stop ----------------

def test_time_stop_fires_after_10_days_flat():
    pos = _position(entry_price=100.0, current_stop_price=90.0,
                    bars_held=10, peak_close=100.0)
    decision = ee.apply_post_strategy_rules(
        pos, bar_high=100.5, bar_low=99.5, bar_close=100.0,
        market_regime="Bull", strategy=ee.FixedTrail(), atr_now=None,
    )
    assert decision.close is True
    assert decision.reason == "time_stop"


def test_time_stop_does_not_fire_when_position_in_profit():
    pos = _position(entry_price=100.0, current_stop_price=90.0,
                    bars_held=10, peak_close=105.0)
    decision = ee.apply_post_strategy_rules(
        pos, bar_high=106, bar_low=104, bar_close=105,
        market_regime="Bull", strategy=ee.FixedTrail(), atr_now=None,
    )
    assert decision.reason != "time_stop"


def test_time_stop_does_not_fire_before_10_days():
    pos = _position(entry_price=100.0, current_stop_price=90.0,
                    bars_held=9, peak_close=100.0)
    decision = ee.apply_post_strategy_rules(
        pos, bar_high=100.5, bar_low=99.5, bar_close=100.0,
        market_regime="Bull", strategy=ee.FixedTrail(), atr_now=None,
    )
    assert decision.reason != "time_stop"


# ---------------- Regime override ----------------

def test_defensive_regime_closes_winners():
    pos = _position(entry_price=100.0, current_stop_price=95.0, peak_close=110.0)
    decision = ee.apply_post_strategy_rules(
        pos, bar_high=111, bar_low=109, bar_close=110,
        market_regime="Defensive", strategy=ee.FixedTrail(), atr_now=None,
    )
    assert decision.close is True
    assert decision.reason == "regime_defensive"


def test_defensive_regime_holds_losers_for_their_stops():
    # Position underwater — let the trailing stop handle it; do NOT exit due to regime.
    pos = _position(entry_price=100.0, current_stop_price=90.0, peak_close=99.0)
    decision = ee.apply_post_strategy_rules(
        pos, bar_high=96, bar_low=94, bar_close=95,
        market_regime="Defensive", strategy=ee.FixedTrail(), atr_now=None,
    )
    assert decision.reason != "regime_defensive"


# ---------------- Profit tightening ----------------

def test_profit_tighten_at_plus_15_pct_for_fixed_trail():
    pos = _position(entry_price=100.0, current_stop_price=99.0,
                    current_stop_pct=10.0, peak_close=115.0)
    decision = ee.apply_post_strategy_rules(
        pos, bar_high=116, bar_low=114, bar_close=115,
        market_regime="Bull", strategy=ee.FixedTrail(), atr_now=None,
    )
    assert decision.close is False
    assert decision.new_stop_pct == 7.0
    # New stop price = anchor (115) × 0.93 = 106.95, must be >= prior stop.
    assert decision.new_stop_price >= 99.0


def test_profit_tighten_at_plus_20_pct():
    pos = _position(entry_price=100.0, current_stop_price=99.0,
                    current_stop_pct=7.0, peak_close=120.0)
    decision = ee.apply_post_strategy_rules(
        pos, bar_high=121, bar_low=119, bar_close=120,
        market_regime="Bull", strategy=ee.FixedTrail(), atr_now=None,
    )
    assert decision.new_stop_pct == 5.0


# ---------------- Strategy registry ----------------

def test_get_strategy_returns_correct_class():
    assert isinstance(ee.get_strategy("fixed_10"), ee.FixedTrail)
    assert isinstance(ee.get_strategy("atr_2_5x"), ee.ATRTrail)
    assert isinstance(ee.get_strategy("chandelier_3xATR22"), ee.ChandelierTrail)


def test_get_strategy_rejects_unknown_name():
    with pytest.raises(ValueError, match="unknown exit strategy"):
        ee.get_strategy("does_not_exist")


# ---------------- unrealized_pct helper ----------------

def test_unrealized_pct_zero_at_entry():
    pos = _position(entry_price=100.0)
    assert ee.unrealized_pct(pos, 100.0) == 0.0


def test_unrealized_pct_correct_at_plus_20():
    pos = _position(entry_price=100.0)
    assert ee.unrealized_pct(pos, 120.0) == pytest.approx(20.0)


def test_unrealized_pct_correct_at_minus_5():
    pos = _position(entry_price=100.0)
    assert ee.unrealized_pct(pos, 95.0) == pytest.approx(-5.0)
