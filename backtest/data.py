"""Historical bar fetcher with parquet cache.

Pulls daily OHLC for the trading universe + SPY + ^VIX from yfinance, caches
to backtest/data_cache/*.parquet. Cache is keyed by symbol; for the backtest
use case history doesn't change after the fact, so cache files never expire
unless the user deletes them or passes force_refresh=True.

Public API:
  load_bars(symbol, start, end, force_refresh=False) -> pd.DataFrame
  load_universe_bars(start, end) -> dict[str, pd.DataFrame]   # universe + SPY + ^VIX
"""
from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import yfinance as yf

# Reuse the universe definition — single source of truth.
_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from universe import TRADING_UNIVERSE  # noqa: E402


CACHE_DIR = Path(__file__).resolve().parent / "data_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Additional symbols the backtest needs beyond the trading universe.
EXTRA_SYMBOLS = frozenset({"^VIX"})  # SPY is already in the universe.

# How much extra history to fetch before `start` so indicators converge:
#   200-day SMA needs 200 prior bars; ATR(14) needs ~30; 20-day return needs 20.
INDICATOR_WARMUP_DAYS = 260


def _cache_path(symbol: str) -> Path:
    # ^VIX → caret is not filename-safe on some FS; replace with underscore.
    safe = symbol.replace("^", "_")
    return CACHE_DIR / f"{safe}.parquet"


def _fetch_bars(symbol: str, start: date, end: date) -> pd.DataFrame:
    """Single-symbol yfinance fetch with normalized output.

    Returns a DataFrame with DatetimeIndex (tz-naive, dates only) and columns:
        Open, High, Low, Close, Adj Close, Volume.
    Empty DataFrame if yfinance returned nothing.
    """
    df = yf.Ticker(symbol).history(
        start=start.isoformat(),
        end=(end + timedelta(days=1)).isoformat(),  # yfinance end is exclusive
        auto_adjust=False,
    )
    if df.empty:
        return df
    # Normalize index: drop timezone, drop time component.
    df = df.copy()
    df.index = pd.to_datetime(df.index).tz_localize(None).normalize()
    df.index.name = "Date"
    return df


def load_bars(symbol: str, start: date, end: date,
              *, force_refresh: bool = False) -> pd.DataFrame:
    """Load historical bars for one symbol.

    Reads from cache if available and the cached range covers [start, end].
    Otherwise fetches from yfinance and overwrites the cache. The cache always
    holds the widest range seen so far.
    """
    path = _cache_path(symbol)
    cached: pd.DataFrame | None = None
    if path.exists() and not force_refresh:
        try:
            cached = pd.read_parquet(path)
        except Exception:
            cached = None

    needs_fetch = (
        cached is None
        or cached.empty
        or cached.index.min().date() > start
        or cached.index.max().date() < end
    )

    if needs_fetch:
        fetch_start = start if cached is None or cached.empty else min(start, cached.index.min().date())
        fetch_end = end if cached is None or cached.empty else max(end, cached.index.max().date())
        fresh = _fetch_bars(symbol, fetch_start, fetch_end)
        if fresh.empty:
            if cached is not None and not cached.empty:
                df = cached
            else:
                raise ValueError(f"no historical data for {symbol} between {start} and {end}")
        else:
            df = fresh
            df.to_parquet(path)
    else:
        df = cached

    # Slice to the requested window.
    mask = (df.index.date >= start) & (df.index.date <= end)
    return df.loc[mask].copy()


def load_universe_bars(start: date, end: date,
                       *, include_extras: bool = True,
                       force_refresh: bool = False) -> dict[str, pd.DataFrame]:
    """Load bars for the full trading universe + extras (SPY/^VIX) over [start, end].

    Adds INDICATOR_WARMUP_DAYS of prior history so callers can compute 200-SMA,
    ATR(14), 20-day return at every bar in [start, end].
    """
    fetch_start = start - timedelta(days=INDICATOR_WARMUP_DAYS)
    symbols = set(TRADING_UNIVERSE)
    if include_extras:
        symbols |= EXTRA_SYMBOLS
    out: dict[str, pd.DataFrame] = {}
    for sym in sorted(symbols):
        try:
            out[sym] = load_bars(sym, fetch_start, end, force_refresh=force_refresh)
        except Exception as e:
            print(f"  warn: failed to load {sym}: {e}", file=sys.stderr)
            continue
    return out


def trading_days_between(df: pd.DataFrame, start: date, end: date) -> pd.DatetimeIndex:
    """Return the DatetimeIndex of actual trading days in [start, end] from `df`."""
    mask = (df.index.date >= start) & (df.index.date <= end)
    return df.loc[mask].index
