"""Tests for scripts/risk_gates.py — daily/weekly DD, peak watermark, lock file."""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

# scripts/ is not a package; add it to sys.path for direct import.
_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import risk_gates as rg  # noqa: E402


# ---------------- daily DD ----------------

def test_daily_unchanged_is_not_tripped():
    r = rg.check_daily(100_000, 100_000)
    assert not r.tripped
    assert r.response == "none"


def test_daily_minus_one_percent_is_not_tripped():
    r = rg.check_daily(99_000, 100_000)
    assert not r.tripped


def test_daily_minus_two_percent_triggers_tighten():
    r = rg.check_daily(98_000, 100_000)
    assert r.tripped
    assert r.response == "tighten_trails"


def test_daily_minus_three_percent_triggers_freeze():
    r = rg.check_daily(97_000, 100_000)
    assert r.tripped
    assert r.response == "freeze_entries_48h"


def test_daily_freeze_takes_precedence_over_tighten():
    r = rg.check_daily(96_500, 100_000)  # −3.5%
    assert r.response == "freeze_entries_48h"


def test_daily_no_history_returns_neutral():
    r = rg.check_daily(100_000, None)
    assert not r.tripped
    assert r.response == "none"


# ---------------- weekly DD ----------------

def test_weekly_minus_four_is_not_tripped():
    r = rg.check_weekly(96_000, 100_000)
    assert not r.tripped


def test_weekly_minus_five_triggers_freeze():
    r = rg.check_weekly(95_000, 100_000)
    assert r.tripped
    assert r.response == "freeze_until_monday"


def test_weekly_minus_six_triggers_freeze():
    r = rg.check_weekly(94_000, 100_000)
    assert r.tripped


# ---------------- drawdown lock ----------------

def test_drawdown_within_bounds_is_ok():
    r = rg.check_drawdown_lock(95_000, 100_000)  # −5%
    assert not r.tripped


def test_drawdown_minus_ten_triggers_lock():
    r = rg.check_drawdown_lock(90_000, 100_000)
    assert r.tripped
    assert r.response == "LOCKED"


def test_drawdown_minus_ten_one_triggers_lock():
    r = rg.check_drawdown_lock(89_900, 100_000)
    assert r.tripped


def test_drawdown_no_peak_recorded_is_ok():
    r = rg.check_drawdown_lock(100_000, None)
    assert not r.tripped


# ---------------- peak watermark ----------------

def test_update_peak_writes_higher_value(tmp_path, monkeypatch):
    fake_peak = tmp_path / "PEAK-EQUITY.txt"
    monkeypatch.setattr(rg, "PEAK_FILE", fake_peak)
    fake_peak.write_text("100000.00\n")

    new_peak, updated = rg.update_peak_if_higher(105_000.0)
    assert updated is True
    assert new_peak == 105_000.0
    assert fake_peak.read_text().strip() == "105000.00"


def test_update_peak_skips_lower_value(tmp_path, monkeypatch):
    fake_peak = tmp_path / "PEAK-EQUITY.txt"
    monkeypatch.setattr(rg, "PEAK_FILE", fake_peak)
    fake_peak.write_text("100000.00\n")

    new_peak, updated = rg.update_peak_if_higher(95_000.0)
    assert updated is False
    assert new_peak == 100_000.0
    assert fake_peak.read_text().strip() == "100000.00"


def test_update_peak_initializes_when_missing(tmp_path, monkeypatch):
    fake_peak = tmp_path / "PEAK-EQUITY.txt"
    monkeypatch.setattr(rg, "PEAK_FILE", fake_peak)

    new_peak, updated = rg.update_peak_if_higher(100_000.0)
    assert updated is True
    assert new_peak == 100_000.0


# ---------------- EOD log parser ----------------

EOD_FIXTURE = """\
### May 23 — EOD Snapshot (Day 1, Saturday)
- EOD 2026-05-23: equity $100,432.10
**Portfolio:** $100,432.10 | **Cash:** $98,000

### May 22 — EOD Snapshot (Day 0, Friday)
- EOD 2026-05-22: equity $100,100.00
**Portfolio:** $100,100.00

### May 21 — EOD Snapshot (Day -1, Thursday)
- EOD 2026-05-21: equity $99,750.50
"""


def test_parse_eod_log_extracts_ordered_history(tmp_path, monkeypatch):
    log = tmp_path / "TRADE-LOG.md"
    log.write_text(EOD_FIXTURE)
    monkeypatch.setattr(rg, "TRADE_LOG", log)

    rows = rg.parse_eod_equity_history()
    assert [r[0] for r in rows] == [
        date(2026, 5, 21), date(2026, 5, 22), date(2026, 5, 23),
    ]
    assert rows[-1][1] == 100_432.10


def test_yesterday_equity_picks_most_recent_prior():
    history = [
        (date(2026, 5, 21), 99_750.50),
        (date(2026, 5, 22), 100_100.00),
        (date(2026, 5, 23), 100_432.10),
    ]
    assert rg.yesterday_equity(history, date(2026, 5, 23)) == 100_100.00


def test_last_friday_equity_skips_intraweek():
    history = [
        (date(2026, 5, 22), 100_100.00),  # Friday
        (date(2026, 5, 25), 100_200.00),  # Monday
        (date(2026, 5, 26), 100_300.00),  # Tuesday
    ]
    # On Tuesday, last Friday is May 22.
    assert rg.last_friday_equity(history, date(2026, 5, 26)) == 100_100.00


def test_last_friday_equity_on_a_friday_returns_prior_friday():
    history = [
        (date(2026, 5, 15), 99_000.00),  # prior Friday
        (date(2026, 5, 22), 100_100.00),  # this Friday
    ]
    # When today IS Friday May 22, "last Friday" means May 15.
    assert rg.last_friday_equity(history, date(2026, 5, 22)) == 99_000.00


# ---------------- check_all integration ----------------

def test_check_all_blocks_entries_on_lock(tmp_path, monkeypatch):
    fake_peak = tmp_path / "PEAK-EQUITY.txt"
    fake_lock = tmp_path / "LOCK"
    fake_log = tmp_path / "TRADE-LOG.md"
    monkeypatch.setattr(rg, "PEAK_FILE", fake_peak)
    monkeypatch.setattr(rg, "LOCK_FILE", fake_lock)
    monkeypatch.setattr(rg, "TRADE_LOG", fake_log)
    fake_peak.write_text("100000.00\n")
    fake_log.write_text(EOD_FIXTURE)

    # 12% drawdown should trip lock + block entries.
    result = rg.check_all(88_000.0, today=date(2026, 5, 25))
    assert result["entries_blocked"] is True
    assert result["lock_file_present"] is True
    assert fake_lock.exists()


def test_check_all_clean_state_allows_entries(tmp_path, monkeypatch):
    fake_peak = tmp_path / "PEAK-EQUITY.txt"
    fake_lock = tmp_path / "LOCK"
    fake_log = tmp_path / "TRADE-LOG.md"
    monkeypatch.setattr(rg, "PEAK_FILE", fake_peak)
    monkeypatch.setattr(rg, "LOCK_FILE", fake_lock)
    monkeypatch.setattr(rg, "TRADE_LOG", fake_log)
    fake_peak.write_text("100000.00\n")
    fake_log.write_text(EOD_FIXTURE)

    # Tiny gain — nothing should trip.
    result = rg.check_all(100_500.0, today=date(2026, 5, 25))
    assert result["entries_blocked"] is False
    assert result["lock_file_present"] is False
    assert result["tighten_trails"] is False


# ---------------- lock metadata + auto-recovery (Phase C) ----------------

def test_create_lock_embeds_trigger_metadata(tmp_path, monkeypatch):
    fake_lock = tmp_path / "LOCK"
    monkeypatch.setattr(rg, "LOCK_FILE", fake_lock)
    rg.create_lock(
        "drawdown -11.00% <= -10.00%",
        trigger_date=date(2026, 5, 1),
        trigger_equity=89_000.0,
        trigger_dd_pct=-11.00,
    )
    meta = rg.parse_lock_metadata()
    assert meta is not None
    assert meta.trigger_date == date(2026, 5, 1)
    assert meta.trigger_equity == 89_000.0
    assert meta.trigger_dd_pct == -11.00


def test_parse_lock_metadata_returns_none_when_legacy_lock(tmp_path, monkeypatch):
    fake_lock = tmp_path / "LOCK"
    monkeypatch.setattr(rg, "LOCK_FILE", fake_lock)
    fake_lock.write_text("LOCKED at whenever\nReason: legacy\n")
    assert rg.parse_lock_metadata() is None


def _seven_up_days_after_trigger(trigger_eq: float, step: float = 200.0) -> str:
    """Build an EOD fixture with 7 non-negative consecutive days after a trigger
    on 2026-05-01. Each day_over_day is exactly +step.
    """
    lines = [f"- EOD 2026-05-01: equity ${trigger_eq:,.2f}"]
    eq = trigger_eq
    for i in range(1, 8):
        eq += step
        d = f"2026-05-{i:02d}"  # weekend skipping is irrelevant for the parser
        lines.append(f"- EOD 2026-05-0{i+1}: equity ${eq:,.2f}")
    return "\n".join(lines) + "\n"


def test_maybe_unlock_clears_lock_when_streak_and_dd_improve(tmp_path, monkeypatch):
    fake_peak = tmp_path / "PEAK-EQUITY.txt"
    fake_lock = tmp_path / "LOCK"
    fake_log = tmp_path / "TRADE-LOG.md"
    monkeypatch.setattr(rg, "PEAK_FILE", fake_peak)
    monkeypatch.setattr(rg, "LOCK_FILE", fake_lock)
    monkeypatch.setattr(rg, "TRADE_LOG", fake_log)
    fake_peak.write_text("100000.00\n")
    fake_log.write_text(_seven_up_days_after_trigger(trigger_eq=89_000.0))

    rg.create_lock("drawdown -11.00% <= -10.00%",
                   trigger_date=date(2026, 5, 1),
                   trigger_equity=89_000.0,
                   trigger_dd_pct=-11.00)

    # Today: equity recovered to 93,000 → dd -7%, improvement +4pp from -11.
    result = rg.check_all(93_000.0, today=date(2026, 5, 9))
    assert "lock_auto_recovered" in result
    assert result["lock_file_present"] is False
    assert not fake_lock.exists()


def test_maybe_unlock_does_not_clear_without_enough_dd_improvement(tmp_path, monkeypatch):
    fake_peak = tmp_path / "PEAK-EQUITY.txt"
    fake_lock = tmp_path / "LOCK"
    fake_log = tmp_path / "TRADE-LOG.md"
    monkeypatch.setattr(rg, "PEAK_FILE", fake_peak)
    monkeypatch.setattr(rg, "LOCK_FILE", fake_lock)
    monkeypatch.setattr(rg, "TRADE_LOG", fake_log)
    fake_peak.write_text("100000.00\n")
    fake_log.write_text(_seven_up_days_after_trigger(trigger_eq=89_000.0))

    rg.create_lock("drawdown -11.00% <= -10.00%",
                   trigger_date=date(2026, 5, 1),
                   trigger_equity=89_000.0,
                   trigger_dd_pct=-11.00)

    # Today: equity 90,000 → dd -10%, improvement +1pp only.
    result = rg.check_all(90_000.0, today=date(2026, 5, 9))
    assert "lock_auto_recovered" not in result
    assert fake_lock.exists()


def test_maybe_unlock_does_not_clear_when_streak_broken(tmp_path, monkeypatch):
    fake_peak = tmp_path / "PEAK-EQUITY.txt"
    fake_lock = tmp_path / "LOCK"
    fake_log = tmp_path / "TRADE-LOG.md"
    monkeypatch.setattr(rg, "PEAK_FILE", fake_peak)
    monkeypatch.setattr(rg, "LOCK_FILE", fake_lock)
    monkeypatch.setattr(rg, "TRADE_LOG", fake_log)
    fake_peak.write_text("100000.00\n")
    # 7 days after trigger but the 4th day is a DOWN day → streak resets.
    fake_log.write_text(
        "- EOD 2026-05-01: equity $89,000.00\n"
        "- EOD 2026-05-02: equity $89,500.00\n"
        "- EOD 2026-05-03: equity $90,000.00\n"
        "- EOD 2026-05-04: equity $90,500.00\n"
        "- EOD 2026-05-05: equity $89,800.00\n"  # red day breaks streak
        "- EOD 2026-05-06: equity $90,200.00\n"
        "- EOD 2026-05-07: equity $90,800.00\n"
        "- EOD 2026-05-08: equity $93,000.00\n"
    )
    rg.create_lock("drawdown -11.00% <= -10.00%",
                   trigger_date=date(2026, 5, 1),
                   trigger_equity=89_000.0,
                   trigger_dd_pct=-11.00)

    # dd improved to -7% (+4pp), but only 4 up days at the end → streak < 5.
    result = rg.check_all(93_000.0, today=date(2026, 5, 9))
    assert "lock_auto_recovered" not in result
    assert fake_lock.exists()


def test_maybe_unlock_skips_when_legacy_lock_has_no_metadata(tmp_path, monkeypatch):
    fake_peak = tmp_path / "PEAK-EQUITY.txt"
    fake_lock = tmp_path / "LOCK"
    fake_log = tmp_path / "TRADE-LOG.md"
    monkeypatch.setattr(rg, "PEAK_FILE", fake_peak)
    monkeypatch.setattr(rg, "LOCK_FILE", fake_lock)
    monkeypatch.setattr(rg, "TRADE_LOG", fake_log)
    fake_peak.write_text("100000.00\n")
    fake_log.write_text(_seven_up_days_after_trigger(trigger_eq=89_000.0))
    fake_lock.write_text("LOCKED at whenever\nReason: pre-Phase-C lock without metadata\n")

    # Even with full recovery on equity, a metadata-less lock requires manual unlock.
    result = rg.check_all(99_500.0, today=date(2026, 5, 9))
    assert "lock_auto_recovered" not in result
    assert fake_lock.exists()
