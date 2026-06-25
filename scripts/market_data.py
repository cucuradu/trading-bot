#!/usr/bin/env python3
"""Free market data backup via yfinance.
Usage:
  python scripts/market_data.py quote SYM
  python scripts/market_data.py news SYM
  python scripts/market_data.py sector-momentum
  python scripts/market_data.py atr SYM [period=14]
  python scripts/market_data.py correlation SYM1 SYM2 [SYM3 ...]
  python scripts/market_data.py earnings SYM
"""
import json
import sys
from datetime import date, datetime

import numpy as np
import pandas as pd
import yfinance as yf

import _yf_session_patch  # noqa: F401  (must run before any yf.Ticker call)


SECTOR_ETFS = {
    "Technology": "XLK",
    "Financials": "XLF",
    "Healthcare": "XLV",
    "Energy": "XLE",
    "Consumer Discretionary": "XLY",
    "Consumer Staples": "XLP",
    "Industrials": "XLI",
    "Materials": "XLB",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Communication Services": "XLC",
}


def quote(symbol: str) -> dict:
    info = yf.Ticker(symbol).fast_info

    def _get(key):
        try:
            v = info[key]
        except (KeyError, AttributeError, IndexError):
            return None
        return v

    last_price = _get("lastPrice")
    prev_close = _get("previousClose")
    day_high = _get("dayHigh")
    day_low = _get("dayLow")
    ten_day_vol = _get("tenDayAverageVolume")
    year_high = _get("yearHigh")
    year_low = _get("yearLow")

    return {
        "symbol": symbol.upper(),
        "last_price": float(last_price) if last_price else None,
        "previous_close": float(prev_close) if prev_close else None,
        "day_high": float(day_high) if day_high else None,
        "day_low": float(day_low) if day_low else None,
        "ten_day_avg_volume": int(ten_day_vol) if ten_day_vol else None,
        "year_high": float(year_high) if year_high else None,
        "year_low": float(year_low) if year_low else None,
    }


def news(symbol: str, limit: int = 5) -> list:
    t = yf.Ticker(symbol)
    items = t.news or []
    out = []
    for item in items[:limit]:
        content = item.get("content", item)
        out.append({
            "title": content.get("title"),
            "publisher": (content.get("provider") or {}).get("displayName") or content.get("publisher"),
            "link": (content.get("canonicalUrl") or {}).get("url") or content.get("link"),
            "published": content.get("pubDate") or content.get("providerPublishTime"),
        })
    return out


def compute_atr(history: pd.DataFrame, period: int = 14) -> dict:
    """Pure ATR calculation from an OHLC DataFrame (no network).

    `history` must have columns High, Low, Close and at least `period + 1` rows.
    Returns the same dict shape as `atr()` minus the network-derived as_of date,
    which the caller adds.
    """
    if history.empty or len(history) < period + 1:
        raise ValueError(f"insufficient history for ATR({period}): need {period + 1}, got {len(history)}")

    high = history["High"].astype(float)
    low = history["Low"].astype(float)
    close = history["Close"].astype(float)
    prev_close = close.shift(1)

    tr = pd.concat(
        [(high - low), (high - prev_close).abs(), (low - prev_close).abs()],
        axis=1,
    ).max(axis=1)
    tr = tr.iloc[1:]  # drop first NaN row

    # Wilder's smoothing: RMA = exponential with alpha = 1/period
    atr_series = tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
    atr_val = float(atr_series.iloc[-1])
    last_close = float(close.iloc[-1])
    atr_pct = (atr_val / last_close) * 100 if last_close > 0 else 0.0

    return {
        "period": period,
        "atr": round(atr_val, 4),
        "last_close": round(last_close, 2),
        "atr_pct_of_price": round(atr_pct, 3),
        "stop_pct_2_5x": round(atr_pct * 2.5, 3),
        "stop_pct_1_75x": round(atr_pct * 1.75, 3),
        "stop_pct_1_25x": round(atr_pct * 1.25, 3),
    }


def atr(symbol: str, period: int = 14) -> dict:
    """14-day Average True Range using Wilder's smoothing.

    Returns:
      {
        "symbol": "AAPL",
        "period": 14,
        "atr": 4.21,                # in dollars
        "last_close": 182.50,
        "atr_pct_of_price": 2.31,   # ATR / close * 100
        "stop_pct_2_5x": 5.77,      # widths the strategy uses
        "stop_pct_1_75x": 4.04,
        "stop_pct_1_25x": 2.89,
        "as_of": "2026-05-23",
      }
    """
    # Pull ~3x the period so Wilder's seed has room to converge.
    hist = yf.Ticker(symbol).history(period=f"{max(period * 3, 60)}d", auto_adjust=False)
    result = compute_atr(hist, period)
    result["symbol"] = symbol.upper()
    result["as_of"] = hist.index[-1].strftime("%Y-%m-%d")
    return result


def stop_pct_for_entry(symbol: str, period: int = 14) -> dict:
    """Compute the strategy-recommended initial stop width for an entry.

    Applies the floor (7%) and cap (15%) defined in TRADING-STRATEGY.md.
    """
    a = atr(symbol, period)
    raw = a["stop_pct_2_5x"]
    clamped = max(7.0, min(15.0, raw))
    return {
        "symbol": a["symbol"],
        "atr": a["atr"],
        "last_close": a["last_close"],
        "raw_2_5x_atr_pct": raw,
        "stop_pct": round(clamped, 2),
        "stop_price": round(a["last_close"] * (1 - clamped / 100), 2),
        "clamped": raw != clamped,
        "as_of": a["as_of"],
    }


def compute_correlation(closes_df: pd.DataFrame, lookback_days: int = 30) -> dict:
    """Pure correlation calculation from a DataFrame of close prices (no network).

    `closes_df` is keyed by symbol with a DatetimeIndex. Drops rows with NaNs.
    Caller adds symbols + as_of.
    """
    df = closes_df.dropna()
    if len(df) < lookback_days + 1:
        raise ValueError(
            f"insufficient overlapping history for correlation: "
            f"got {len(df)} rows, need {lookback_days + 1}"
        )

    returns = df.pct_change().iloc[1:].tail(lookback_days)
    corr = returns.corr()

    arr = corr.to_numpy().copy()
    np.fill_diagonal(arr, -np.inf)
    flat_idx = int(np.argmax(arr))
    i, j = divmod(flat_idx, arr.shape[1])
    max_pair = [str(corr.index[i]), str(corr.columns[j])]
    max_val = float(corr.iat[i, j])

    matrix = {
        str(row): {str(col): round(float(corr.at[row, col]), 4) for col in corr.columns}
        for row in corr.index
    }

    return {
        "lookback_days": lookback_days,
        "matrix": matrix,
        "max_off_diagonal": round(max_val, 4),
        "max_pair": max_pair,
    }


def correlation(symbols: list[str], lookback_days: int = 30) -> dict:
    """30-day daily-return correlation matrix for the given symbols.

    Returns:
      {
        "symbols": ["AAPL", "MSFT", "NVDA"],
        "lookback_days": 30,
        "matrix": {"AAPL": {"AAPL": 1.0, "MSFT": 0.72, ...}, ...},
        "max_off_diagonal": 0.81,
        "max_pair": ["MSFT", "NVDA"],
        "as_of": "2026-05-23",
      }
    """
    if len(symbols) < 2:
        raise ValueError("correlation requires at least 2 symbols")

    uniq = sorted({s.strip().upper() for s in symbols})
    # Need ~lookback_days + buffer of trading days; pull 90d to be safe across weekends.
    data = yf.download(
        uniq,
        period=f"{max(lookback_days * 3, 90)}d",
        auto_adjust=False,
        progress=False,
        group_by="ticker",
    )
    # Extract Close column for each symbol — yf.download has different shapes
    # for 1 symbol vs many; normalize to a DataFrame keyed by symbol.
    closes: dict[str, pd.Series] = {}
    if isinstance(data.columns, pd.MultiIndex):
        for sym in uniq:
            if sym in data.columns.get_level_values(0):
                closes[sym] = data[sym]["Close"].astype(float)
    else:
        closes[uniq[0]] = data["Close"].astype(float)

    df = pd.DataFrame(closes)
    result = compute_correlation(df, lookback_days)
    result["symbols"] = uniq
    result["as_of"] = df.dropna().index[-1].strftime("%Y-%m-%d")
    return result


def max_correlation_with_existing(candidate: str, existing: list[str], lookback_days: int = 30) -> dict:
    """How correlated is `candidate` with the most-correlated of `existing`?

    Used by the buy-gate to enforce the 0.70 cap (Phase A3).
    """
    if not existing:
        return {
            "candidate": candidate.upper(),
            "existing": [],
            "max_correlation": None,
            "max_pair_with": None,
            "as_of": None,
        }
    all_syms = [candidate.upper(), *[s.upper() for s in existing]]
    full = correlation(all_syms, lookback_days)
    row = full["matrix"][candidate.upper()]
    # Strip self-correlation
    pairs = {k: v for k, v in row.items() if k != candidate.upper()}
    best_sym = max(pairs, key=lambda k: pairs[k])
    return {
        "candidate": candidate.upper(),
        "existing": sorted([s.upper() for s in existing]),
        "max_correlation": pairs[best_sym],
        "max_pair_with": best_sym,
        "as_of": full["as_of"],
    }


def _coerce_date(val) -> date | None:
    if val is None:
        return None
    if isinstance(val, date) and not isinstance(val, datetime):
        return val
    if isinstance(val, datetime):
        return val.date()
    if isinstance(val, pd.Timestamp):
        return val.date()
    if isinstance(val, str):
        try:
            return datetime.fromisoformat(val.split()[0]).date()
        except ValueError:
            return None
    return None


def earnings(symbol: str) -> dict:
    """Days until next earnings announcement (calendar days, not trading days).

    Returns:
      {
        "symbol": "AAPL",
        "next_earnings_date": "2026-07-30",
        "days_until": 68,
        "in_blackout": false,           # < 5 days
        "blackout_window_days": 5,
        "source": "calendar|earnings_dates|unknown"
      }
    `days_until` is None if no upcoming earnings date is available.
    """
    t = yf.Ticker(symbol)
    today = date.today()
    next_date: date | None = None
    source = "unknown"

    # Preferred: ticker.calendar (recent yfinance)
    try:
        cal = t.calendar
        if isinstance(cal, dict):
            raw = cal.get("Earnings Date") or cal.get("earningsDate")
            if isinstance(raw, list) and raw:
                next_date = _coerce_date(raw[0])
            else:
                next_date = _coerce_date(raw)
            source = "calendar"
        elif isinstance(cal, pd.DataFrame) and not cal.empty:
            raw = cal.iloc[0].get("Earnings Date")
            next_date = _coerce_date(raw)
            source = "calendar"
    except Exception:
        next_date = None

    # Fallback: earnings_dates table (covers more tickers)
    if next_date is None:
        try:
            df = t.get_earnings_dates(limit=8)
            if df is not None and not df.empty:
                future = [_coerce_date(idx) for idx in df.index]
                future = [d for d in future if d and d >= today]
                if future:
                    next_date = min(future)
                    source = "earnings_dates"
        except Exception:
            pass

    if next_date is None:
        return {
            "symbol": symbol.upper(),
            "next_earnings_date": None,
            "days_until": None,
            "in_blackout": False,
            "blackout_window_days": 5,
            "source": source,
        }

    days_until = (next_date - today).days
    return {
        "symbol": symbol.upper(),
        "next_earnings_date": next_date.isoformat(),
        "days_until": days_until,
        "in_blackout": 0 <= days_until < 5,
        "blackout_window_days": 5,
        "source": source,
    }


def sector_momentum() -> list:
    rows = []
    for sector, etf in SECTOR_ETFS.items():
        hist = yf.Ticker(etf).history(period="1mo", auto_adjust=False)
        if hist.empty:
            continue
        first, last = hist["Close"].iloc[0], hist["Close"].iloc[-1]
        rows.append({
            "sector": sector,
            "etf": etf,
            "month_return_pct": round((last / first - 1) * 100, 2),
            "last_close": round(float(last), 2),
        })
    rows.sort(key=lambda r: r["month_return_pct"], reverse=True)
    return rows


def _wilder(series: pd.Series, period: int) -> pd.Series:
    """Wilder's smoothing == EMA with alpha = 1/period."""
    return series.ewm(alpha=1 / period, adjust=False).mean()


def technicals(symbol: str) -> dict:
    """Local price technicals from yfinance OHLCV — RSI / MACD / SMA50-200 /
    ADX / 52-week range / volume. Deterministic, no API quota: replaces asking
    an LLM "what do the technicals say". Pulls ~1y so the 200-SMA and 52w range
    are well defined.
    """
    hist = yf.Ticker(symbol).history(period="1y", auto_adjust=False)
    if hist.empty or len(hist) < 30:
        raise ValueError(f"insufficient history for technicals: got {len(hist)} rows")
    close = hist["Close"].astype(float)
    high = hist["High"].astype(float)
    low = hist["Low"].astype(float)
    vol = hist["Volume"].astype(float)
    last = float(close.iloc[-1])
    last_vol = float(vol.iloc[-1])

    sma50 = float(close.rolling(50).mean().iloc[-1]) if len(close) >= 50 else None
    sma200 = float(close.rolling(200).mean().iloc[-1]) if len(close) >= 200 else None

    # RSI(14), Wilder
    delta = close.diff()
    rs = _wilder(delta.clip(lower=0), 14) / _wilder(-delta.clip(upper=0), 14).replace(0, float("nan"))
    rsi_last = rs.iloc[-1]
    rsi14 = float(100 - 100 / (1 + rsi_last)) if rsi_last == rsi_last else None

    # MACD (12, 26, 9)
    macd_line = close.ewm(span=12, adjust=False).mean() - close.ewm(span=26, adjust=False).mean()
    macd_hist = float(macd_line.iloc[-1] - macd_line.ewm(span=9, adjust=False).mean().iloc[-1])

    # ADX(14), Wilder
    up, down = high.diff(), -low.diff()
    plus_dm = ((up > down) & (up > 0)) * up
    minus_dm = ((down > up) & (down > 0)) * down
    tr = pd.concat([(high - low), (high - close.shift()).abs(), (low - close.shift()).abs()], axis=1).max(axis=1)
    atr_w = _wilder(tr, 14).replace(0, float("nan"))
    plus_di = 100 * _wilder(plus_dm, 14) / atr_w
    minus_di = 100 * _wilder(minus_dm, 14) / atr_w
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di).replace(0, float("nan"))
    adx_series = _wilder(dx, 14).dropna()
    adx14 = float(adx_series.iloc[-1]) if len(adx_series) else None

    hi_52, lo_52 = float(high.tail(252).max()), float(low.tail(252).min())
    vol20 = float(vol.tail(20).mean())

    def pct(a, b):
        return round((a / b - 1) * 100, 2) if b else None

    return {
        "symbol": symbol.upper(),
        "as_of": hist.index[-1].strftime("%Y-%m-%d"),
        "price": round(last, 2),
        "sma50": round(sma50, 2) if sma50 else None,
        "sma200": round(sma200, 2) if sma200 else None,
        "dist_sma50_pct": pct(last, sma50),
        "dist_sma200_pct": pct(last, sma200),
        "above_200sma": (last > sma200) if sma200 else None,
        "rsi14": round(rsi14, 1) if rsi14 is not None else None,
        "macd_hist": round(macd_hist, 3),
        "macd_bias": "bullish" if macd_hist > 0 else "bearish",
        "adx14": round(adx14, 1) if adx14 is not None else None,
        "trend_strength": (("strong" if adx14 >= 25 else "weak/none") if adx14 is not None else None),
        "high_52w": round(hi_52, 2),
        "low_52w": round(lo_52, 2),
        "dist_52w_high_pct": pct(last, hi_52),
        "dist_52w_low_pct": pct(last, lo_52),
        "vol_vs_20d_avg": round(last_vol / vol20, 2) if vol20 else None,
    }


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    cmd = sys.argv[1]
    if cmd == "quote":
        sym = sys.argv[2]
        print(json.dumps(quote(sym), indent=2))
    elif cmd == "news":
        sym = sys.argv[2]
        print(json.dumps(news(sym), indent=2))
    elif cmd == "sector-momentum":
        print(json.dumps(sector_momentum(), indent=2))
    elif cmd == "atr":
        sym = sys.argv[2]
        period = int(sys.argv[3]) if len(sys.argv) >= 4 else 14
        print(json.dumps(atr(sym, period), indent=2))
    elif cmd == "stop-for-entry":
        sym = sys.argv[2]
        period = int(sys.argv[3]) if len(sys.argv) >= 4 else 14
        print(json.dumps(stop_pct_for_entry(sym, period), indent=2))
    elif cmd == "correlation":
        if len(sys.argv) < 4:
            print("usage: correlation SYM1 SYM2 [SYM3 ...]", file=sys.stderr)
            return 2
        print(json.dumps(correlation(sys.argv[2:]), indent=2))
    elif cmd == "max-correlation-with":
        # max-correlation-with CANDIDATE EXISTING1 [EXISTING2 ...]
        if len(sys.argv) < 4:
            print("usage: max-correlation-with CANDIDATE EXISTING1 [EXISTING2 ...]", file=sys.stderr)
            return 2
        print(json.dumps(max_correlation_with_existing(sys.argv[2], sys.argv[3:]), indent=2))
    elif cmd == "earnings":
        sym = sys.argv[2]
        print(json.dumps(earnings(sym), indent=2))
    elif cmd == "technicals":
        sym = sys.argv[2]
        print(json.dumps(technicals(sym), indent=2))
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
