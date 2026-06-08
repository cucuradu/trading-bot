#!/usr/bin/env python3
"""Analyst consensus + fundamentals via yfinance — free, no key, no quota.

Replaces the Gemini-grounded / WebSearch path the bot used to fetch price
targets and ratings (which starves whenever Gemini hits its quota). Gives the
buy-gate a real, citeable consensus target for the R:R floor (B3) instead of a
cherry-picked outlier or an unverifiable LLM number.

Pass the LIVE price (from Alpaca) via --price so implied-return / R:R math uses
the real quote — yfinance's own `currentPrice` is delayed/EOD.

Usage:
  python scripts/analyst_data.py targets SYM [--price LIVE]   # JSON
  python scripts/analyst_data.py line    SYM [--price LIVE]   # one-line summary
"""
from __future__ import annotations

import argparse
import json
import sys

import yfinance as yf


def _num(x):
    try:
        f = float(x)
        return f if f == f else None  # drop NaN
    except (TypeError, ValueError):
        return None


def fetch(symbol: str, price: float | None = None) -> dict:
    t = yf.Ticker(symbol)
    info = t.info or {}

    px = price if price is not None else _num(info.get("currentPrice"))
    tgt_mean = _num(info.get("targetMeanPrice"))
    tgt_med = _num(info.get("targetMedianPrice"))
    tgt_high = _num(info.get("targetHighPrice"))
    tgt_low = _num(info.get("targetLowPrice"))

    def implied(target):
        if target is None or not px:
            return None
        return round((target / px - 1) * 100, 1)

    # Rating breakdown (most recent row of the recommendations table).
    counts = {}
    try:
        rec = t.recommendations
        if rec is not None and len(rec):
            row = rec.iloc[0]
            for k in ("strongBuy", "buy", "hold", "sell", "strongSell"):
                if k in row:
                    counts[k] = int(row[k])
    except Exception:
        counts = {}

    return {
        "symbol": symbol.upper(),
        "price_used": round(px, 2) if px else None,
        "price_source": "alpaca_live" if price is not None else "yfinance_delayed",
        "target_mean": tgt_mean,
        "target_median": tgt_med,
        "target_high": tgt_high,
        "target_low": tgt_low,
        "implied_return_mean_pct": implied(tgt_mean),
        "implied_return_median_pct": implied(tgt_med),
        "num_analysts": info.get("numberOfAnalystOpinions"),
        "rating_key": info.get("recommendationKey"),
        "rating_mean": _num(info.get("recommendationMean")),  # 1=Strong Buy .. 5=Sell
        "rating_counts": counts,
        "fundamentals": {
            "trailing_pe": _num(info.get("trailingPE")),
            "forward_pe": _num(info.get("forwardPE")),
            "revenue_growth": _num(info.get("revenueGrowth")),
            "gross_margins": _num(info.get("grossMargins")),
            "profit_margins": _num(info.get("profitMargins")),
            "peg_ratio": _num(info.get("trailingPegRatio")),
        },
    }


def to_line(d: dict) -> str:
    if not d.get("target_mean") and not d.get("num_analysts"):
        return f"{d['symbol']}: no analyst coverage in yfinance"
    parts = [
        f"{d['symbol']} @ ${d['price_used']}",
        f"consensus PT ${d.get('target_median') or d.get('target_mean')} "
        f"(mean ${d.get('target_mean')}, range ${d.get('target_low')}-${d.get('target_high')})",
        f"implied {d.get('implied_return_median_pct')}% (median)",
        f"{d.get('rating_key')} [{d.get('num_analysts')} analysts, mean {d.get('rating_mean')}]",
    ]
    fpe = d["fundamentals"].get("forward_pe")
    if fpe:
        parts.append(f"fwdPE {fpe:.1f}")
    return " | ".join(parts)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="analyst_data.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("targets", "line"):
        sp = sub.add_parser(name)
        sp.add_argument("symbol")
        sp.add_argument("--price", type=float, default=None,
                        help="live price from Alpaca (overrides yfinance delayed quote)")
    args = p.parse_args(argv)

    d = fetch(args.symbol, args.price)
    print(to_line(d) if args.cmd == "line" else json.dumps(d, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
