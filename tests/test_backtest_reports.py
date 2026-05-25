"""Tests for backtest/reports.py — equity-curve and trade metrics."""
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

import reports as br  # noqa: E402
from engine import ClosedTradeRecord  # noqa: E402


def _curve(values: list[float]) -> pd.Series:
    idx = pd.date_range("2024-01-01", periods=len(values), freq="B")
    return pd.Series(values, index=idx, name="equity")


def _trade(r: float, pnl: float, *, sector: str = "XLK",
           regime: str = "Bull", exit_reason: str = "trailing_stop") -> ClosedTradeRecord:
    return ClosedTradeRecord(
        symbol="AAPL",
        entry_date=date(2024, 1, 1), exit_date=date(2024, 1, 10),
        entry_price=100.0, exit_price=100 + r * 10,
        initial_stop=90.0, shares=100,
        pnl=pnl, r_multiple=r,
        sector=sector, regime_at_entry=regime, exit_reason=exit_reason,
    )


# ---------------- equity_curve_metrics ----------------

def test_equity_curve_metrics_total_return():
    curve = _curve([100_000, 105_000, 110_000])
    m = br.equity_curve_metrics(curve)
    assert m["total_return_pct"] == pytest.approx(10.0, abs=0.01)


def test_equity_curve_metrics_max_drawdown():
    # Peak at 110, trough at 99 → -10% drawdown
    curve = _curve([100, 110, 99, 105])
    m = br.equity_curve_metrics(curve)
    assert m["max_drawdown_pct"] == pytest.approx(-10.0, abs=0.01)


def test_equity_curve_metrics_zero_volatility_yields_zero_sharpe():
    curve = _curve([100_000] * 10)
    m = br.equity_curve_metrics(curve)
    assert m["sharpe"] == 0.0


def test_equity_curve_metrics_empty_curve_returns_zeros():
    m = br.equity_curve_metrics(pd.Series(dtype=float))
    assert m["total_return_pct"] == 0.0
    assert m["sharpe"] == 0.0


def test_equity_curve_metrics_handles_single_point():
    m = br.equity_curve_metrics(_curve([100_000]))
    assert m["total_return_pct"] == 0.0


# ---------------- trade_metrics ----------------

def test_trade_metrics_empty_returns_none_fields():
    m = br.trade_metrics([])
    assert m["win_rate"] is None
    assert m["profit_factor"] is None
    assert m["n_trades"] == 0


def test_trade_metrics_computes_win_rate_and_pf():
    trades = [
        _trade(r=2.0, pnl=200),
        _trade(r=2.0, pnl=200),
        _trade(r=-1.0, pnl=-100),
    ]
    m = br.trade_metrics(trades)
    assert m["win_rate"] == pytest.approx(2 / 3, abs=0.001)
    assert m["profit_factor"] == pytest.approx(400 / 100)
    assert m["avg_r_win"] == pytest.approx(2.0)
    assert m["avg_r_loss"] == pytest.approx(-1.0)
    assert m["expectancy"] == pytest.approx((2 / 3) * 2.0 - (1 / 3) * 1.0, abs=0.001)


def test_trade_metrics_all_winners_no_profit_factor():
    trades = [_trade(r=1.5, pnl=150), _trade(r=2.0, pnl=200)]
    m = br.trade_metrics(trades)
    assert m["profit_factor"] is None
    assert m["expectancy"] is None


# ---------------- sector_pnl ----------------

def test_sector_pnl_groups_by_sector():
    trades = [
        _trade(r=1.0, pnl=100, sector="XLK"),
        _trade(r=2.0, pnl=200, sector="XLK"),
        _trade(r=-1.0, pnl=-150, sector="XLF"),
    ]
    assert br.sector_pnl(trades) == {"XLK": 300.0, "XLF": -150.0}


# ---------------- regime_breakdown ----------------

def test_regime_breakdown_buckets_correctly():
    trades = [
        _trade(r=2.0, pnl=200, regime="Bull"),
        _trade(r=-1.0, pnl=-100, regime="Bull"),
        _trade(r=-1.0, pnl=-100, regime="Caution"),
    ]
    b = br.regime_breakdown(trades)
    assert b["Bull"]["n"] == 2
    assert b["Bull"]["wins"] == 1
    assert b["Bull"]["pnl"] == 100.0
    assert b["Bull"]["win_rate"] == pytest.approx(0.5)
    assert b["Caution"]["n"] == 1
    assert b["Caution"]["win_rate"] == 0.0


# ---------------- exit_reason_breakdown ----------------

def test_exit_reason_breakdown_counts():
    trades = [
        _trade(r=1.0, pnl=100, exit_reason="trailing_stop"),
        _trade(r=1.0, pnl=100, exit_reason="trailing_stop"),
        _trade(r=-1.0, pnl=-100, exit_reason="hard_cut"),
    ]
    b = br.exit_reason_breakdown(trades)
    assert b["trailing_stop"] == 2
    assert b["hard_cut"] == 1


# ---------------- markdown report sanity ----------------

class _FakeResult:
    """Minimal mock to drive write_markdown_report without a full backtest."""
    def __init__(self):
        from engine import BacktestConfig
        self.config = BacktestConfig(start=date(2024, 1, 1), end=date(2024, 12, 31))
        self.trades = [_trade(r=2.0, pnl=200), _trade(r=-1.0, pnl=-100)]
        self.equity_curve = _curve([100_000, 101_000, 100_000, 101_000])
        self.regime_history = []
        self.lock_triggered = False
        self.final_equity = 100_100.0
        self.peak_equity = 101_000.0


def test_write_markdown_report_creates_file(tmp_path):
    result = _FakeResult()
    benches = {"SPY buy-hold": _curve([100_000, 100_500, 101_000, 101_500])}
    path = br.write_markdown_report(
        result=result, benchmarks=benches, run_name="unit-test",
        out_dir=tmp_path,
    )
    assert path.exists()
    contents = path.read_text()
    assert "Backtest report" in contents
    assert "SPY buy-hold" in contents
    assert "XLK" in contents  # sector attribution table
    assert "Bull" in contents  # regime breakdown
