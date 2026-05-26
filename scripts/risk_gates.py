#!/usr/bin/env python3
"""Account-level risk gates: daily DD, weekly DD, peak-to-trough lock file.

These run BEFORE any buy/sell decision in every market-touching skill. Pure
arithmetic on equity history — no models, no opinions. If any gate trips, the
bot must respect the response (freeze, tighten, or lock).

Usage:
  python scripts/risk_gates.py check               # all gates, JSON to stdout
  python scripts/risk_gates.py lock-status         # 0 if no lock, 42 if locked
  python scripts/risk_gates.py update-peak EQUITY  # bump PEAK-EQUITY.txt if higher

State files:
  memory/PEAK-EQUITY.txt    Single float: highest EOD equity ever recorded.
  memory/LOCK               If present, all market-touching skills must refuse.

Responses:
  daily:    none | tighten_trails | freeze_entries_48h
  weekly:   none | freeze_until_monday
  drawdown: ok | LOCKED
"""
from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PEAK_FILE = ROOT / "memory" / "PEAK-EQUITY.txt"
LOCK_FILE = ROOT / "memory" / "LOCK"
TRADE_LOG = ROOT / "memory" / "TRADE-LOG.md"

DAILY_TIGHTEN_THRESHOLD_PCT = -2.0
DAILY_FREEZE_THRESHOLD_PCT = -3.0
WEEKLY_FREEZE_THRESHOLD_PCT = -5.0
DRAWDOWN_LOCK_THRESHOLD_PCT = -10.0

# Auto-recovery (Phase C): the drawdown lock auto-clears when BOTH conditions
# hold. Keeps the kill-switch from indefinitely silencing a bot whose drawdown
# has demonstrably healed.
LOCK_RECOVERY_STREAK_DAYS = 5         # consecutive non-negative EOD day-over-day
LOCK_RECOVERY_DD_IMPROVEMENT_PP = 3.0  # current_dd must beat trigger_dd by ≥ this


@dataclass(frozen=True)
class GateResult:
    gate: str
    tripped: bool
    response: str
    detail: str

    def as_dict(self) -> dict:
        return {
            "gate": self.gate,
            "tripped": self.tripped,
            "response": self.response,
            "detail": self.detail,
        }


def read_peak_equity() -> float | None:
    if not PEAK_FILE.exists():
        return None
    raw = PEAK_FILE.read_text().strip()
    if not raw:
        return None
    return float(raw)


def write_peak_equity(equity: float) -> None:
    PEAK_FILE.parent.mkdir(parents=True, exist_ok=True)
    PEAK_FILE.write_text(f"{equity:.2f}\n")


def update_peak_if_higher(current_equity: float) -> tuple[float, bool]:
    """Returns (new_peak, was_updated)."""
    existing = read_peak_equity()
    if existing is None or current_equity > existing:
        write_peak_equity(current_equity)
        return current_equity, True
    return existing, False


def lock_exists() -> bool:
    return LOCK_FILE.exists()


def create_lock(reason: str, *, trigger_date: date | None = None,
                trigger_equity: float | None = None,
                trigger_dd_pct: float | None = None) -> None:
    """Write the LOCK file. Embeds trigger metadata so maybe_unlock can evaluate
    auto-recovery later. Skills should always pass the trigger_* kwargs; without
    them, auto-recovery is disabled and a human must delete the file.
    """
    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = [f"LOCKED at {stamp}", f"Reason: {reason}"]
    if trigger_date is not None:
        lines.append(f"trigger_date={trigger_date.isoformat()}")
    if trigger_equity is not None:
        lines.append(f"trigger_equity={trigger_equity:.2f}")
    if trigger_dd_pct is not None:
        lines.append(f"trigger_dd_pct={trigger_dd_pct:.2f}")
    lines.append("")
    lines.append(
        f"Auto-recovery: {LOCK_RECOVERY_STREAK_DAYS} consecutive non-negative EOD days "
        f"AND drawdown improves by >= {LOCK_RECOVERY_DD_IMPROVEMENT_PP}pp from trigger. "
        "Otherwise delete this file manually after reviewing the failure."
    )
    LOCK_FILE.write_text("\n".join(lines) + "\n")


def remove_lock() -> None:
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()


@dataclass(frozen=True)
class LockMetadata:
    trigger_date: date
    trigger_equity: float
    trigger_dd_pct: float


_LOCK_META_RE = {
    "trigger_date": re.compile(r"^trigger_date=(\d{4}-\d{2}-\d{2})", re.MULTILINE),
    "trigger_equity": re.compile(r"^trigger_equity=([0-9.]+)", re.MULTILINE),
    "trigger_dd_pct": re.compile(r"^trigger_dd_pct=(-?[0-9.]+)", re.MULTILINE),
}


def parse_lock_metadata() -> LockMetadata | None:
    if not LOCK_FILE.exists():
        return None
    text = LOCK_FILE.read_text()
    td = _LOCK_META_RE["trigger_date"].search(text)
    te = _LOCK_META_RE["trigger_equity"].search(text)
    tp = _LOCK_META_RE["trigger_dd_pct"].search(text)
    if not (td and te and tp):
        return None
    return LockMetadata(
        trigger_date=date.fromisoformat(td.group(1)),
        trigger_equity=float(te.group(1)),
        trigger_dd_pct=float(tp.group(1)),
    )


def maybe_unlock(current_equity: float, today: date,
                 history: list[tuple[date, float]],
                 peak: float | None) -> tuple[bool, str]:
    """Return (should_unlock, reason). Caller must remove_lock() on True.

    Conditions (BOTH must hold):
      1. current_dd improved by >= LOCK_RECOVERY_DD_IMPROVEMENT_PP vs trigger.
      2. The last LOCK_RECOVERY_STREAK_DAYS EOD entries after the trigger date
         are non-negative day-over-day (a calm-or-up streak).
    """
    if not lock_exists():
        return False, "no lock present"
    meta = parse_lock_metadata()
    if meta is None:
        return False, "lock present without recoverable metadata — manual unlock required"

    if peak is None or peak <= 0:
        return False, "no peak recorded — cannot evaluate drawdown improvement"
    current_dd = (current_equity - peak) / peak * 100
    improvement = current_dd - meta.trigger_dd_pct
    if improvement < LOCK_RECOVERY_DD_IMPROVEMENT_PP:
        return False, (
            f"dd improvement {improvement:+.2f}pp < "
            f"{LOCK_RECOVERY_DD_IMPROVEMENT_PP}pp required "
            f"(trigger {meta.trigger_dd_pct:.2f}% → current {current_dd:.2f}%)"
        )

    post = [(d, eq) for d, eq in history if d > meta.trigger_date]
    if len(post) < LOCK_RECOVERY_STREAK_DAYS:
        return False, (
            f"only {len(post)} EOD days post-trigger "
            f"(need {LOCK_RECOVERY_STREAK_DAYS})"
        )

    pre = [(d, eq) for d, eq in history if d <= meta.trigger_date]
    prior_eq = pre[-1][1] if pre else meta.trigger_equity

    streak = 0
    for _, eq in post:
        if prior_eq > 0 and eq >= prior_eq:
            streak += 1
        else:
            streak = 0
        prior_eq = eq

    if streak < LOCK_RECOVERY_STREAK_DAYS:
        return False, (
            f"non-negative EOD streak {streak} < {LOCK_RECOVERY_STREAK_DAYS} required"
        )

    return True, (
        f"auto-unlock: {streak} consecutive non-negative EOD days "
        f"AND dd improved {improvement:+.2f}pp "
        f"(trigger {meta.trigger_dd_pct:.2f}% → current {current_dd:.2f}%)"
    )


# ----------------------------- EOD equity log -----------------------------
#
# TRADE-LOG.md contains EOD snapshots. We look for lines that match a known
# pattern emitted by the daily-summary skill — the canonical format is:
#
#     - EOD 2026-05-23: equity $100,432.10
#
# A small regex is enough; nothing else in TRADE-LOG should match.

EOD_LINE_RE = re.compile(
    r"EOD\s+(?P<date>\d{4}-\d{2}-\d{2}).{0,40}?equity\s+\$([0-9,]+(?:\.\d+)?)",
    re.IGNORECASE,
)


def parse_eod_equity_history() -> list[tuple[date, float]]:
    if not TRADE_LOG.exists():
        return []
    rows: list[tuple[date, float]] = []
    for line in TRADE_LOG.read_text().splitlines():
        m = EOD_LINE_RE.search(line)
        if not m:
            continue
        d = date.fromisoformat(m.group("date"))
        amount = float(m.group(2).replace(",", ""))
        rows.append((d, amount))
    rows.sort(key=lambda x: x[0])
    return rows


def yesterday_equity(history: list[tuple[date, float]], today: date) -> float | None:
    """Most recent EOD equity strictly before `today`."""
    prior = [eq for d, eq in history if d < today]
    return prior[-1] if prior else None


def last_friday_equity(history: list[tuple[date, float]], today: date) -> float | None:
    """EOD equity on the most recent Friday strictly before today.

    If we haven't recorded a Friday yet (early in the run), returns None and the
    gate stays neutral.
    """
    # Find the Friday on or before today, but strictly before today.
    days_back = (today.weekday() - 4) % 7
    if days_back == 0:
        days_back = 7  # if today IS Friday, want last Friday
    target = today - timedelta(days=days_back)
    for d, eq in reversed(history):
        if d <= target:
            return eq
    return None


# ------------------------------ gate logic --------------------------------


def check_daily(current_equity: float, yesterday: float | None) -> GateResult:
    if yesterday is None or yesterday <= 0:
        return GateResult("daily", False, "none", "no prior EOD equity recorded")
    pct = (current_equity - yesterday) / yesterday * 100
    if pct <= DAILY_FREEZE_THRESHOLD_PCT:
        return GateResult(
            "daily", True, "freeze_entries_48h",
            f"daily P&L {pct:.2f}% <= {DAILY_FREEZE_THRESHOLD_PCT}% "
            f"(equity ${current_equity:,.2f} vs yesterday ${yesterday:,.2f})",
        )
    if pct <= DAILY_TIGHTEN_THRESHOLD_PCT:
        return GateResult(
            "daily", True, "tighten_trails",
            f"daily P&L {pct:.2f}% <= {DAILY_TIGHTEN_THRESHOLD_PCT}% "
            f"(equity ${current_equity:,.2f} vs yesterday ${yesterday:,.2f})",
        )
    return GateResult("daily", False, "none", f"daily P&L {pct:.2f}% within bounds")


def check_weekly(current_equity: float, last_friday: float | None) -> GateResult:
    if last_friday is None or last_friday <= 0:
        return GateResult("weekly", False, "none", "no prior Friday EOD recorded")
    pct = (current_equity - last_friday) / last_friday * 100
    if pct <= WEEKLY_FREEZE_THRESHOLD_PCT:
        return GateResult(
            "weekly", True, "freeze_until_monday",
            f"week P&L {pct:.2f}% <= {WEEKLY_FREEZE_THRESHOLD_PCT}% "
            f"(equity ${current_equity:,.2f} vs last Friday ${last_friday:,.2f})",
        )
    return GateResult("weekly", False, "none", f"week P&L {pct:.2f}% within bounds")


def check_drawdown_lock(current_equity: float, peak: float | None) -> GateResult:
    if peak is None or peak <= 0:
        return GateResult("drawdown", False, "ok", "no peak recorded yet")
    pct = (current_equity - peak) / peak * 100
    if pct <= DRAWDOWN_LOCK_THRESHOLD_PCT:
        return GateResult(
            "drawdown", True, "LOCKED",
            f"drawdown {pct:.2f}% <= {DRAWDOWN_LOCK_THRESHOLD_PCT}% "
            f"(equity ${current_equity:,.2f} vs peak ${peak:,.2f})",
        )
    return GateResult("drawdown", False, "ok", f"drawdown {pct:.2f}%")


def check_all(current_equity: float, today: date | None = None) -> dict:
    today = today or date.today()
    history = parse_eod_equity_history()
    y_eq = yesterday_equity(history, today)
    f_eq = last_friday_equity(history, today)
    peak = read_peak_equity()

    daily = check_daily(current_equity, y_eq)
    weekly = check_weekly(current_equity, f_eq)
    drawdown = check_drawdown_lock(current_equity, peak)

    if drawdown.tripped and not lock_exists():
        trigger_dd = (current_equity - peak) / peak * 100 if peak and peak > 0 else 0.0
        create_lock(
            drawdown.detail,
            trigger_date=today,
            trigger_equity=current_equity,
            trigger_dd_pct=trigger_dd,
        )

    # Phase-C auto-recovery: if today's drawdown is no longer tripping AND the
    # recovery streak/improvement gates are satisfied, clear the lock now.
    lock_auto_recovered: str | None = None
    if lock_exists() and not drawdown.tripped:
        ok, msg = maybe_unlock(current_equity, today, history, peak)
        if ok:
            remove_lock()
            lock_auto_recovered = msg

    any_freeze = daily.response == "freeze_entries_48h" or weekly.tripped
    entries_blocked = any_freeze or drawdown.tripped or lock_exists()
    tighten = daily.response == "tighten_trails"

    # Phase E: cap deployment at 40% if a binary macro event releases within
    # the next 2 trading days. Caller decides how to enforce — typically by
    # passing pre_macro_event_cap_pct to sizing.recommend(), or by Claude
    # skipping the 3rd candidate when cap_active is true.
    try:
        import trading_calendar as tcal  # type: ignore
        macro_check = tcal.pre_macro_event_check(today)
    except Exception:
        macro_check = {"cap_active": False, "within_24h": False,
                       "event_name": None, "event_date": None,
                       "days_to_event": None}

    result = {
        "current_equity": current_equity,
        "peak_equity": peak,
        "yesterday_equity": y_eq,
        "last_friday_equity": f_eq,
        "lock_file_present": lock_exists(),
        "entries_blocked": entries_blocked,
        "tighten_trails": tighten,
        "pre_macro_event": macro_check,
        "gates": [daily.as_dict(), weekly.as_dict(), drawdown.as_dict()],
    }
    if lock_auto_recovered is not None:
        result["lock_auto_recovered"] = lock_auto_recovered
    return result


def _fetch_alpaca_equity() -> float:
    """Best-effort: shell out to scripts/alpaca.sh account and pull equity.

    Returns 0.0 if Alpaca call fails — caller decides what to do.
    """
    import subprocess
    try:
        out = subprocess.check_output(
            ["bash", str(ROOT / "scripts" / "alpaca.sh"), "account"],
            stderr=subprocess.DEVNULL,
            timeout=15,
        )
        data = json.loads(out)
        return float(data.get("equity", 0.0))
    except Exception:
        return 0.0


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    cmd = sys.argv[1]

    if cmd == "lock-status":
        if lock_exists():
            print(LOCK_FILE.read_text(), file=sys.stderr)
            return 42
        return 0

    if cmd == "update-peak":
        if len(sys.argv) < 3:
            print("usage: update-peak EQUITY", file=sys.stderr)
            return 2
        eq = float(sys.argv[2])
        new_peak, updated = update_peak_if_higher(eq)
        print(json.dumps({"peak": new_peak, "updated": updated}))
        return 0

    if cmd == "check":
        # Optional explicit equity override; otherwise pull from Alpaca.
        if len(sys.argv) >= 3:
            equity = float(sys.argv[2])
        else:
            equity = _fetch_alpaca_equity()
            if equity <= 0:
                print(
                    json.dumps({"error": "could not fetch equity from Alpaca"}),
                    file=sys.stderr,
                )
                return 3
        print(json.dumps(check_all(equity), indent=2))
        return 0

    print(f"unknown command: {cmd}", file=sys.stderr)
    print(__doc__, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
