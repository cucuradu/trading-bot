#!/usr/bin/env python3
"""Rule-based market + sector regime classifier (Phase B fallback).

Inputs come from yfinance (VIX, SPY, sector ETFs). No ML, no opinions —
purely arithmetic on price + volatility. Used by the pre-market skill when
ml-insights.json is missing or stale.

Usage:
  python scripts/regime.py current             # JSON: market regime + posture
  python scripts/regime.py sectors             # JSON: all 11 sector regimes
  python scripts/regime.py all                 # JSON: market + sectors combined
"""
from __future__ import annotations

import json
import sys

import numpy as np
import pandas as pd
import yfinance as yf

from _yf_compat import patch as _patch_yf
_patch_yf()


# ---- Market regime constants (mirror memory/TRADING-STRATEGY.md) ----

MARKET_REGIMES = ("Bull", "Neutral", "Caution", "Defensive")

POSTURE = {
    "Bull":      {"deployment_target": 0.85, "trade_slots": 3},
    "Neutral":   {"deployment_target": 0.75, "trade_slots": 2},
    "Caution":   {"deployment_target": 0.50, "trade_slots": 1},
    "Defensive": {"deployment_target": 0.00, "trade_slots": 0},
}

PERSISTENCE_BARS_REQUIRED = 3

# ---- Sector regime constants ----

SECTOR_ETFS = (
    "XLK", "XLF", "XLV", "XLE", "XLY",
    "XLP", "XLI", "XLU", "XLB", "XLRE", "XLC",
)
SECTOR_REGIMES = ("Trend", "Choppy", "Bear")


# ---------- Pure classifiers (no I/O) ----------

def classify_market(vix: float, spy: float, spy_200sma: float, spy_20d_return_pct: float) -> str:
    """Pure rule-based classification.

    Order matters: most defensive first.
    Rules (from memory/TRADING-STRATEGY.md):
      Defensive: VIX > 30
      Caution:   VIX in [22, 30] OR SPY < 200SMA
      Bull:      VIX < 15 AND SPY > 200SMA AND 20d return > 0
      Neutral:   everything else (VIX in [15, 22) AND SPY > 200SMA)
    """
    if vix > 30:
        return "Defensive"
    if vix >= 22 or spy < spy_200sma:
        return "Caution"
    if vix < 15 and spy > spy_200sma and spy_20d_return_pct > 0:
        return "Bull"
    return "Neutral"


def classify_sector(price: float, sma_50: float, return_10d_pct: float) -> str:
    """Pure sector classification.

    Order matters: Bear is the safest call to make first.
    Rules:
      Bear:   price < 50SMA OR 10d return < -4%
      Trend:  price > 50SMA AND 10d return > +2%
      Choppy: anything else
    """
    if price < sma_50 or return_10d_pct < -4.0:
        return "Bear"
    if price > sma_50 and return_10d_pct > 2.0:
        return "Trend"
    return "Choppy"


def compute_persistence(classifications: list[str]) -> int:
    """Count how many trailing entries match the last entry.

    classifications: chronological [oldest, ..., newest].
    Returns at least 1 if the list is non-empty.
    """
    if not classifications:
        return 0
    last = classifications[-1]
    count = 0
    for c in reversed(classifications):
        if c == last:
            count += 1
        else:
            break
    return count


# ---------- Data fetch + assembly ----------

def _spy_history(days: int = 260) -> pd.DataFrame:
    """Enough history for 200-SMA + 20d return + 3-day persistence window."""
    return yf.Ticker("SPY").history(period=f"{days}d", auto_adjust=False)


def _vix_history(days: int = 10) -> pd.DataFrame:
    """A handful of recent VIX closes for the persistence window."""
    return yf.Ticker("^VIX").history(period=f"{days}d", auto_adjust=False)


def _sector_history(symbol: str, days: int = 80) -> pd.DataFrame:
    """Enough for 50-day SMA + 10-day return."""
    return yf.Ticker(symbol).history(period=f"{days}d", auto_adjust=False)


def market_regime_from_history(spy: pd.DataFrame, vix: pd.DataFrame,
                               persistence_window: int = PERSISTENCE_BARS_REQUIRED) -> dict:
    """Compute today's market regime + trailing persistence from raw history.

    Pure once data is in hand — used by both the live wrapper and tests.
    """
    if len(spy) < 200 + 20:
        raise ValueError(
            f"SPY history too short: need ≥ 220 bars for 200-SMA + 20d return, got {len(spy)}"
        )
    if len(vix) < persistence_window:
        raise ValueError(f"VIX history too short: need ≥ {persistence_window} bars")

    spy_close = spy["Close"].astype(float)
    sma_200 = spy_close.rolling(window=200).mean()
    pct_20d = spy_close.pct_change(20) * 100

    # Align VIX to SPY's trading days (VIX trades on the same calendar).
    vix_close = vix["Close"].astype(float)

    # Classify each of the last `persistence_window` available bars.
    valid_idx = spy_close.dropna().index.intersection(sma_200.dropna().index).intersection(pct_20d.dropna().index)
    if len(valid_idx) < persistence_window:
        raise ValueError(f"insufficient valid bars: {len(valid_idx)} < {persistence_window}")

    tail = valid_idx[-persistence_window:]
    classifications: list[str] = []
    for ts in tail:
        spy_t = float(spy_close.loc[ts])
        sma_t = float(sma_200.loc[ts])
        pct_t = float(pct_20d.loc[ts])
        # Use the VIX close on or before ts (forward-fill).
        vix_aligned = vix_close.reindex([ts], method="ffill")
        if vix_aligned.empty or pd.isna(vix_aligned.iloc[0]):
            raise ValueError(f"no VIX value available for {ts.date()}")
        vix_t = float(vix_aligned.iloc[0])
        classifications.append(classify_market(vix_t, spy_t, sma_t, pct_t))

    current = classifications[-1]
    persistence = compute_persistence(classifications)
    stable = persistence >= PERSISTENCE_BARS_REQUIRED

    return {
        "regime": current,
        "persistence_bars": persistence,
        "stable": stable,
        "deployment_target": POSTURE[current]["deployment_target"],
        "trade_slots": POSTURE[current]["trade_slots"],
        "vix": float(vix_close.iloc[-1]),
        "spy_close": float(spy_close.iloc[-1]),
        "spy_200sma": float(sma_200.iloc[-1]),
        "spy_vs_200sma_pct": round((float(spy_close.iloc[-1]) / float(sma_200.iloc[-1]) - 1) * 100, 3),
        "spy_20d_return_pct": round(float(pct_20d.iloc[-1]), 3),
        "classifications_trailing": classifications,
        "as_of": tail[-1].strftime("%Y-%m-%d"),
    }


def sector_regime_from_history(symbol: str, hist: pd.DataFrame) -> dict:
    """Compute one sector ETF's regime + score from raw history."""
    if len(hist) < 50 + 10:
        raise ValueError(
            f"{symbol} history too short: need ≥ 60 bars, got {len(hist)}"
        )
    close = hist["Close"].astype(float)
    sma_50 = float(close.rolling(window=50).mean().iloc[-1])
    last_close = float(close.iloc[-1])
    ret_10d_pct = (last_close / float(close.iloc[-11]) - 1) * 100

    regime = classify_sector(last_close, sma_50, ret_10d_pct)
    # Score: sign indicates direction; magnitude is conviction.
    # Positive when price > SMA (trending) and momentum is positive.
    sma_dev = (last_close / sma_50 - 1) * 100
    score = round((sma_dev + ret_10d_pct) / 2 / 10, 4)  # normalize to ~[-1, 1] range

    return {
        "symbol": symbol,
        "regime": regime,
        "score": score,
        "price": round(last_close, 2),
        "sma_50": round(sma_50, 2),
        "return_10d_pct": round(ret_10d_pct, 3),
        "as_of": hist.index[-1].strftime("%Y-%m-%d"),
    }


# ---------- Public live functions ----------

def market_regime() -> dict:
    """Fetch live SPY + VIX and classify today's market regime."""
    spy = _spy_history(260)
    vix = _vix_history(10)
    return market_regime_from_history(spy, vix)


def sector_regimes() -> dict:
    """Fetch all 11 sector ETFs and classify each."""
    out: dict[str, dict] = {}
    for sym in SECTOR_ETFS:
        try:
            hist = _sector_history(sym, 80)
            out[sym] = sector_regime_from_history(sym, hist)
        except Exception as e:
            out[sym] = {"symbol": sym, "regime": None, "error": str(e)}
    return {"sectors": out}


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    cmd = sys.argv[1]
    if cmd == "current":
        print(json.dumps(market_regime(), indent=2))
    elif cmd == "sectors":
        print(json.dumps(sector_regimes(), indent=2))
    elif cmd == "all":
        m = market_regime()
        s = sector_regimes()
        print(json.dumps({"market": m, **s}, indent=2))
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
