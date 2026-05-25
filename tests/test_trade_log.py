"""Tests for scripts/trade_log.py — CLOSED-line parser + D1/D2/D3 aggregates."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import trade_log as tl  # noqa: E402


# ---------------- parse_closed_line ----------------

SAMPLE = (
    '- CLOSED 2026-05-23: NVDA entry=180.50 exit=195.00 initial_stop=165.00 '
    'shares=110 regime_entry=Bull sector=XLK pnl=$1595.00 r=0.97 '
    'reason="trailing stop hit"'
)


def test_parse_closed_line_extracts_all_fields():
    ct = tl.parse_closed_line(SAMPLE)
    assert ct is not None
    assert ct.symbol == "NVDA"
    assert ct.exit_date == date(2026, 5, 23)
    assert ct.entry_price == 180.50
    assert ct.exit_price == 195.00
    assert ct.initial_stop == 165.00
    assert ct.shares == 110
    assert ct.regime_at_entry == "Bull"
    assert ct.sector == "XLK"
    assert ct.pnl == 1595.00
    assert ct.r_multiple == 0.97
    assert ct.reason == "trailing stop hit"


def test_parse_closed_line_handles_dollar_signs_and_commas():
    line = ('- CLOSED 2026-05-23: AAPL entry=150.00 exit=160.00 initial_stop=140.00 '
            'shares=100 pnl=$1,000.00 r=1.0')
    ct = tl.parse_closed_line(line)
    assert ct is not None
    assert ct.pnl == 1000.00


def test_parse_closed_line_handles_negative_pnl_and_r():
    line = ('- CLOSED 2026-05-23: AAPL entry=150.00 exit=140.00 initial_stop=135.00 '
            'shares=100 regime_entry=Caution sector=XLK pnl=-$1000.00 r=-0.67 '
            'reason="cut at -7% per rule"')
    ct = tl.parse_closed_line(line)
    assert ct is not None
    assert ct.pnl == -1000.0
    assert ct.r_multiple == -0.67
    assert ct.is_win is False


def test_parse_closed_line_rejects_non_closed_markdown():
    assert tl.parse_closed_line("### May 23 — EOD Snapshot (Day 1)") is None
    assert tl.parse_closed_line("- EOD 2026-05-23: equity $100,432.10") is None
    assert tl.parse_closed_line("- OPEN 2026-05-23: NVDA entry=180.50") is None
    assert tl.parse_closed_line("- some prose about a trade") is None


def test_parse_closed_line_rejects_missing_required_field():
    # Missing `r=` field
    line = ('- CLOSED 2026-05-23: AAPL entry=150 exit=160 initial_stop=140 '
            'shares=100 pnl=$1000')
    assert tl.parse_closed_line(line) is None


def test_parse_closed_line_optional_fields_default_to_none():
    line = ('- CLOSED 2026-05-23: AAPL entry=150 exit=160 initial_stop=140 '
            'shares=100 pnl=$1000 r=2.0')
    ct = tl.parse_closed_line(line)
    assert ct is not None
    assert ct.regime_at_entry is None
    assert ct.sector is None
    assert ct.reason is None


# ---------------- parse_closed_trades (full log) ----------------

FIXTURE_LOG = """\
# Trade Log

### May 22 — EOD Snapshot
- EOD 2026-05-22: equity $100,100.00

### May 23 — Entries
- OPEN 2026-05-23: NVDA entry=180.50 initial_stop=165.00 shares=110 regime_entry=Bull sector=XLK sizing=flat_20pct thesis="AI tailwind"

Some prose about NVDA setup goes here.

### May 27 — Trailing stop hits
- CLOSED 2026-05-27: NVDA entry=180.50 exit=195.00 initial_stop=165.00 shares=110 regime_entry=Bull sector=XLK pnl=$1595.00 r=0.97 reason="trailing stop hit"

### May 28 — Cut a loser
- CLOSED 2026-05-28: AAPL entry=150.00 exit=139.50 initial_stop=140.00 shares=130 regime_entry=Neutral sector=XLK pnl=-$1365.00 r=-1.05 reason="cut at -7% per rule"

### June 2 — Another win
- CLOSED 2026-06-02: META entry=480.00 exit=520.00 initial_stop=440.00 shares=40 regime_entry=Bull sector=XLC pnl=$1600.00 r=1.0 reason="thesis broken — closed for gain"
"""


def test_parse_closed_trades_returns_only_closed_in_chronological_order():
    trades = tl.parse_closed_trades(FIXTURE_LOG)
    assert len(trades) == 3
    assert [t.symbol for t in trades] == ["NVDA", "AAPL", "META"]
    assert [t.exit_date for t in trades] == [
        date(2026, 5, 27), date(2026, 5, 28), date(2026, 6, 2)
    ]


def test_parse_closed_trades_handles_empty_log():
    assert tl.parse_closed_trades("") == []
    assert tl.parse_closed_trades("# only headers and prose") == []


def test_load_closed_trades_from_file(tmp_path, monkeypatch):
    log = tmp_path / "TRADE-LOG.md"
    log.write_text(FIXTURE_LOG)
    monkeypatch.setattr(tl, "TRADE_LOG", log)
    trades = tl.load_closed_trades()
    assert len(trades) == 3


def test_load_closed_trades_returns_empty_for_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(tl, "TRADE_LOG", tmp_path / "missing.md")
    assert tl.load_closed_trades() == []


# ---------------- compute_r ----------------

def test_compute_r_winner_at_2x_risk():
    # entry 100, stop 90 (risk 10), exit 120 → R = (120-100)/10 = 2.0
    assert tl.compute_r(entry=100, exit_=120, initial_stop=90) == 2.0


def test_compute_r_loss_at_stop_is_minus_one():
    assert tl.compute_r(entry=100, exit_=90, initial_stop=90) == -1.0


def test_compute_r_partial_loss():
    # Cut early at -7% with 10% stop: R = -0.7
    r = tl.compute_r(entry=100, exit_=93, initial_stop=90)
    assert r == pytest.approx(-0.7)


def test_compute_r_rejects_stop_at_or_above_entry():
    with pytest.raises(ValueError, match="must be strictly below"):
        tl.compute_r(entry=100, exit_=110, initial_stop=100)
    with pytest.raises(ValueError):
        tl.compute_r(entry=100, exit_=110, initial_stop=105)


# ---------------- aggregate (D1, D2, D3) ----------------

def _trade(sym: str, r: float, pnl: float, regime: str | None = None,
           sector: str | None = None, d: date = date(2026, 5, 23)) -> tl.ClosedTrade:
    return tl.ClosedTrade(
        symbol=sym, exit_date=d, entry_price=100, exit_price=100 + r * 10,
        initial_stop=90, shares=10, pnl=pnl,
        r_multiple=r, regime_at_entry=regime, sector=sector,
    )


def test_aggregate_empty_returns_zeros():
    a = tl.aggregate([])
    assert a.n == 0
    assert a.win_rate is None
    assert a.expectancy is None
    assert a.sector_pnl == {}


def test_aggregate_computes_win_rate_and_pnl():
    trades = [
        _trade("AAPL", r=2.0, pnl=200),
        _trade("MSFT", r=-1.0, pnl=-100),
        _trade("NVDA", r=1.5, pnl=150),
    ]
    a = tl.aggregate(trades)
    assert a.n == 3
    assert a.n_wins == 2
    assert a.n_losses == 1
    assert a.win_rate == pytest.approx(2 / 3, abs=0.001)
    assert a.total_pnl == 250.0


def test_aggregate_payoff_ratio_and_expectancy():
    # 2 wins at +2R, 1 loss at -1R → W=0.667, avg_win=2, avg_loss=-1, payoff=2,
    # expectancy = 0.667*2 - 0.333*1 = 1.0
    trades = [
        _trade("A", r=2.0, pnl=200),
        _trade("B", r=2.0, pnl=200),
        _trade("C", r=-1.0, pnl=-100),
    ]
    a = tl.aggregate(trades)
    assert a.payoff_ratio == pytest.approx(2.0)
    assert a.expectancy == pytest.approx(1.0, abs=0.001)


def test_aggregate_sector_pnl_groups_by_sector():
    trades = [
        _trade("AAPL", r=1.0, pnl=100, sector="XLK"),
        _trade("MSFT", r=2.0, pnl=200, sector="XLK"),
        _trade("JPM", r=-1.0, pnl=-150, sector="XLF"),
    ]
    a = tl.aggregate(trades)
    assert a.sector_pnl == {"XLK": 300.0, "XLF": -150.0}


def test_aggregate_regime_buckets_win_rate_and_pnl():
    trades = [
        _trade("A", r=2.0, pnl=200, regime="Bull"),
        _trade("B", r=1.0, pnl=100, regime="Bull"),
        _trade("C", r=-1.0, pnl=-100, regime="Bull"),
        _trade("D", r=-1.0, pnl=-100, regime="Caution"),
    ]
    a = tl.aggregate(trades)
    assert a.regime_pnl["Bull"] == 200.0
    assert a.regime_pnl["Caution"] == -100.0
    assert a.regime_win_rate["Bull"] == pytest.approx(2 / 3, abs=0.001)
    assert a.regime_win_rate["Caution"] == 0.0


def test_aggregate_ignores_trades_without_regime_or_sector_for_those_buckets():
    trades = [
        _trade("A", r=2.0, pnl=200, regime="Bull", sector="XLK"),
        _trade("B", r=1.0, pnl=100),  # no regime, no sector
    ]
    a = tl.aggregate(trades)
    assert a.sector_pnl == {"XLK": 200.0}
    assert a.regime_pnl == {"Bull": 200.0}
    # Win-rate counts ALL trades regardless of metadata.
    assert a.n == 2
    assert a.n_wins == 2


def test_aggregate_since_filters_by_date():
    trades = [
        _trade("OLD", r=2.0, pnl=200, d=date(2026, 4, 1)),
        _trade("RECENT", r=-1.0, pnl=-100, d=date(2026, 5, 28)),
        _trade("ALSO_RECENT", r=1.0, pnl=100, d=date(2026, 6, 1)),
    ]
    a = tl.aggregate_since(trades, since=date(2026, 5, 1))
    assert a.n == 2
    assert a.total_pnl == 0.0


def test_aggregate_handles_all_winners_no_losses():
    # Edge case: no losses → avg_r_loss is None, payoff/expectancy undefined.
    trades = [_trade("A", r=2.0, pnl=200), _trade("B", r=1.5, pnl=150)]
    a = tl.aggregate(trades)
    assert a.n_losses == 0
    assert a.avg_r_loss is None
    assert a.payoff_ratio is None
    assert a.expectancy is None
