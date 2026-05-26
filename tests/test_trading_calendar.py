"""Tests for scripts/trading_calendar.py — date math + macro-event detection."""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import trading_calendar as tc  # noqa: E402


def test_memorial_day_2026_is_holiday():
    assert datetime.date(2026, 5, 25) in tc.US_HOLIDAYS
    assert not tc.is_trading_day(datetime.date(2026, 5, 25))


def test_saturday_is_not_trading_day():
    assert not tc.is_trading_day(datetime.date(2026, 5, 23))


def test_next_trading_day_skips_holiday_and_weekend():
    # Fri May 22 → Tue May 26 (Sat/Sun + Memorial Day Mon skipped)
    assert tc.next_trading_day(datetime.date(2026, 5, 22)) == datetime.date(2026, 5, 26)


def test_next_trading_day_simple_weekday():
    # Tue → Wed (no holiday in between)
    assert tc.next_trading_day(datetime.date(2026, 5, 26)) == datetime.date(2026, 5, 27)


def test_prev_trading_day_skips_holiday():
    # Tue May 26 → Fri May 22 (Memorial Day Mon + weekend skipped)
    assert tc.prev_trading_day(datetime.date(2026, 5, 26)) == datetime.date(2026, 5, 22)


def test_pre_macro_event_caps_cap_active_within_2_days():
    # Tue May 26 with Core PCE on Thu May 28 → cap_active=True
    out = tc.pre_macro_event_check(datetime.date(2026, 5, 26))
    assert out["cap_active"] is True
    assert out["event_name"].startswith("Core PCE")
    assert out["event_date"] == "2026-05-28"
    assert out["days_to_event"] == 2


def test_pre_macro_event_within_24h_distinct_from_cap_active():
    # Wed May 27 → PCE Thu = days_to_event=1, within_24h=True
    out = tc.pre_macro_event_check(datetime.date(2026, 5, 27))
    assert out["within_24h"] is True
    assert out["cap_active"] is True
    assert out["days_to_event"] == 1


def test_pre_macro_event_inactive_with_no_event_in_window():
    # Mon Mar 23: FOMC Mar 18 is past; PCE Mar 27 is 4 days out (outside horizon).
    out = tc.pre_macro_event_check(datetime.date(2026, 3, 23))
    assert out["cap_active"] is False
    assert out["event_name"] is None
