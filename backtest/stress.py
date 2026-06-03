"""Synthetic crash injection (C4).

The engine already supports per-bar shock injection via config flags; this
module is a thin wrapper that returns the right BacktestConfig and verifies
the expected safety nets fired.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date

from backtest.engine import BacktestConfig, BacktestResult


@dataclass
class StressReport:
    lock_triggered: bool
    hard_cut_trades: int
    regime_defensive_exits: int
    days_with_circuit_breaker: int   # naive: days where daily P&L <= -2%

    def as_dict(self) -> dict:
        return {
            "lock_triggered": self.lock_triggered,
            "hard_cut_trades": self.hard_cut_trades,
            "regime_defensive_exits": self.regime_defensive_exits,
            "days_with_circuit_breaker": self.days_with_circuit_breaker,
        }


def stress_config(base: BacktestConfig, *, shock_prob: float = 0.015,
                  shock_range: tuple[float, float] = (-0.15, -0.10),
                  seed: int = 42) -> BacktestConfig:
    """Return a copy of `base` with stress-shock fields populated.

    Uses dataclasses.replace so every other knob carries over. The previous
    hand-rolled reconstruction silently dropped max_per_sector, time_stop_days
    and time_stop_band, reverting them to defaults — so a stress run with
    custom CLI flags secretly ran a different config than the user asked for.
    """
    return replace(
        base,
        apply_stress_shocks=True,
        stress_shock_prob=shock_prob,
        stress_shock_range=shock_range,
        stress_seed=seed,
    )


def summarize_stress(result: BacktestResult) -> StressReport:
    hard_cuts = sum(1 for t in result.trades if t.exit_reason == "hard_cut")
    regime_exits = sum(1 for t in result.trades if t.exit_reason == "regime_defensive")
    # Daily circuit-breaker proxy: how many days dropped ≥ 2% bar-over-bar?
    breaker_days = 0
    eq = result.equity_curve
    if not eq.empty:
        rets = eq.pct_change().fillna(0)
        breaker_days = int((rets <= -0.02).sum())
    return StressReport(
        lock_triggered=result.lock_triggered,
        hard_cut_trades=hard_cuts,
        regime_defensive_exits=regime_exits,
        days_with_circuit_breaker=breaker_days,
    )
