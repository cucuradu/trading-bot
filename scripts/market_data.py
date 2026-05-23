#!/usr/bin/env python3
"""Free market data backup via yfinance.
Usage:
  python scripts/yfinance.py quote SYM
  python scripts/yfinance.py news SYM
  python scripts/yfinance.py sector-momentum
"""
import json
import sys

import yfinance as yf


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
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
