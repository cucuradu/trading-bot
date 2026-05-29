"""Tests for the carry-forward watchlist (Phase G2)."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import watchlist as wl  # noqa: E402


@pytest.fixture
def wl_path(tmp_path):
    return tmp_path / "WATCHLIST.md"


def test_add_creates_file_and_persists_entry(wl_path):
    e = wl.add_entry(
        "NVDA",
        setup="PULLBACK",
        entry=138.50,
        initial_stop=125.00,
        thesis="AI capex",
        today=date(2026, 5, 29),
        path=wl_path,
    )
    assert e.symbol == "NVDA"
    assert e.setup == "PULLBACK"
    assert e.days_remaining == wl.DEFAULT_DAYS
    listed = wl.load(wl_path)
    assert len(listed) == 1
    assert listed[0].planned_entry == 138.50


def test_add_rejects_unknown_setup(wl_path):
    with pytest.raises(ValueError, match="setup"):
        wl.add_entry("NVDA", setup="OPTIONS", entry=138.50, initial_stop=125.0,
                     path=wl_path)


def test_add_refreshes_existing_ticker(wl_path):
    """A re-add of the same symbol must replace, not duplicate."""
    wl.add_entry("NVDA", setup="PULLBACK", entry=138.50, initial_stop=125.0,
                 today=date(2026, 5, 29), path=wl_path)
    # Decrement happens in a different call (prune); re-add resets days_remaining
    wl.add_entry("NVDA", setup="PULLBACK", entry=141.00, initial_stop=128.0,
                 today=date(2026, 5, 30), path=wl_path)
    entries = wl.load(wl_path)
    assert len(entries) == 1
    assert entries[0].planned_entry == 141.00
    assert entries[0].initial_stop == 128.00
    assert entries[0].days_remaining == wl.DEFAULT_DAYS


def test_max_entries_cap_drops_lowest_days_remaining(wl_path):
    """The hard cap is 6; once exceeded, the most tired entries leave."""
    for i, sym in enumerate(["AAA", "BBB", "CCC", "DDD", "EEE", "FFF"]):
        wl.add_entry(sym, setup="PULLBACK", entry=100.0 + i, initial_stop=90.0,
                     today=date(2026, 5, 29), path=wl_path)
    # Prune once so different entries get different days_remaining
    wl.prune(wl_path)
    # Now add 2 fresh ones — the cap should drop the most-pruned (lowest days_remaining)
    wl.add_entry("GGG", setup="BREAKOUT", entry=200.0, initial_stop=180.0,
                 today=date(2026, 5, 30), path=wl_path)
    wl.add_entry("HHH", setup="MOMENTUM", entry=300.0, initial_stop=270.0,
                 today=date(2026, 5, 30), path=wl_path)
    entries = wl.load(wl_path)
    assert len(entries) <= wl.MAX_ENTRIES
    # Fresh adds (3 days remaining) should outlast the pruned ones (2 days remaining)
    symbols = {e.symbol for e in entries}
    assert "GGG" in symbols
    assert "HHH" in symbols


def test_prune_decrements_and_drops_expired(wl_path):
    wl.add_entry("AAA", setup="PULLBACK", entry=100.0, initial_stop=90.0,
                 days=1, today=date(2026, 5, 29), path=wl_path)
    wl.add_entry("BBB", setup="BREAKOUT", entry=200.0, initial_stop=180.0,
                 days=3, today=date(2026, 5, 29), path=wl_path)
    res = wl.prune(wl_path)
    assert res["expired"] == ["AAA"]
    assert res["kept"] == ["BBB"]
    remaining = wl.load(wl_path)
    assert len(remaining) == 1
    assert remaining[0].symbol == "BBB"
    assert remaining[0].days_remaining == 2  # decremented from 3


def test_drop_removes_named_ticker(wl_path):
    wl.add_entry("AAA", setup="PULLBACK", entry=100.0, initial_stop=90.0,
                 path=wl_path)
    wl.add_entry("BBB", setup="BREAKOUT", entry=200.0, initial_stop=180.0,
                 path=wl_path)
    assert wl.drop("AAA", wl_path) is True
    assert wl.drop("AAA", wl_path) is False  # second time: nothing to drop
    remaining = {e.symbol for e in wl.load(wl_path)}
    assert remaining == {"BBB"}


def test_round_trip_preserves_thesis_with_special_chars(wl_path):
    thesis = "fed cut path; CPI 2.1% vs 2.4% expected — strong"
    wl.add_entry("XYZ", setup="PULLBACK", entry=100.0, initial_stop=90.0,
                 thesis=thesis, path=wl_path)
    entries = wl.load(wl_path)
    assert entries[0].thesis == thesis


def test_load_returns_empty_when_file_missing(tmp_path):
    assert wl.load(tmp_path / "missing.md") == []


def test_parse_line_rejects_unknown_setup():
    bad = (
        '- 2026-05-29: NVDA setup=OPTIONS entry=138.50 initial_stop=125.00 '
        'days_remaining=3 thesis="bad"'
    )
    assert wl.parse_line(bad) is None


def test_parse_line_rejects_missing_required():
    bad = '- 2026-05-29: NVDA setup=PULLBACK entry=138.50'  # missing stop + days
    assert wl.parse_line(bad) is None
