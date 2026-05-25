#!/usr/bin/env python3
"""Hardcoded trading universe — the ONLY tickers this bot may research or trade.

Universe changes are strategy changes: edit this file in a dedicated commit with
rationale in the commit body. Do not pass tickers in as CLI args or env vars.

Usage:
  python scripts/universe.py list           # print all symbols, one per line
  python scripts/universe.py is_member SYM  # exit 0 if member, 1 if not
  python scripts/universe.py json           # print as JSON list
  python scripts/universe.py sector SYM     # print sector ETF (XLK/XLF/...) or BROAD
"""
from __future__ import annotations

import json
import sys


SECTOR_ETFS: frozenset[str] = frozenset({
    "XLK", "XLF", "XLV", "XLE", "XLY", "XLP", "XLI", "XLU", "XLB", "XLRE", "XLC",
})

BROAD_ETFS: frozenset[str] = frozenset({
    "SPY", "QQQ", "IWM", "DIA",
})

MEGA_CAP_TECH: frozenset[str] = frozenset({
    "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "AVGO", "TSLA",
})

MEGA_CAP_CONSUMER_FINANCE: frozenset[str] = frozenset({
    "JPM", "V", "MA", "COST", "WMT", "HD", "PG", "KO",
})

MEGA_CAP_HEALTH_INDUSTRIAL: frozenset[str] = frozenset({
    "UNH", "JNJ", "LLY", "CAT", "BA",
})

MEGA_CAP_ENERGY_COMMS: frozenset[str] = frozenset({
    "XOM", "CVX", "NFLX", "DIS",
})

TRADING_UNIVERSE: frozenset[str] = (
    SECTOR_ETFS
    | BROAD_ETFS
    | MEGA_CAP_TECH
    | MEGA_CAP_CONSUMER_FINANCE
    | MEGA_CAP_HEALTH_INDUSTRIAL
    | MEGA_CAP_ENERGY_COMMS
)


# Symbol -> sector ETF mapping. Follows SPDR Select Sector classifications:
#   - AAPL/MSFT/NVDA/AVGO -> XLK (Information Technology)
#   - GOOGL/META/NFLX/DIS -> XLC (Communication Services)
#   - AMZN/TSLA/HD        -> XLY (Consumer Discretionary)
#   - WMT/COST/PG/KO      -> XLP (Consumer Staples)
#   - JPM/V/MA            -> XLF (Financials)
#   - UNH/JNJ/LLY         -> XLV (Health Care)
#   - CAT/BA              -> XLI (Industrials)
#   - XOM/CVX             -> XLE (Energy)
# Broad ETFs (SPY/QQQ/IWM/DIA) and sector ETFs themselves map to None / themselves.
SECTOR_OF: dict[str, str] = {
    # Tech
    "AAPL": "XLK", "MSFT": "XLK", "NVDA": "XLK", "AVGO": "XLK",
    # Communication services
    "GOOGL": "XLC", "META": "XLC", "NFLX": "XLC", "DIS": "XLC",
    # Consumer discretionary
    "AMZN": "XLY", "TSLA": "XLY", "HD": "XLY",
    # Consumer staples
    "WMT": "XLP", "COST": "XLP", "PG": "XLP", "KO": "XLP",
    # Financials
    "JPM": "XLF", "V": "XLF", "MA": "XLF",
    # Health care
    "UNH": "XLV", "JNJ": "XLV", "LLY": "XLV",
    # Industrials
    "CAT": "XLI", "BA": "XLI",
    # Energy
    "XOM": "XLE", "CVX": "XLE",
    # Sector ETFs map to themselves (useful for attribution when trading the ETF directly)
    "XLK": "XLK", "XLF": "XLF", "XLV": "XLV", "XLE": "XLE", "XLY": "XLY",
    "XLP": "XLP", "XLI": "XLI", "XLU": "XLU", "XLB": "XLB", "XLRE": "XLRE", "XLC": "XLC",
    # Broad ETFs intentionally have no sector — they're cross-sector index plays.
    "SPY": "BROAD", "QQQ": "BROAD", "IWM": "BROAD", "DIA": "BROAD",
}


def is_member(symbol: str) -> bool:
    return symbol.strip().upper() in TRADING_UNIVERSE


def sector_of(symbol: str) -> str | None:
    """Return the SPDR sector ETF for a universe ticker, or None if unknown.

    Broad ETFs (SPY/QQQ/IWM/DIA) return the string "BROAD" — they belong to no
    single sector and should be excluded from sector-attribution math.
    """
    return SECTOR_OF.get(symbol.strip().upper())


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    cmd = sys.argv[1]
    if cmd == "list":
        for sym in sorted(TRADING_UNIVERSE):
            print(sym)
    elif cmd == "json":
        print(json.dumps(sorted(TRADING_UNIVERSE)))
    elif cmd == "is_member":
        if len(sys.argv) < 3:
            print("usage: is_member SYM", file=sys.stderr)
            return 2
        return 0 if is_member(sys.argv[2]) else 1
    elif cmd == "sector":
        if len(sys.argv) < 3:
            print("usage: sector SYM", file=sys.stderr)
            return 2
        sec = sector_of(sys.argv[2])
        if sec is None:
            print(f"unknown: {sys.argv[2]}", file=sys.stderr)
            return 1
        print(sec)
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
