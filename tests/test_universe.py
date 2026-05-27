"""Tests for scripts/universe.py — membership + sector mapping (Phase A7 + D2)."""
from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import universe as u  # noqa: E402


def test_universe_has_70_tickers():
    # Phase F (2026-05-27): expanded 40 → 70 to broaden screener opportunity set.
    assert len(u.TRADING_UNIVERSE) == 70


def test_phase_f_additions_present():
    # Sanity check that each Phase F group made it into the universe.
    for sym in ("AMD", "MU", "ORCL", "CRM", "ADBE", "NOW", "INTU"):  # tech
        assert sym in u.TRADING_UNIVERSE
    for sym in ("ABBV", "MRK", "TMO", "ABT", "DHR", "AMGN"):  # health
        assert sym in u.TRADING_UNIVERSE
    for sym in ("BAC", "GS", "MS", "SPGI", "BLK"):  # financials
        assert sym in u.TRADING_UNIVERSE
    for sym in ("GE", "RTX", "LMT", "HON", "UNP", "DE"):  # industrials
        assert sym in u.TRADING_UNIVERSE
    for sym in ("NKE", "MCD", "SBUX", "LOW"):  # consumer
        assert sym in u.TRADING_UNIVERSE
    for sym in ("SMH", "XBI"):  # thematic
        assert sym in u.TRADING_UNIVERSE


def test_phase_f_sector_mapping():
    # Tech adds
    assert u.sector_of("AMD") == "XLK"
    assert u.sector_of("ORCL") == "XLK"
    assert u.sector_of("SMH") == "XLK"
    # Health adds
    assert u.sector_of("ABBV") == "XLV"
    assert u.sector_of("XBI") == "XLV"
    # Financials adds
    assert u.sector_of("GS") == "XLF"
    # Industrials adds
    assert u.sector_of("RTX") == "XLI"
    # Consumer adds (all four discretionary)
    assert u.sector_of("MCD") == "XLY"
    assert u.sector_of("LOW") == "XLY"


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
