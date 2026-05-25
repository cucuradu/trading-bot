"""Reference benchmark equity curves for backtest reports.

  - SPY buy-and-hold      — passive baseline
  - SPY 200-SMA trend     — naive timing baseline
  - Equal-weight random   — sample 5–6 random universe tickers weekly

Each function returns a pd.Series indexed by trading day (Timestamp) holding
notional equity in dollars assuming a starting balance of `equity_start`.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from universe import TRADING_UNIVERSE  # noqa: E402


def spy_buy_hold(spy: pd.DataFrame, equity_start: float,
                 start: date, end: date) -> pd.Series:
    """Buy SPY at start-of-window close, hold to end."""
    window = spy.loc[(spy.index.date >= start) & (spy.index.date <= end)]
    if window.empty:
        return pd.Series(dtype=float)
    base = float(window["Close"].iloc[0])
    return (window["Close"].astype(float) / base) * equity_start


def spy_200sma_trend(spy: pd.DataFrame, equity_start: float,
                     start: date, end: date) -> pd.Series:
    """Hold SPY when Close > 200-SMA, cash otherwise.

    Position state changes on the NEXT bar after the crossover (no peeking).
    """
    df = spy.copy()
    df["sma_200"] = df["Close"].astype(float).rolling(window=200).mean()
    df["signal"] = df["Close"] > df["sma_200"]
    df["position"] = df["signal"].shift(1).fillna(False)
    df["ret"] = df["Close"].pct_change().fillna(0.0)
    df["strategy_ret"] = np.where(df["position"], df["ret"], 0.0)
    df["equity"] = (1 + df["strategy_ret"]).cumprod() * equity_start
    return df.loc[(df.index.date >= start) & (df.index.date <= end), "equity"]


def equal_weight_random(bars: dict[str, pd.DataFrame], equity_start: float,
                        start: date, end: date,
                        *, n_picks: int = 5, seed: int = 42,
                        rebalance_weekly: bool = True) -> pd.Series:
    """Pick N random universe tickers, equal-weight, rebalance weekly.

    Deterministic given `seed`. Skips tickers without bars on a rebalance day.
    """
    rng = np.random.default_rng(seed)
    spy_df = bars.get("SPY")
    if spy_df is None:
        return pd.Series(dtype=float)
    cal = spy_df.loc[(spy_df.index.date >= start) & (spy_df.index.date <= end)].index
    if len(cal) == 0:
        return pd.Series(dtype=float)

    universe = sorted(s for s in TRADING_UNIVERSE if s in bars and not bars[s].empty)
    if len(universe) < n_picks:
        return pd.Series(dtype=float)

    equity = equity_start
    holdings: dict[str, int] = {}  # symbol -> shares
    equity_pts: list[tuple[pd.Timestamp, float]] = []
    last_week = None

    for ts in cal:
        # Rebalance if first day of a new ISO week (or first bar).
        iso = ts.isocalendar()
        wk = (iso.year, iso.week)
        if not holdings or (rebalance_weekly and wk != last_week):
            # Liquidate at today's close.
            if holdings:
                for sym, sh in holdings.items():
                    df = bars[sym]
                    if ts in df.index:
                        equity += sh * float(df.at[ts, "Close"])
                    elif not df.empty:
                        equity += sh * float(df["Close"].iloc[-1])
                holdings = {}
            # Pick fresh.
            picks = rng.choice(universe, size=n_picks, replace=False).tolist()
            slot = equity / n_picks
            for sym in picks:
                df = bars[sym]
                if ts not in df.index:
                    continue
                px = float(df.at[ts, "Close"])
                shares = int(slot // px) if px > 0 else 0
                if shares > 0:
                    holdings[sym] = shares
                    equity -= shares * px
            last_week = wk

        mtm = equity + sum(
            sh * float(bars[sym].at[ts, "Close"])
            for sym, sh in holdings.items()
            if ts in bars[sym].index
        )
        equity_pts.append((ts, mtm))

    return pd.Series({t: e for t, e in equity_pts}, name="equal_weight_random")
