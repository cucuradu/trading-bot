#!/usr/bin/env python3
"""Carry-forward watchlist for the Trading Bot (Phase G2).

The pre-market routine writes daily candidates with a planned entry price
and a Setup type (PULLBACK / BREAKOUT / MOMENTUM). When the day's limit /
stop / market order does not fill, the daily-summary routine adds the
candidate here so the next pre-market can carry it forward instead of
losing the thesis to a fresh screener re-rank.

File: memory/WATCHLIST.md, one entry per line:

    - YYYY-MM-DD: SYM setup=PULLBACK|BREAKOUT|MOMENTUM entry=PRICE
      initial_stop=PRICE days_remaining=N thesis="..."

Lifecycle:
  - add SYM ...        — append entry (used by daily-summary on missed fill)
  - list               — JSON of current entries (used by pre-market)
  - prune              — drop entries with days_remaining <= 0 or expired

Hard cap: 6 entries (matches the open-position cap so the carry never
crowds out fresh ideas). Token cost when read by pre-market: < 200 tokens.

Usage:
  python scripts/watchlist.py list
  python scripts/watchlist.py add SYM --setup PULLBACK --entry 138.50 \
      --stop 125.00 --thesis "AI capex cycle, COMPUTEX June"
  python scripts/watchlist.py prune          # drops expired entries
  python scripts/watchlist.py drop SYM       # remove a single ticker
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WATCHLIST = ROOT / "memory" / "WATCHLIST.md"

MAX_ENTRIES = 6
DEFAULT_DAYS = 3
VALID_SETUPS = {"PULLBACK", "BREAKOUT", "MOMENTUM"}

HEADER = (
    "# Watchlist (Phase G2)\n\n"
    "Carry-forward candidates whose planned entry did not fill. Each entry\n"
    "expires after N trading days (default 3). Pre-market consults this file\n"
    "at STEP 4b and applies a small screener bonus to symbols listed here.\n\n"
)

LINE_RE = re.compile(
    r"-\s*(?P<date>\d{4}-\d{2}-\d{2}):\s*(?P<sym>[A-Z][A-Z0-9.]*)\s+(?P<kv>.+?)"
    r"(?:\s+thesis=\"[^\"]*\")?\s*$"
)


@dataclass
class WatchEntry:
    symbol: str
    added: date
    setup: str
    planned_entry: float
    initial_stop: float
    days_remaining: int
    thesis: str = ""

    def as_jsonable(self) -> dict:
        d = asdict(self)
        d["added"] = self.added.isoformat()
        return d

    def to_line(self) -> str:
        thesis = self.thesis.replace('"', "'")  # keep quoting simple
        return (
            f"- {self.added.isoformat()}: {self.symbol} setup={self.setup} "
            f"entry={self.planned_entry:.2f} initial_stop={self.initial_stop:.2f} "
            f"days_remaining={self.days_remaining} thesis=\"{thesis}\""
        )


def parse_line(line: str) -> WatchEntry | None:
    m = LINE_RE.match(line.strip())
    if not m:
        return None
    kv: dict[str, str] = {}
    for km in re.finditer(r"(\w+)=([^\s\"]+|\"[^\"]*\")", m.group("kv")):
        v = km.group(2)
        if v.startswith('"') and v.endswith('"'):
            v = v[1:-1]
        kv[km.group(1).lower()] = v
    thesis = ""
    tm = re.search(r'thesis="([^"]*)"', line)
    if tm:
        thesis = tm.group(1)
    required = ("setup", "entry", "initial_stop", "days_remaining")
    if not all(k in kv for k in required):
        return None
    setup = kv["setup"].upper()
    if setup not in VALID_SETUPS:
        return None
    try:
        return WatchEntry(
            symbol=m.group("sym").upper(),
            added=date.fromisoformat(m.group("date")),
            setup=setup,
            planned_entry=float(kv["entry"]),
            initial_stop=float(kv["initial_stop"]),
            days_remaining=int(kv["days_remaining"]),
            thesis=thesis,
        )
    except (ValueError, KeyError):
        return None


def load(path: Path | None = None) -> list[WatchEntry]:
    p = path or WATCHLIST
    if not p.exists():
        return []
    entries: list[WatchEntry] = []
    for line in p.read_text().splitlines():
        e = parse_line(line)
        if e is not None:
            entries.append(e)
    return entries


def save(entries: list[WatchEntry], path: Path | None = None) -> None:
    p = path or WATCHLIST
    p.parent.mkdir(parents=True, exist_ok=True)
    body = HEADER + "\n".join(e.to_line() for e in entries)
    if entries:
        body += "\n"
    p.write_text(body)


def add_entry(
    symbol: str,
    setup: str,
    entry: float,
    initial_stop: float,
    thesis: str = "",
    days: int = DEFAULT_DAYS,
    today: date | None = None,
    path: Path | None = None,
) -> WatchEntry:
    today = today or date.today()
    setup = setup.upper()
    if setup not in VALID_SETUPS:
        raise ValueError(f"setup must be one of {sorted(VALID_SETUPS)}, got {setup!r}")
    entries = load(path)
    # If ticker already present, refresh in place rather than duplicate.
    entries = [e for e in entries if e.symbol != symbol.upper()]
    new = WatchEntry(
        symbol=symbol.upper(),
        added=today,
        setup=setup,
        planned_entry=float(entry),
        initial_stop=float(initial_stop),
        days_remaining=int(days),
        thesis=thesis,
    )
    entries.append(new)
    # Cap at MAX_ENTRIES, dropping the oldest (lowest days_remaining first,
    # then earliest added) — fresh adds win against tired ones.
    if len(entries) > MAX_ENTRIES:
        entries.sort(key=lambda e: (-e.days_remaining, -e.added.toordinal()))
        entries = entries[:MAX_ENTRIES]
    save(entries, path)
    return new


def drop(symbol: str, path: Path | None = None) -> bool:
    entries = load(path)
    n0 = len(entries)
    entries = [e for e in entries if e.symbol != symbol.upper()]
    if len(entries) == n0:
        return False
    save(entries, path)
    return True


def prune(path: Path | None = None) -> dict:
    """Drop expired entries (days_remaining <= 0) and decrement the rest.

    Daily-summary calls this once per EOD. Returns a summary so the routine
    can include the expirations in its WhatsApp brief.
    """
    entries = load(path)
    kept: list[WatchEntry] = []
    expired: list[str] = []
    for e in entries:
        new_days = e.days_remaining - 1
        if new_days <= 0:
            expired.append(e.symbol)
            continue
        kept.append(
            WatchEntry(
                symbol=e.symbol,
                added=e.added,
                setup=e.setup,
                planned_entry=e.planned_entry,
                initial_stop=e.initial_stop,
                days_remaining=new_days,
                thesis=e.thesis,
            )
        )
    save(kept, path)
    return {"kept": [k.symbol for k in kept], "expired": expired}


def main() -> int:
    p = argparse.ArgumentParser(prog="watchlist.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="JSON of current entries")
    sub.add_parser("prune", help="drop expired entries, decrement remaining")

    sp_add = sub.add_parser("add", help="append an entry")
    sp_add.add_argument("symbol")
    sp_add.add_argument("--setup", required=True, choices=sorted(VALID_SETUPS))
    sp_add.add_argument("--entry", type=float, required=True)
    sp_add.add_argument("--stop", type=float, required=True, dest="initial_stop")
    sp_add.add_argument("--thesis", default="")
    sp_add.add_argument("--days", type=int, default=DEFAULT_DAYS)

    sp_drop = sub.add_parser("drop", help="remove one ticker")
    sp_drop.add_argument("symbol")

    args = p.parse_args()

    if args.cmd == "list":
        print(json.dumps([e.as_jsonable() for e in load()], indent=2))
    elif args.cmd == "prune":
        print(json.dumps(prune(), indent=2))
    elif args.cmd == "add":
        e = add_entry(
            symbol=args.symbol,
            setup=args.setup,
            entry=args.entry,
            initial_stop=args.initial_stop,
            thesis=args.thesis,
            days=args.days,
        )
        print(json.dumps(e.as_jsonable(), indent=2))
    elif args.cmd == "drop":
        ok = drop(args.symbol)
        print(json.dumps({"dropped": ok, "symbol": args.symbol.upper()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
