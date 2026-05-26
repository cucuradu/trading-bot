#!/usr/bin/env python3
"""Trading-calendar helper. Single source of truth for US-market holidays
and weekday/holiday logic — used by routine prompts to avoid asking Gemini
to do date math (which it hallucinates).

Usage:
  python scripts/trading_calendar.py today           # today's date
  python scripts/trading_calendar.py is-trading-day  # 0 if yes, 1 if no
  python scripts/trading_calendar.py next            # next trading day
  python scripts/trading_calendar.py prev            # previous trading day
  python scripts/trading_calendar.py status          # JSON with everything
  python scripts/trading_calendar.py pre-macro-event # JSON: binary macro event within 24h?
"""
from __future__ import annotations

import datetime
import json
import sys


# US stock-market holidays. Extend at the end of each year.
US_HOLIDAYS: set[datetime.date] = {
    # 2026
    datetime.date(2026, 1, 1),    # New Year's Day
    datetime.date(2026, 1, 19),   # MLK Day
    datetime.date(2026, 2, 16),   # Presidents' Day
    datetime.date(2026, 4, 3),    # Good Friday
    datetime.date(2026, 5, 25),   # Memorial Day
    datetime.date(2026, 6, 19),   # Juneteenth
    datetime.date(2026, 7, 3),    # Independence Day (observed)
    datetime.date(2026, 9, 7),    # Labor Day
    datetime.date(2026, 11, 26),  # Thanksgiving
    datetime.date(2026, 12, 25),  # Christmas
    # 2027 (add when known)
}


# Known binary-impact macro events. The bot caps total deployment at 40%
# within 24h of any of these (Phase E rule in TRADING-STRATEGY.md).
# FOMC dates are firm; CPI/PPI/PCE/NFP are approximate release patterns
# (refresh quarterly when BLS/BEA publishes the schedule).
MACRO_EVENTS: dict[datetime.date, str] = {
    # FOMC 2026 (8 scheduled meetings)
    datetime.date(2026, 1, 28):  "FOMC",
    datetime.date(2026, 3, 18):  "FOMC",
    datetime.date(2026, 4, 29):  "FOMC",
    datetime.date(2026, 6, 17):  "FOMC",
    datetime.date(2026, 7, 29):  "FOMC",
    datetime.date(2026, 9, 16):  "FOMC",
    datetime.date(2026, 10, 28): "FOMC",
    datetime.date(2026, 12, 16): "FOMC",
    # Core PCE 2026 (BEA, ~last Friday of the month; approximate)
    datetime.date(2026, 1, 30):  "Core PCE",
    datetime.date(2026, 2, 27):  "Core PCE",
    datetime.date(2026, 3, 27):  "Core PCE",
    datetime.date(2026, 4, 30):  "Core PCE",
    datetime.date(2026, 5, 28):  "Core PCE + GDP Q1 2nd",
    datetime.date(2026, 6, 26):  "Core PCE",
    datetime.date(2026, 7, 31):  "Core PCE",
    datetime.date(2026, 8, 28):  "Core PCE",
    datetime.date(2026, 9, 25):  "Core PCE",
    datetime.date(2026, 10, 30): "Core PCE",
    datetime.date(2026, 11, 25): "Core PCE",
    datetime.date(2026, 12, 23): "Core PCE",
    # CPI 2026 (BLS, ~mid-month; approximate)
    datetime.date(2026, 1, 14):  "CPI",
    datetime.date(2026, 2, 11):  "CPI",
    datetime.date(2026, 3, 11):  "CPI",
    datetime.date(2026, 4, 14):  "CPI",
    datetime.date(2026, 5, 13):  "CPI",
    datetime.date(2026, 6, 11):  "CPI",
    datetime.date(2026, 7, 14):  "CPI",
    datetime.date(2026, 8, 12):  "CPI",
    datetime.date(2026, 9, 11):  "CPI",
    datetime.date(2026, 10, 14): "CPI",
    datetime.date(2026, 11, 12): "CPI",
    datetime.date(2026, 12, 10): "CPI",
    # NFP / jobs (BLS, first Friday; approximate)
    datetime.date(2026, 1, 2):   "NFP",
    datetime.date(2026, 2, 6):   "NFP",
    datetime.date(2026, 3, 6):   "NFP",
    datetime.date(2026, 4, 3):   "NFP",
    datetime.date(2026, 5, 1):   "NFP",
    datetime.date(2026, 6, 5):   "NFP",
    datetime.date(2026, 7, 2):   "NFP",
    datetime.date(2026, 8, 7):   "NFP",
    datetime.date(2026, 9, 4):   "NFP",
    datetime.date(2026, 10, 2):  "NFP",
    datetime.date(2026, 11, 6):  "NFP",
    datetime.date(2026, 12, 4):  "NFP",
}


def is_trading_day(d: datetime.date) -> bool:
    return d.weekday() < 5 and d not in US_HOLIDAYS


def next_trading_day(d: datetime.date | None = None) -> datetime.date:
    d = d or datetime.date.today()
    while True:
        d = d + datetime.timedelta(days=1)
        if is_trading_day(d):
            return d


def prev_trading_day(d: datetime.date | None = None) -> datetime.date:
    d = d or datetime.date.today()
    while True:
        d = d - datetime.timedelta(days=1)
        if is_trading_day(d):
            return d


def pre_macro_event_check(d: datetime.date | None = None) -> dict:
    """Return whether a binary macro event releases within the next 2 trading days.

    Phase E rule: cap deployment at 40% when `cap_active` is True. The 2-day
    horizon catches events the night before (true 24h cap) AND the prep day
    (deploying Monday for a Wed event would be over-extended once the binary
    drops).
    """
    d = d or datetime.date.today()
    horizon: list[datetime.date] = [d]
    cursor = d
    for _ in range(3):  # look ~3 trading days out to cover the prep window
        cursor = next_trading_day(cursor)
        horizon.append(cursor)
    for candidate in horizon:
        if candidate in MACRO_EVENTS:
            days_to = (candidate - d).days
            return {
                "cap_active": days_to <= 2,        # the operative rule (Phase E)
                "within_24h": days_to <= 1,        # tighter window for posture
                "event_name": MACRO_EVENTS[candidate],
                "event_date": candidate.isoformat(),
                "days_to_event": days_to,
            }
    return {
        "cap_active": False,
        "within_24h": False,
        "event_name": None,
        "event_date": None,
        "days_to_event": None,
    }


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    today = datetime.date.today()

    if cmd == "today":
        print(today.strftime("%a %b %d %Y"))
    elif cmd == "today-iso":
        print(today.isoformat())
    elif cmd == "is-trading-day":
        return 0 if is_trading_day(today) else 1
    elif cmd == "next":
        print(next_trading_day(today).strftime("%a %b %d"))
    elif cmd == "next-iso":
        print(next_trading_day(today).isoformat())
    elif cmd == "prev":
        print(prev_trading_day(today).strftime("%a %b %d"))
    elif cmd == "prev-iso":
        print(prev_trading_day(today).isoformat())
    elif cmd == "status":
        out = {
            "today": today.isoformat(),
            "today_human": today.strftime("%a %b %d %Y"),
            "is_trading_day": is_trading_day(today),
            "next_trading_day": next_trading_day(today).isoformat(),
            "next_trading_day_human": next_trading_day(today).strftime("%a %b %d"),
            "prev_trading_day": prev_trading_day(today).isoformat(),
            "prev_trading_day_human": prev_trading_day(today).strftime("%a %b %d"),
            "is_us_holiday": today in US_HOLIDAYS,
            "pre_macro_event": pre_macro_event_check(today),
        }
        print(json.dumps(out, indent=2))
    elif cmd == "pre-macro-event":
        print(json.dumps(pre_macro_event_check(today), indent=2))
    else:
        print(__doc__, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
