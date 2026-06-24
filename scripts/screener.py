#!/usr/bin/env python3
"""Wall-Street-grade local screener — multi-factor ranker over the trading universe.

Deterministic, network-cheap (one batched yf.download per run), and emits output
schema-compatible with `docs/ml-insights-schema.md` `universe_ranking` so it
plugs into `scripts/ml_insights.py:resolve()` as the rule-fallback ranking.

Pipeline:
  1. fetch_universe_bars  — one yf.download for the whole universe + sector ETFs
  2. compute_factors      — 7 per-ticker factors (pure pandas)
  3. sanity gates         — drop illiquid / penny / ultra-vol / Bear-sector
  4. z-score + clip + weight-sum → ml_score
  5. rank_universe        — sorted list of {symbol, ml_score, factor_breakdown}
  6. deep_dive_shortlist  — runtime filter (open positions, sector cap, correlation)

Usage:
  python scripts/screener.py rank                  # full JSON: ranking + diagnostics
  python scripts/screener.py rank --top 20         # truncate
  python scripts/screener.py rank --json-ml-shape  # universe_ranking list (drop-in)
  python scripts/screener.py shortlist --slots 3   # deep-dive shortlist (<=6 names)
  python scripts/screener.py explain SYM           # per-factor breakdown
"""
from __future__ import annotations

import argparse
import contextlib
import io
import json
import math
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd
import yfinance as yf

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from _yf_compat import patch as _patch_yf, get_session as _yf_session  # noqa: E402
_patch_yf()
import regime as rg  # noqa: E402
from universe import TRADING_UNIVERSE, sector_of  # noqa: E402

# news_sources is best-effort — missing key returns []. Never blocks the screener.
try:
    import news_sources as ns  # noqa: E402
except Exception:
    ns = None  # type: ignore


# ---- Factor weights (sum = 1.0) ----------------------------------------
FACTOR_WEIGHTS: dict[str, float] = {
    "momentum_125d": 0.25,        # Jegadeesh-Titman 6-mo momentum (dominant signal)
    "momentum_20d": 0.10,
    "rs_vs_sector_60d": 0.18,     # "best stock in best sector" — Wall Street RS
    "technical_setup": 0.12,      # golden cross + 52w-high proximity
    "dist_from_52w_high": 0.08,
    "volume_surge": 0.08,         # institutional positioning footprint
    "vol_stability": 0.04,        # mild cost-of-vol penalty
    "catalyst": 0.15,             # Phase F+: analyst upgrades + insider buying (free Finnhub data)
}
assert abs(sum(FACTOR_WEIGHTS.values()) - 1.0) < 1e-9

# On binary macro-event days (FOMC, CPI, Core PCE, NFP within 24h), shift the
# factor weights defensively: penalize high-vol names more, trust pure momentum
# less, dial down catalyst (rating moves are noise around binary prints).
# Engaged when caller passes macro_event=True to rank_universe().
MACRO_DAY_FACTOR_WEIGHTS: dict[str, float] = {
    "momentum_125d": 0.18,
    "momentum_20d": 0.05,         # short-term noise heavier on event days
    "rs_vs_sector_60d": 0.13,
    "technical_setup": 0.13,
    "dist_from_52w_high": 0.08,
    "volume_surge": 0.13,         # volume confirms institutional positioning
    "vol_stability": 0.18,        # heavy defensive tilt on binary days
    "catalyst": 0.12,
}
assert abs(sum(MACRO_DAY_FACTOR_WEIGHTS.values()) - 1.0) < 1e-9

CATALYST_LOOKBACK_DAYS = 30
CATALYST_FETCH_WORKERS = 8

# ---- Sanity gates (drop BEFORE scoring) --------------------------------
MIN_DOLLAR_VOLUME_20D = 50_000_000.0   # $50M avg daily
MIN_PRICE = 5.00                       # penny rule
MAX_ATR_PCT = 8.0                      # single-day blow-up risk vs 20% sizing
MIN_BARS = 220                         # 200-SMA + 20d return need 220 bars
ZSCORE_CLIP = 3.0

# ---- Output schema constants -------------------------------------------
SECTOR_ETFS = tuple(rg.SECTOR_ETFS)


# ========================================================================
# Bar fetch
# ========================================================================

def fetch_universe_bars(
    symbols: list[str],
    period_days: int = 400,
) -> dict[str, pd.DataFrame]:
    """One batched yf.download for the whole universe.

    Returns {symbol: DataFrame[Open, High, Low, Close, Volume]}.
    Symbols with fewer than MIN_BARS bars are silently dropped.

    Pattern mirrors market_data.correlation() line 216 — the only proven
    batch-fetch in the codebase.
    """
    uniq = sorted({s.strip().upper() for s in symbols})
    if not uniq:
        return {}
    data = yf.download(
        uniq,
        period=f"{period_days}d",
        auto_adjust=False,
        progress=False,
        group_by="ticker",
        threads=True,
        session=_yf_session(),
    )

    out: dict[str, pd.DataFrame] = {}
    if isinstance(data.columns, pd.MultiIndex):
        for sym in uniq:
            if sym in data.columns.get_level_values(0):
                df = data[sym].dropna(how="all")
                if len(df) >= MIN_BARS:
                    out[sym] = df
    elif len(uniq) == 1:
        df = data.dropna(how="all")
        if len(df) >= MIN_BARS:
            out[uniq[0]] = df

    return out


# ========================================================================
# Catalyst signals (analyst rating changes + insider transactions, Finnhub)
# ========================================================================

def _parse_iso_date(s: str) -> date | None:
    """Best-effort ISO date parse — Finnhub uses 'YYYY-MM-DD HH:MM:SS' or epoch."""
    if not s or not isinstance(s, str):
        return None
    try:
        return datetime.fromisoformat(s.split()[0].split("T")[0]).date()
    except Exception:
        return None


def _catalyst_signal_for_symbol(symbol: str, lookback_days: int) -> dict:
    """One ticker's analyst + insider score over the lookback window.

    Returns {symbol, analyst_net_upgrades, insider_net_buy_shares, catalyst_raw}.
    All zeros when news_sources/key are missing or no data — neutral, not penalized.
    """
    if ns is None:
        return {
            "symbol": symbol,
            "analyst_net_upgrades": 0.0,
            "insider_net_buy_shares": 0.0,
            "catalyst_raw": 0.0,
        }
    cutoff = date.today() - timedelta(days=lookback_days)

    # Analyst: count "up" actions minus "down" actions in the window
    analyst_net = 0
    try:
        for item in ns.finnhub_analyst_changes(symbol):
            d = _parse_iso_date(item.get("published", ""))
            if d is None or d < cutoff:
                continue
            title = (item.get("title") or "").lower()
            if "upgrade" in title:
                analyst_net += 1
            elif "downgrade" in title:
                analyst_net -= 1
    except Exception:
        pass

    # Insider: sum of share changes (BUY = +shares, SELL = -shares) in window
    insider_net = 0.0
    try:
        for item in ns.finnhub_insider(symbol):
            d = _parse_iso_date(item.get("published", ""))
            if d is None or d < cutoff:
                continue
            title = (item.get("title") or "")
            # Title format: "Insider BUY <name> (<change> sh)" — parse the change number
            import re as _re
            m = _re.search(r"\(([\-+]?[0-9]+(?:\.[0-9]+)?)\s*sh\)", title)
            if m:
                try:
                    insider_net += float(m.group(1))
                except ValueError:
                    pass
    except Exception:
        pass

    # Composite raw score: 1 upgrade ≈ 1 unit; 10k insider shares ≈ 1 unit (log-scaled).
    insider_unit = math.copysign(math.log10(abs(insider_net) + 1), insider_net) if insider_net else 0.0
    catalyst_raw = float(analyst_net) + insider_unit

    return {
        "symbol": symbol,
        "analyst_net_upgrades": float(analyst_net),
        "insider_net_buy_shares": float(insider_net),
        "catalyst_raw": float(catalyst_raw),
    }


def compute_catalyst_signals(
    symbols: list[str],
    lookback_days: int = CATALYST_LOOKBACK_DAYS,
    max_workers: int = CATALYST_FETCH_WORKERS,
) -> pd.DataFrame:
    """Parallel Finnhub fetch — analyst rating changes + insider transactions.

    Returns DataFrame indexed by symbol with columns: analyst_net_upgrades,
    insider_net_buy_shares, catalyst_raw. Missing data → 0 (neutral).

    Safe to call without FINNHUB_KEY: every signal will be 0; catalyst factor
    will z-score to 0 and contribute nothing to ml_score. No-op fallback.
    """
    if not symbols:
        return pd.DataFrame(columns=["analyst_net_upgrades", "insider_net_buy_shares", "catalyst_raw"])
    rows: list[dict] = []
    # Finnhub free tier returns 403 on /upgrade-downgrade and 429 on /insider-transactions
    # when called in parallel. news_sources.py logs these per-call to stderr, which
    # spams pre-market output. The screener already defaults missing data to 0
    # (neutral, doesn't affect ranking), so the warnings are pure noise — suppress them.
    with contextlib.redirect_stderr(io.StringIO()):
        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futures = [ex.submit(_catalyst_signal_for_symbol, s, lookback_days) for s in symbols]
            for fut in futures:
                try:
                    rows.append(fut.result(timeout=20))
                except Exception:
                    pass
    df = pd.DataFrame(rows).set_index("symbol") if rows else \
        pd.DataFrame(columns=["analyst_net_upgrades", "insider_net_buy_shares", "catalyst_raw"])
    return df


# ========================================================================
# Per-ticker factors
# ========================================================================

def _safe_pct_change(series: pd.Series, lookback: int) -> float:
    """Return (last / last-lookback) - 1, or NaN if not enough data."""
    if len(series) <= lookback:
        return float("nan")
    a = float(series.iloc[-1])
    b = float(series.iloc[-(lookback + 1)])
    if b == 0 or not np.isfinite(a) or not np.isfinite(b):
        return float("nan")
    return a / b - 1.0


def compute_factors(
    bars: dict[str, pd.DataFrame],
    sector_of_fn: Callable[[str], str | None] = sector_of,
    catalyst_signals: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Compute raw per-ticker factor values + sanity-gate fields.

    Returns a DataFrame indexed by symbol. Columns include every factor in
    FACTOR_WEIGHTS plus the gate-input columns (price, dollar_vol_20d_med,
    atr_pct, sector). NaN values mean "could not compute" — handled
    downstream as a drop reason.

    catalyst_signals: optional DataFrame from compute_catalyst_signals() with
    `catalyst_raw` column indexed by symbol. When omitted, the catalyst factor
    defaults to 0 (neutral — z-scores to 0, contributes nothing).
    """
    rows: dict[str, dict] = {}
    # Pre-compute sector ETF 60d returns once (needed for RS factor).
    sector_ret_60d: dict[str, float] = {}
    for etf in SECTOR_ETFS:
        if etf in bars:
            sector_ret_60d[etf] = _safe_pct_change(bars[etf]["Close"], 60)

    for sym, df in bars.items():
        close = df["Close"].astype(float)
        high = df["High"].astype(float)
        low = df["Low"].astype(float)
        vol = df["Volume"].astype(float)
        last_close = float(close.iloc[-1]) if len(close) else float("nan")

        # Liquidity gate input: 20d median dollar volume
        if len(close) >= 20:
            dv_20 = (close * vol).tail(20).median()
            dollar_vol_20d_med = float(dv_20) if pd.notna(dv_20) else float("nan")
        else:
            dollar_vol_20d_med = float("nan")

        # ATR(14) % of price (single-day vol gate input + factor 7)
        try:
            prev_close = close.shift(1)
            tr = pd.concat(
                [(high - low), (high - prev_close).abs(), (low - prev_close).abs()],
                axis=1,
            ).max(axis=1).iloc[1:]
            atr_series = tr.ewm(alpha=1 / 14, adjust=False, min_periods=14).mean()
            atr_val = float(atr_series.iloc[-1])
            atr_pct = (atr_val / last_close) * 100 if last_close > 0 else float("nan")
        except Exception:
            atr_pct = float("nan")

        # Factor 1: medium-term momentum (125d)
        mom_125 = _safe_pct_change(close, 125)
        # Factor 2: short-term momentum (20d)
        mom_20 = _safe_pct_change(close, 20)
        # Factor 3: relative strength vs sector (60d)
        # BROAD ETFs (SPY/QQQ/IWM/DIA) have no sector benchmark → neutral RS (0).
        sec = sector_of_fn(sym)
        own_60 = _safe_pct_change(close, 60)
        if sec == "BROAD":
            rs_60 = 0.0
        elif sec and sec in sector_ret_60d \
                and pd.notna(own_60) and pd.notna(sector_ret_60d[sec]):
            rs_60 = own_60 - sector_ret_60d[sec]
        else:
            rs_60 = float("nan")

        # Factor 4: technical setup — continuous score in [0, 1]
        # 50% weight: golden cross (Close > SMA50 > SMA200)
        # 50% weight: proximity to 52w high (linear: 1 at high, 0 at <=20% below)
        if len(close) >= 200:
            sma_50 = float(close.rolling(50).mean().iloc[-1])
            sma_200 = float(close.rolling(200).mean().iloc[-1])
            cross_score = 1.0 if (last_close > sma_50 > sma_200) else 0.0
            high_252 = float(close.tail(252).max()) if len(close) >= 252 else float(close.max())
            if high_252 > 0:
                pct_below_high = (high_252 - last_close) / high_252
                prox = max(0.0, 1.0 - (pct_below_high / 0.20))  # 1 at high, 0 at 20% below
            else:
                prox = 0.0
            technical_setup = 0.5 * cross_score + 0.5 * prox
        else:
            technical_setup = float("nan")

        # Factor 5: distance from 52w high (1 = at high, lower = further)
        if len(close) >= 252:
            high_252 = float(close.tail(252).max())
            dist = 1.0 - (high_252 - last_close) / max(last_close, 1e-9)
            dist_from_52w_high = max(0.0, min(1.0, dist))
        else:
            dist_from_52w_high = float("nan")

        # Factor 6: volume surge — last 5d avg / preceding 15d avg - 1
        if len(vol) >= 20:
            v_recent = float(vol.iloc[-5:].mean())
            v_prior = float(vol.iloc[-20:-5].mean())
            if v_prior > 0:
                volume_surge = v_recent / v_prior - 1.0
            else:
                volume_surge = float("nan")
        else:
            volume_surge = float("nan")

        # Factor 7: vol-stability (inverse ATR%) — negate so lower atr = higher score
        vol_stability = -atr_pct if pd.notna(atr_pct) else float("nan")

        # Factor 8: catalyst (analyst upgrades + insider net-buy). Defaults to 0
        # if no catalyst_signals provided (neutral; doesn't affect ranking).
        catalyst = 0.0
        if catalyst_signals is not None and sym in catalyst_signals.index:
            raw = catalyst_signals.at[sym, "catalyst_raw"]
            if pd.notna(raw):
                catalyst = float(raw)

        rows[sym] = {
            "price": last_close,
            "dollar_vol_20d_med": dollar_vol_20d_med,
            "atr_pct": atr_pct,
            "sector": sec,
            "momentum_125d": mom_125,
            "momentum_20d": mom_20,
            "rs_vs_sector_60d": rs_60,
            "technical_setup": technical_setup,
            "dist_from_52w_high": dist_from_52w_high,
            "volume_surge": volume_surge,
            "vol_stability": vol_stability,
            "catalyst": catalyst,
        }

    return pd.DataFrame.from_dict(rows, orient="index")


# ========================================================================
# Ranking
# ========================================================================

def _drop_reason(
    row: pd.Series,
    sector_regimes: dict[str, dict],
) -> str | None:
    """Apply sanity gates. Return drop reason string or None to keep."""
    if pd.isna(row.get("price")) or row["price"] < MIN_PRICE:
        return "penny"
    dv = row.get("dollar_vol_20d_med")
    if pd.isna(dv) or dv < MIN_DOLLAR_VOLUME_20D:
        return "illiquid"
    ap = row.get("atr_pct")
    if pd.isna(ap) or ap > MAX_ATR_PCT:
        return "high_vol"
    sec = row.get("sector")
    if sec and sec != "BROAD":
        info = sector_regimes.get(sec) or {}
        if info.get("regime") == "Bear":
            return "sector_bear"
    # Any required factor NaN → can't score
    for f in FACTOR_WEIGHTS:
        if pd.isna(row.get(f)):
            return f"missing_factor:{f}"
    return None


def _zscore_clip(series: pd.Series) -> pd.Series:
    """Z-score over non-NaN values, clipped to [-ZSCORE_CLIP, ZSCORE_CLIP].

    If std == 0 (all equal), returns 0s. Preserves NaN positions.
    """
    s = series.astype(float)
    mu = s.mean(skipna=True)
    sd = s.std(skipna=True, ddof=0)
    if not np.isfinite(sd) or sd == 0:
        return pd.Series(0.0, index=s.index)
    z = (s - mu) / sd
    return z.clip(lower=-ZSCORE_CLIP, upper=ZSCORE_CLIP)


def rank_universe(
    symbols: list[str] | None = None,
    sector_regimes: dict[str, dict] | None = None,
    bars: dict[str, pd.DataFrame] | None = None,
    exclude: set[str] | None = None,
    macro_event: bool = False,
    catalyst_signals: pd.DataFrame | None = None,
    enable_catalyst_fetch: bool = False,
) -> list[dict]:
    """Multi-factor rank of the trading universe.

    Returns sorted-descending list of:
      {symbol, ml_score, factor_breakdown: {factor: z-clipped}, drop_reason}

    drop_reason is None for survivors, set for excluded tickers. Excluded
    tickers are kept in the output (at the tail with ml_score=NaN) for
    diagnostic visibility — callers should filter on drop_reason.

    macro_event=True engages MACRO_DAY_FACTOR_WEIGHTS — a defensive weighting
    profile for binary release days (FOMC/CPI/Core PCE/NFP within 24h). It
    triples the vol_stability weight (0.05 → 0.20) and shaves momentum.
    """
    symbols = sorted(symbols or TRADING_UNIVERSE)
    exclude = exclude or set()
    if bars is None:
        bars = fetch_universe_bars(symbols)
    if sector_regimes is None:
        sector_regimes = rg.sector_regimes()["sectors"]
    if catalyst_signals is None and enable_catalyst_fetch:
        # Parallel Finnhub fetch — no-op if FINNHUB_KEY absent. Limited to symbols
        # that actually have bars (so we don't waste Finnhub quota on dropped names).
        try:
            catalyst_signals = compute_catalyst_signals(list(bars.keys()))
        except Exception as e:
            print(f"[screener] catalyst fetch failed: {e}", file=sys.stderr)
            catalyst_signals = None

    factors = compute_factors(bars, catalyst_signals=catalyst_signals)
    if factors.empty:
        return []

    # Apply gates per-row
    reasons = factors.apply(lambda r: _drop_reason(r, sector_regimes), axis=1)
    survivors_mask = reasons.isna() & ~factors.index.isin(exclude)

    # Z-score each factor over survivors only
    survivors = factors[survivors_mask]
    weights = MACRO_DAY_FACTOR_WEIGHTS if macro_event else FACTOR_WEIGHTS
    z_cols: dict[str, pd.Series] = {}
    for f in weights:
        z_cols[f] = _zscore_clip(survivors[f])
    z_df = pd.DataFrame(z_cols, index=survivors.index)

    # Weighted sum → ml_score
    ml_scores = pd.Series(0.0, index=z_df.index)
    for f, w in weights.items():
        ml_scores = ml_scores + (z_df[f] * w)

    out: list[dict] = []
    # Survivors first, sorted by ml_score desc
    for sym in ml_scores.sort_values(ascending=False).index:
        out.append({
            "symbol": sym,
            "ml_score": round(float(ml_scores[sym]), 4),
            "factor_breakdown": {f: round(float(z_df.at[sym, f]), 3) for f in weights},
            "drop_reason": None,
            "sector": factors.at[sym, "sector"],
            "price": round(float(factors.at[sym, "price"]), 2) if pd.notna(factors.at[sym, "price"]) else None,
            "atr_pct": round(float(factors.at[sym, "atr_pct"]), 3) if pd.notna(factors.at[sym, "atr_pct"]) else None,
        })
    # Drops at the tail with reasons
    for sym in factors.index:
        if sym in ml_scores.index or sym in exclude:
            continue
        reason = reasons.get(sym)
        out.append({
            "symbol": sym,
            "ml_score": None,
            "factor_breakdown": {},
            "drop_reason": str(reason) if reason else "excluded",
            "sector": factors.at[sym, "sector"],
            "price": round(float(factors.at[sym, "price"]), 2) if pd.notna(factors.at[sym, "price"]) else None,
            "atr_pct": round(float(factors.at[sym, "atr_pct"]), 3) if pd.notna(factors.at[sym, "atr_pct"]) else None,
        })

    return out


# ========================================================================
# Shortlist (runtime filtering for deep-dive)
# ========================================================================

def _pairwise_corr_30d(
    sym_a: str,
    sym_b: str,
    bars: dict[str, pd.DataFrame],
    lookback: int = 30,
) -> float:
    """Pearson correlation of daily returns over the trailing lookback days."""
    da = bars.get(sym_a)
    db = bars.get(sym_b)
    if da is None or db is None or len(da) < lookback + 1 or len(db) < lookback + 1:
        return 0.0
    ra = da["Close"].astype(float).pct_change().dropna().tail(lookback)
    rb = db["Close"].astype(float).pct_change().dropna().tail(lookback)
    aligned = pd.concat([ra, rb], axis=1, join="inner")
    if len(aligned) < 10:
        return 0.0
    c = aligned.iloc[:, 0].corr(aligned.iloc[:, 1])
    return 0.0 if pd.isna(c) else abs(float(c))


def deep_dive_shortlist(
    ranked: list[dict],
    open_symbols: set[str],
    bars: dict[str, pd.DataFrame],
    trade_slots: int,
    k: int = 6,
    sector_cap: int = 2,
    corr_cap: float = 0.70,
) -> list[str]:
    """Top-K survivors after runtime filters.

    Filters (in order):
      1. drop_reason is None  (sanity-gated survivor)
      2. not already in open_symbols
      3. sector cap: <= sector_cap existing positions in same sector
      4. max correlation <= corr_cap with each already-picked candidate

    K is bounded: K = min(k, max(trade_slots * 2, 2)).
    BROAD ETFs are exempt from the sector cap.
    """
    if trade_slots <= 0:
        return []
    k_eff = min(k, max(trade_slots * 2, 2))

    # Count existing sector exposure
    sector_counts: dict[str, int] = {}
    for sym in open_symbols:
        sec = sector_of(sym)
        if sec and sec != "BROAD":
            sector_counts[sec] = sector_counts.get(sec, 0) + 1

    picks: list[str] = []
    for entry in ranked:
        if len(picks) >= k_eff:
            break
        if entry["drop_reason"] is not None:
            continue
        sym = entry["symbol"]
        if sym in open_symbols:
            continue
        sec = entry.get("sector")
        if sec and sec != "BROAD":
            if sector_counts.get(sec, 0) >= sector_cap:
                continue
        # Correlation filter against already-picked candidates
        too_correlated = False
        for picked in picks:
            if _pairwise_corr_30d(sym, picked, bars) > corr_cap:
                too_correlated = True
                break
        if too_correlated:
            continue
        picks.append(sym)
        if sec and sec != "BROAD":
            sector_counts[sec] = sector_counts.get(sec, 0) + 1

    return picks


# ========================================================================
# CLI helpers
# ========================================================================

def _fetch_open_positions_from_alpaca() -> set[str]:
    """Best-effort: call alpaca.sh positions and extract symbols.

    Returns empty set on any error — the screener should never crash
    pre-market because Alpaca is unreachable.
    """
    root = _HERE.parent
    try:
        result = subprocess.run(
            ["bash", str(root / "scripts" / "alpaca.sh"), "positions"],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode != 0:
            return set()
        payload = json.loads(result.stdout or "[]")
        if isinstance(payload, list):
            return {p.get("symbol", "").upper() for p in payload if isinstance(p, dict)}
    except Exception:
        pass
    return set()


def main() -> int:
    ap = argparse.ArgumentParser(prog="screener", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_rank = sub.add_parser("rank", help="Full ranking with diagnostics")
    p_rank.add_argument("--top", type=int, default=None, help="Truncate to top N")
    p_rank.add_argument("--json-ml-shape", action="store_true",
                        help="Output universe_ranking list shape only")
    p_rank.add_argument("--no-sector-check", action="store_true",
                        help="Skip Bear-sector filter (testing)")
    p_rank.add_argument("--macro-day", action="store_true",
                        help="Use MACRO_DAY_FACTOR_WEIGHTS (defensive tilt for FOMC/CPI/PCE/NFP days)")
    p_rank.add_argument("--no-catalyst", action="store_true",
                        help="Skip Finnhub catalyst fetch (faster, no FINNHUB_KEY needed)")

    p_short = sub.add_parser("shortlist", help="Top-K deep-dive shortlist")
    p_short.add_argument("--slots", type=int, required=True,
                         help="trade_slots from regime (1, 2, or 3)")
    p_short.add_argument("--k", type=int, default=6, help="Max shortlist size")
    p_short.add_argument("--open", type=str, default="",
                         help="Comma-separated symbols to treat as open positions")
    p_short.add_argument("--macro-day", action="store_true",
                         help="Use defensive weights for ranking (passed to rank_universe)")
    p_short.add_argument("--no-catalyst", action="store_true",
                         help="Skip Finnhub catalyst fetch")

    p_explain = sub.add_parser("explain", help="Per-factor breakdown for one ticker")
    p_explain.add_argument("symbol", type=str)

    args = ap.parse_args()

    if args.cmd == "rank":
        sector_regimes = {} if args.no_sector_check else None
        ranked = rank_universe(
            sector_regimes=sector_regimes,
            macro_event=args.macro_day,
            enable_catalyst_fetch=not args.no_catalyst,
        )
        if args.json_ml_shape:
            survivors = [r for r in ranked if r["drop_reason"] is None]
            out = [{"symbol": r["symbol"], "ml_score": r["ml_score"]} for r in survivors]
            print(json.dumps(out, indent=2))
        else:
            survivors = [r for r in ranked if r["drop_reason"] is None]
            dropped = [r for r in ranked if r["drop_reason"] is not None]
            payload = {
                "as_of": date.today().isoformat(),
                "universe_size": len(ranked),
                "survivors": len(survivors),
                "dropped": len(dropped),
                "factor_weights": FACTOR_WEIGHTS,
                "ranking": survivors[: args.top] if args.top else survivors,
                "dropped_detail": [
                    {"symbol": r["symbol"], "drop_reason": r["drop_reason"],
                     "sector": r["sector"], "price": r["price"]}
                    for r in dropped
                ],
            }
            print(json.dumps(payload, indent=2, default=str))
        return 0

    if args.cmd == "shortlist":
        bars = fetch_universe_bars(sorted(TRADING_UNIVERSE))
        sector_regimes = rg.sector_regimes()["sectors"]
        ranked = rank_universe(
            bars=bars, sector_regimes=sector_regimes,
            macro_event=args.macro_day,
            enable_catalyst_fetch=not args.no_catalyst,
        )
        if args.open:
            open_syms = {s.strip().upper() for s in args.open.split(",") if s.strip()}
        else:
            open_syms = _fetch_open_positions_from_alpaca()
        picks = deep_dive_shortlist(
            ranked=ranked, open_symbols=open_syms, bars=bars,
            trade_slots=args.slots, k=args.k,
        )
        payload = {
            "as_of": date.today().isoformat(),
            "trade_slots": args.slots,
            "open_positions": sorted(open_syms),
            "shortlist": picks,
            "shortlist_size": len(picks),
            "top_10_ranked": [
                {"symbol": r["symbol"], "ml_score": r["ml_score"], "sector": r["sector"]}
                for r in ranked if r["drop_reason"] is None
            ][:10],
        }
        print(json.dumps(payload, indent=2, default=str))
        return 0

    if args.cmd == "explain":
        sym = args.symbol.strip().upper()
        ranked = rank_universe()
        match = next((r for r in ranked if r["symbol"] == sym), None)
        if match is None:
            print(json.dumps({"error": f"{sym} not in universe ranking"}, indent=2))
            return 1
        print(json.dumps(match, indent=2, default=str))
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
