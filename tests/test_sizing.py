"""Tests for scripts/sizing.py — flat 20% → Half-Kelly switchover at N=30."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import sizing as sz  # noqa: E402
from trade_log import ClosedTrade  # noqa: E402


def _trade(r: float, pnl: float = 100) -> ClosedTrade:
    """Minimal trade fixture: only r_multiple matters for sizing."""
    return ClosedTrade(
        symbol="AAPL", exit_date=date(2026, 5, 23),
        entry_price=100.0, exit_price=100 + r * 10, initial_stop=90.0,
        shares=10, pnl=pnl, r_multiple=r,
    )


# ---------------- N < 30 → flat 20% ----------------

def test_no_trades_yields_flat_20pct():
    r = sz.compute_size(regime="Bull", trades=[])
    assert r.method == "flat_20pct"
    assert r.size_pct == 20.0
    assert r.n_closed == 0
    assert r.kelly_f is None


def test_below_threshold_yields_flat_20pct_regardless_of_regime():
    # 29 trades — one shy of threshold — still flat.
    trades = [_trade(r=1.0) for _ in range(29)]
    for regime in ("Bull", "Neutral", "Caution", "Defensive"):
        r = sz.compute_size(regime=regime, trades=trades)
        assert r.method == "flat_20pct"
        assert r.size_pct == 20.0


def test_exactly_at_threshold_switches_to_half_kelly():
    # 30 wins-and-losses mix → switchover triggered.
    trades = [_trade(r=2.0) for _ in range(20)] + [_trade(r=-1.0) for _ in range(10)]
    r = sz.compute_size(regime="Bull", trades=trades)
    assert r.method == "half_kelly"
    assert r.n_closed == 30


# ---------------- Kelly math ----------------

def test_half_kelly_known_W_R_match_formula():
    # W = 0.6, avg_R_win = 2, avg_R_loss = -1 → payoff = 2, f = 0.6 - 0.4/2 = 0.4,
    # half_kelly = 0.2 → 20% raw. Bull regime ×1.0 → 20% pre-clamp, clamped to cap.
    trades = [_trade(r=2.0) for _ in range(18)] + [_trade(r=-1.0) for _ in range(12)]
    r = sz.compute_size(regime="Bull", trades=trades)
    assert r.method == "half_kelly"
    assert r.win_rate == pytest.approx(0.6)
    assert r.payoff_ratio == pytest.approx(2.0)
    assert r.kelly_f == pytest.approx(0.4)
    assert r.half_kelly_raw_pct == pytest.approx(20.0)
    assert r.size_pct == 20.0  # at cap exactly
    assert r.clamped is False


def test_kelly_below_floor_clamps_to_floor():
    # Mediocre stats — Kelly tiny.
    # W = 0.50, payoff = 1.2 → f = 0.5 - 0.5/1.2 = 0.083; half = 0.0417 → 4.17%.
    # Floor 8% → clamped up.
    trades = [_trade(r=1.2) for _ in range(15)] + [_trade(r=-1.0) for _ in range(15)]
    r = sz.compute_size(regime="Bull", trades=trades)
    assert r.size_pct == sz.FLOOR_PCT
    assert r.clamped is True


def test_kelly_above_cap_clamps_to_cap():
    # Excellent stats: W = 0.8, payoff = 3 → f = 0.8 - 0.2/3 = 0.733; half = 36.7%.
    # Bull regime ×1.0 → still 36.7% → clamped to 20% cap.
    trades = [_trade(r=3.0) for _ in range(24)] + [_trade(r=-1.0) for _ in range(6)]
    r = sz.compute_size(regime="Bull", trades=trades)
    assert r.size_pct == sz.CAP_PCT
    assert r.clamped is True
    assert r.half_kelly_raw_pct > sz.CAP_PCT


def test_negative_kelly_returns_floor():
    # W = 0.3, payoff = 1 → f = 0.3 - 0.7/1 = -0.4 → max(0, f) = 0 → 0% raw → clamped to floor.
    trades = [_trade(r=1.0) for _ in range(9)] + [_trade(r=-1.0) for _ in range(21)]
    r = sz.compute_size(regime="Bull", trades=trades)
    assert r.kelly_f < 0
    assert r.half_kelly_raw_pct == 0.0
    assert r.size_pct == sz.FLOOR_PCT


# ---------------- Regime modulation ----------------

def test_neutral_regime_scales_down():
    # Same Kelly inputs as the cap-clamping test, but Neutral ×0.85 → 36.7 × 0.85 = 31.2 → still cap.
    # Use less extreme stats so we land within the band.
    # W = 0.6, payoff = 1.6 → f = 0.6 - 0.4/1.6 = 0.35; half = 17.5% raw.
    # Bull ×1.0 → 17.5%; Neutral ×0.85 → 14.875%.
    trades = [_trade(r=1.6) for _ in range(18)] + [_trade(r=-1.0) for _ in range(12)]
    bull = sz.compute_size(regime="Bull", trades=trades)
    neutral = sz.compute_size(regime="Neutral", trades=trades)
    assert bull.size_pct == pytest.approx(17.5, abs=0.01)
    assert neutral.size_pct == pytest.approx(17.5 * 0.85, abs=0.01)
    assert neutral.regime_factor == 0.85


def test_caution_regime_scales_down_further():
    trades = [_trade(r=1.6) for _ in range(18)] + [_trade(r=-1.0) for _ in range(12)]
    caution = sz.compute_size(regime="Caution", trades=trades)
    # 17.5% × 0.50 = 8.75% → above floor, not clamped
    assert caution.size_pct == pytest.approx(17.5 * 0.50, abs=0.01)


def test_defensive_regime_falls_to_floor():
    # ×0.0 → 0% pre-clamp → floor 8%.
    trades = [_trade(r=2.0) for _ in range(20)] + [_trade(r=-1.0) for _ in range(10)]
    r = sz.compute_size(regime="Defensive", trades=trades)
    assert r.regime_factor == 0.0
    assert r.size_pct == sz.FLOOR_PCT
    assert r.clamped is True


def test_unknown_regime_defaults_to_neutral_factor():
    trades = [_trade(r=2.0) for _ in range(20)] + [_trade(r=-1.0) for _ in range(10)]
    r = sz.compute_size(regime="Euphoria", trades=trades)
    assert r.regime_factor == sz.REGIME_FACTORS["Neutral"]


# ---------------- Degenerate samples ----------------

def test_all_winners_falls_to_floor():
    # N=30, no losses → degenerate, default to floor.
    trades = [_trade(r=1.5) for _ in range(30)]
    r = sz.compute_size(regime="Bull", trades=trades)
    assert r.method == "half_kelly"
    assert r.size_pct == sz.FLOOR_PCT
    assert r.payoff_ratio is None


def test_all_losers_falls_to_floor():
    # N=30, no wins → degenerate (Kelly would be negative anyway).
    trades = [_trade(r=-1.0) for _ in range(30)]
    r = sz.compute_size(regime="Bull", trades=trades)
    assert r.size_pct == sz.FLOOR_PCT


# ---------------- recommended_size_pct convenience wrapper ----------------

def test_recommended_size_pct_with_equity_returns_dollars():
    trades = [_trade(r=1.0) for _ in range(5)]
    out = sz.recommended_size_pct(regime="Bull", equity=100_000, trades=trades)
    assert out["method"] == "flat_20pct"
    assert out["size_pct"] == 20.0
    assert out["size_dollars"] == 20_000.0


def test_recommended_size_pct_without_equity_omits_dollars():
    out = sz.recommended_size_pct(regime="Bull", equity=None, trades=[])
    assert "size_dollars" not in out


# ---------------- B5: per-trade risk cap (audit 2026-06-03) ----------------

def test_risk_cap_binds_on_wide_stop():
    # MU case: $20k size, $835 entry, 15% stop ($709.75) → per-share risk $125.25.
    # 2% of $100k = $2,000 cap → floor(2000/125.25) = 15 shares, well below the
    # flat 23 shares ($20k/$835). The risk cap must bind.
    out = sz.risk_capped_shares(size_dollars=20_000, entry_price=835.0,
                                stop_price=709.75, equity=100_000, risk_cap_pct=2.0)
    assert out["bound"] == "risk_cap"
    assert out["shares"] == 15
    assert out["shares"] < out["flat_shares"]
    assert out["risk_dollars"] <= 2_000.0


def test_risk_cap_does_not_bind_on_narrow_stop():
    # CAT case: 8% stop is narrow enough that flat-20% sizing stays under the cap.
    out = sz.risk_capped_shares(size_dollars=20_000, entry_price=868.0,
                                stop_price=798.56, equity=100_000, risk_cap_pct=2.0)
    assert out["bound"] == "size"
    assert out["shares"] == out["flat_shares"]


def test_risk_cap_default_is_module_constant():
    out = sz.risk_capped_shares(size_dollars=20_000, entry_price=835.0,
                                stop_price=709.75, equity=100_000)
    assert out["risk_cap_pct"] == sz.RISK_CAP_PCT


def test_risk_cap_handles_zero_or_inverted_risk():
    # stop >= entry (should never happen) → no positive per-share risk → size bound.
    out = sz.risk_capped_shares(size_dollars=20_000, entry_price=100.0,
                                stop_price=100.0, equity=100_000)
    assert out["bound"] == "size"
    assert out["shares"] == out["flat_shares"]
