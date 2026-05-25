"""Entry proxy: weekly top-N momentum rebalance.

We cannot simulate Claude's catalyst research, so we approximate with a
deterministic momentum filter. The simulator emits buy candidates whenever:
  - it's the first trading day of the calendar week (Monday or first open)
  - market regime is NOT Defensive
  - sector regime for the candidate is NOT Bear

Selection rule:
  1. Rank all universe tickers by 20-day percent return
  2. Drop tickers already open
  3. Drop tickers from sectors classified as Bear today
  4. Drop tickers within the 5-day earnings blackout (approximated: skip if a
     known earnings date is within 5 trading days; we don't have a historical
     calendar, so this is left as a future hook — for now we do NOT filter)
  5. Pick the top `slots` survivors

A simple correlation filter is applied: candidates must have <= 0.70 30-day
correlation with already-open positions and with each other.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

_HERE = Path(__file__).resolve().parent
_SCRIPTS = _HERE.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(_HERE))

import regime as rg  # noqa: E402
from universe import TRADING_UNIVERSE, sector_of  # noqa: E402


MOMENTUM_LOOKBACK_DAYS = 20
CORR_LOOKBACK_DAYS = 30
CORR_CAP = 0.70


def _is_first_trading_day_of_week(idx: pd.DatetimeIndex, ts: pd.Timestamp) -> bool:
    """True if `ts` is the first trading day in its ISO week within the calendar."""
    week = ts.isocalendar().week
    year = ts.isocalendar().year
    same_week = idx[
        (idx.isocalendar().week == week) & (idx.isocalendar().year == year)
    ]
    if same_week.empty:
        return False
    return same_week[0] == ts


def _classify_sector_on(bars: dict[str, pd.DataFrame], etf: str,
                        ts: pd.Timestamp) -> str:
    df = bars.get(etf)
    if df is None or ts not in df.index:
        return "Choppy"
    row = df.loc[ts]
    if pd.isna(row.get("sma_50")) or pd.isna(row.get("ret_10")):
        return "Choppy"
    return rg.classify_sector(
        price=float(row["Close"]),
        sma_50=float(row["sma_50"]),
        return_10d_pct=float(row["ret_10"]),
    )


def _max_correlation(candidate: str, others: list[str],
                     bars: dict[str, pd.DataFrame],
                     ts: pd.Timestamp,
                     lookback: int = CORR_LOOKBACK_DAYS) -> float:
    """Pearson correlation of daily returns between `candidate` and each of
    `others`, computed on the most recent `lookback` days ending at `ts`.

    Returns the maximum absolute pairwise correlation. If insufficient data, 0.0.
    """
    if not others:
        return 0.0
    series: dict[str, pd.Series] = {}
    for sym in [candidate, *others]:
        df = bars.get(sym)
        if df is None or df.empty:
            continue
        sub = df[df.index <= ts]["Close"].astype(float)
        if len(sub) < lookback + 1:
            continue
        series[sym] = sub.tail(lookback + 1).pct_change().dropna()
    if candidate not in series or len(series) < 2:
        return 0.0
    cand_rets = series[candidate]
    max_corr = 0.0
    for sym, rets in series.items():
        if sym == candidate:
            continue
        # Align on shared index.
        aligned = pd.concat([cand_rets, rets], axis=1, join="inner")
        if len(aligned) < 5:
            continue
        c = aligned.iloc[:, 0].corr(aligned.iloc[:, 1])
        if pd.isna(c):
            continue
        max_corr = max(max_corr, abs(float(c)))
    return max_corr


def make_top_n_entry_simulator() -> Callable:
    """Factory: returns an entry_simulator closure for engine.Engine."""

    def simulator(*, bars: dict[str, pd.DataFrame],
                  current_date: pd.Timestamp,
                  regime: str,
                  open_symbols: set[str],
                  equity: float,
                  slots: int) -> list[tuple[str, float]]:
        if slots <= 0 or regime == "Defensive":
            return []
        if not _is_first_trading_day_of_week(bars["SPY"].index, current_date):
            return []

        ts = current_date
        candidates: list[tuple[str, float, float]] = []  # (sym, momentum_pct, close)
        for sym in TRADING_UNIVERSE:
            if sym in open_symbols:
                continue
            df = bars.get(sym)
            if df is None or ts not in df.index:
                continue
            row = df.loc[ts]
            if pd.isna(row.get("ret_20")):
                continue
            # Sector regime filter (skip Bear).
            sec = sector_of(sym)
            if sec and sec not in {"BROAD", None}:
                sec_regime = _classify_sector_on(bars, sec, ts)
                if sec_regime == "Bear":
                    continue
            candidates.append((sym, float(row["ret_20"]), float(row["Close"])))

        candidates.sort(key=lambda x: x[1], reverse=True)

        picks: list[tuple[str, float]] = []
        picked_syms: list[str] = list(open_symbols)
        for sym, mom, px in candidates:
            if len(picks) >= slots:
                break
            corr = _max_correlation(sym, picked_syms, bars, ts)
            if corr > CORR_CAP:
                continue
            picks.append((sym, px))
            picked_syms.append(sym)
        return picks

    return simulator
