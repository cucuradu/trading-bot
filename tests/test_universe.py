"""Tests for scripts/universe.py — membership + sector mapping (Phase A7 + D2)."""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import universe as u  # noqa: E402


def test_universe_has_40_tickers():
    assert len(u.TRADING_UNIVERSE) == 40


def test_membership_is_case_insensitive():
    assert u.is_member("aapl")
    assert u.is_member("AAPL")
    assert u.is_member("  NVDA  ")
    assert not u.is_member("GME")


def test_sector_of_tech_constituents():
    assert u.sector_of("AAPL") == "XLK"
    assert u.sector_of("MSFT") == "XLK"
    assert u.sector_of("NVDA") == "XLK"
    assert u.sector_of("AVGO") == "XLK"


def test_sector_of_communication_services():
    # GOOGL, META, NFLX, DIS belong to XLC per SPDR.
    assert u.sector_of("GOOGL") == "XLC"
    assert u.sector_of("META") == "XLC"
    assert u.sector_of("NFLX") == "XLC"
    assert u.sector_of("DIS") == "XLC"


def test_sector_of_consumer_discretionary():
    assert u.sector_of("AMZN") == "XLY"
    assert u.sector_of("TSLA") == "XLY"
    assert u.sector_of("HD") == "XLY"


def test_sector_of_consumer_staples():
    assert u.sector_of("WMT") == "XLP"
    assert u.sector_of("COST") == "XLP"
    assert u.sector_of("PG") == "XLP"
    assert u.sector_of("KO") == "XLP"


def test_sector_of_financials():
    assert u.sector_of("JPM") == "XLF"
    assert u.sector_of("V") == "XLF"
    assert u.sector_of("MA") == "XLF"


def test_sector_of_health_industrial_energy():
    assert u.sector_of("UNH") == "XLV"
    assert u.sector_of("JNJ") == "XLV"
    assert u.sector_of("LLY") == "XLV"
    assert u.sector_of("CAT") == "XLI"
    assert u.sector_of("BA") == "XLI"
    assert u.sector_of("XOM") == "XLE"
    assert u.sector_of("CVX") == "XLE"


def test_sector_etfs_map_to_themselves():
    for etf in ("XLK", "XLF", "XLV", "XLE", "XLY", "XLP", "XLI", "XLU", "XLB", "XLRE", "XLC"):
        assert u.sector_of(etf) == etf


def test_broad_etfs_return_broad_label():
    for etf in ("SPY", "QQQ", "IWM", "DIA"):
        assert u.sector_of(etf) == "BROAD"


def test_sector_of_unknown_returns_none():
    assert u.sector_of("GME") is None
    assert u.sector_of("UNKNOWN") is None


def test_sector_of_is_case_insensitive():
    assert u.sector_of("aapl") == "XLK"
    assert u.sector_of("  TSLA  ") == "XLY"


def test_every_universe_member_has_sector_mapping():
    # Every ticker in TRADING_UNIVERSE must resolve via sector_of so attribution never returns None.
    for sym in u.TRADING_UNIVERSE:
        assert u.sector_of(sym) is not None, f"missing sector mapping for {sym}"
