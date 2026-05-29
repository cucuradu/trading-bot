#!/usr/bin/env python3
"""Parser + aggregations for memory/TRADE-LOG.md (Phase D foundation).

The skills append free-form markdown to TRADE-LOG.md for human readability AND
a single canonical CLOSED line per closed trade for machine consumption:

    - CLOSED YYYY-MM-DD: SYM entry=PRICE exit=PRICE initial_stop=PRICE shares=N
      regime_entry=REGIME sector=SECTOR pnl=$X.XX r=R.RR reason="..."

Phase G adds a PENDING line for limit/stop entries that are placed but not
yet filled (broker-side conditional orders):

    - PENDING YYYY-MM-DD: SYM order_id=ABC type=limit shares=N entry=PRICE
      initial_stop=PRICE regime_entry=REGIME sector=SECTOR sizing=METHOD
      thesis="..."

PENDING orders do not count toward the weekly trade cap until they fill and
are promoted to an OPEN line by daily-summary's reconciliation step.

The same canonical EOD line already exists (parsed by scripts/risk_gates.py):

    - EOD YYYY-MM-DD: equity $X,XXX.XX

This module exposes the closed-trade parser + helpers used by:
  - scripts/sizing.py        (D4 Half-Kelly switchover at N >= 30)
  - weekly-review skill      (D1 expectancy, D2 sector P&L, D3 regime stats)

Usage:
  python scripts/trade_log.py list-closed              # JSON: all closed trades
  python scripts/trade_log.py list-pending             # JSON: open PENDING orders
  python scripts/trade_log.py stats                    # JSON: aggregates
  python scripts/trade_log.py stats-since YYYY-MM-DD   # JSON: aggregates from date
  python scripts/trade_log.py count                    # int: N closed trades
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
TRADE_LOG = ROOT / "memory" / "TRADE-LOG.md"

# Match lines like:
#   - CLOSED 2026-05-23: NVDA entry=180.50 exit=195.00 initial_stop=165.00 shares=110
#     regime_entry=Bull sector=XLK pnl=$1595.00 r=0.97 reason="trailing stop hit"
#
# Be tolerant: keys may appear in any order; the reason field is optional.
CLOSED_LINE_RE = re.compile(
    r"-\s*CLOSED\s+(?P<date>\d{4}-\d{2}-\d{2}):\s*(?P<sym>[A-Z][A-Z0-9.]*)\s+(?P<kv>.+?)(?:\s+reason=\"[^\"]*\")?\s*$",
    re.IGNORECASE,
)
# Phase G — PENDING lines for limit/stop entries that have been placed but
# not yet filled. Daily-summary reconciles these against Alpaca and promotes
# fills to canonical OPEN lines.
PENDING_LINE_RE = re.compile(
    r"-\s*PENDING\s+(?P<date>\d{4}-\d{2}-\d{2}):\s*(?P<sym>[A-Z][A-Z0-9.]*)\s+(?P<kv>.+?)(?:\s+thesis=\"[^\"]*\")?\s*$",
    re.IGNORECASE,
)
KV_RE = re.compile(r"(\w+)=([^\s\"]+|\"[^\"]*\")")


@dataclass(frozen=True)
class ClosedTrade:
    symbol: str
    exit_date: date
    entry_price: float
    exit_price: float
    initial_stop: float
    shares: int
    pnl: float
    r_multiple: float
    regime_at_entry: str | None = None
    sector: str | None = None
    reason: str | None = None

    @property
    def is_win(self) -> bool:
        return self.r_multiple > 0

    def as_jsonable(self) -> dict:
        d = asdict(self)
        d["exit_date"] = self.exit_date.isoformat()
        return d


def _parse_kv_segment(text: str) -> dict[str, str]:
    """Pull KEY=VALUE pairs out of the tail of a CLOSED line."""
    out: dict[str, str] = {}
    for m in KV_RE.finditer(text):
        val = m.group(2)
        if val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        out[m.group(1).lower()] = val
    return out


def _coerce_float(s: str) -> float:
    # Strip currency markers anywhere in the token (handles `-$1365.00`).
    return float(s.replace("$", "").replace(",", ""))


def parse_closed_line(line: str) -> ClosedTrade | None:
    """Parse a single CLOSED line. Returns None if it doesn't match.

    Required keys: entry, exit, initial_stop, shares, pnl, r.
    Optional keys: regime_entry, sector, reason.
    """
    m = CLOSED_LINE_RE.match(line.strip())
    if not m:
        return None
    kv = _parse_kv_segment(m.group("kv") + " " + (m.group(0) if "reason=" in m.group(0) else ""))
    # Reason capture is handled separately — re-scan the original line for it.
    reason = None
    rm = re.search(r'reason="([^"]*)"', line)
    if rm:
        reason = rm.group(1)

    required = ("entry", "exit", "initial_stop", "shares", "pnl", "r")
    if not all(k in kv for k in required):
        return None

    try:
        return ClosedTrade(
            symbol=m.group("sym").upper(),
            exit_date=date.fromisoformat(m.group("date")),
            entry_price=_coerce_float(kv["entry"]),
            exit_price=_coerce_float(kv["exit"]),
            initial_stop=_coerce_float(kv["initial_stop"]),
            shares=int(kv["shares"]),
            pnl=_coerce_float(kv["pnl"]),
            r_multiple=_coerce_float(kv["r"]),
            regime_at_entry=kv.get("regime_entry"),
            sector=kv.get("sector"),
            reason=reason,
        )
    except (ValueError, KeyError):
        return None


def parse_closed_trades(text: str) -> list[ClosedTrade]:
    """Parse all CLOSED lines from a TRADE-LOG.md body."""
    out: list[ClosedTrade] = []
    for line in text.splitlines():
        ct = parse_closed_line(line)
        if ct is not None:
            out.append(ct)
    return sorted(out, key=lambda c: c.exit_date)


def load_closed_trades(path: Path | None = None) -> list[ClosedTrade]:
    p = path or TRADE_LOG
    if not p.exists():
        return []
    return parse_closed_trades(p.read_text())


# ---------- PENDING-line parser (Phase G) ----------

@dataclass(frozen=True)
class PendingOrder:
    """A limit/stop entry order placed but not yet filled.

    Daily-summary reconciles these against Alpaca: filled -> promote to OPEN
    line; canceled/expired -> drop (and optionally add to WATCHLIST.md).
    """
    symbol: str
    placed_date: date
    order_id: str
    order_type: str            # "limit" | "stop" | "market" (market for MOMENTUM setup)
    planned_entry: float
    initial_stop: float
    shares: int
    regime_at_entry: str | None = None
    sector: str | None = None
    sizing_method: str | None = None
    thesis: str | None = None

    def as_jsonable(self) -> dict:
        d = asdict(self)
        d["placed_date"] = self.placed_date.isoformat()
        return d


def parse_pending_line(line: str) -> PendingOrder | None:
    """Parse a single PENDING line. Returns None if it doesn't match.

    Required keys: order_id, type, entry, initial_stop, shares.
    Optional keys: regime_entry, sector, sizing, thesis.
    """
    m = PENDING_LINE_RE.match(line.strip())
    if not m:
        return None
    kv = _parse_kv_segment(m.group("kv"))
    thesis = None
    tm = re.search(r'thesis="([^"]*)"', line)
    if tm:
        thesis = tm.group(1)

    required = ("order_id", "type", "entry", "initial_stop", "shares")
    if not all(k in kv for k in required):
        return None

    try:
        return PendingOrder(
            symbol=m.group("sym").upper(),
            placed_date=date.fromisoformat(m.group("date")),
            order_id=kv["order_id"],
            order_type=kv["type"].lower(),
            planned_entry=_coerce_float(kv["entry"]),
            initial_stop=_coerce_float(kv["initial_stop"]),
            shares=int(kv["shares"]),
            regime_at_entry=kv.get("regime_entry"),
            sector=kv.get("sector"),
            sizing_method=kv.get("sizing"),
            thesis=thesis,
        )
    except (ValueError, KeyError):
        return None


def parse_pending_orders(text: str) -> list[PendingOrder]:
    """Parse all PENDING lines from a TRADE-LOG.md body.

    Returns PENDING orders that have NOT been promoted to OPEN or CLOSED
    (matched on symbol + order_id). A pending order is considered open until
    daily-summary writes either an OPEN line referencing the same order_id or
    explicitly drops it.
    """
    pendings: list[PendingOrder] = []
    promoted_order_ids: set[str] = set()
    for line in text.splitlines():
        po = parse_pending_line(line)
        if po is not None:
            pendings.append(po)
            continue
        # An OPEN line written by reconciliation may reference order_id; if
        # present, treat the PENDING as superseded. Same for CLOSED.
        for tag in ("OPEN", "CLOSED"):
            if line.lstrip().startswith(f"- {tag}"):
                om = re.search(r"order_id=(\S+)", line)
                if om:
                    promoted_order_ids.add(om.group(1))
                break
    return [p for p in pendings if p.order_id not in promoted_order_ids]


def load_pending_orders(path: Path | None = None) -> list[PendingOrder]:
    p = path or TRADE_LOG
    if not p.exists():
        return []
    return parse_pending_orders(p.read_text())


# ---------- R-multiple math (D1) ----------

def compute_r(entry: float, exit_: float, initial_stop: float) -> float:
    """R = (exit - entry) / (entry - initial_stop), assuming a long position.

    A losing trade hit at the initial stop yields R = -1.0 exactly.
    A 2:1 winner yields R = +2.0.
    """
    risk_per_share = entry - initial_stop
    if risk_per_share <= 0:
        raise ValueError(
            f"initial_stop {initial_stop} must be strictly below entry {entry} for a long"
        )
    return (exit_ - entry) / risk_per_share


# ---------- Aggregations (D1, D2, D3) ----------

@dataclass(frozen=True)
class Aggregates:
    n: int
    n_wins: int
    n_losses: int
    win_rate: float | None
    avg_r_win: float | None
    avg_r_loss: float | None
    payoff_ratio: float | None  # avg_r_win / |avg_r_loss|
    expectancy: float | None    # win_rate * avg_r_win - (1-win_rate) * |avg_r_loss|
    total_pnl: float
    sector_pnl: dict[str, float]
    regime_pnl: dict[str, float]
    regime_win_rate: dict[str, float]

    def as_dict(self) -> dict:
        return {
            "n": self.n,
            "n_wins": self.n_wins,
            "n_losses": self.n_losses,
            "win_rate": self.win_rate,
            "avg_r_win": self.avg_r_win,
            "avg_r_loss": self.avg_r_loss,
            "payoff_ratio": self.payoff_ratio,
            "expectancy": self.expectancy,
            "total_pnl": self.total_pnl,
            "sector_pnl": self.sector_pnl,
            "regime_pnl": self.regime_pnl,
            "regime_win_rate": self.regime_win_rate,
        }


def aggregate(trades: list[ClosedTrade]) -> Aggregates:
    """Compute D1/D2/D3 aggregates over a list of closed trades."""
    n = len(trades)
    if n == 0:
        return Aggregates(0, 0, 0, None, None, None, None, None, 0.0, {}, {}, {})

    wins = [t for t in trades if t.is_win]
    losses = [t for t in trades if not t.is_win]
    n_w, n_l = len(wins), len(losses)
    win_rate = n_w / n if n else None
    avg_r_win = sum(t.r_multiple for t in wins) / n_w if n_w else None
    avg_r_loss = sum(t.r_multiple for t in losses) / n_l if n_l else None
    payoff = None
    if avg_r_win is not None and avg_r_loss is not None and avg_r_loss != 0:
        payoff = avg_r_win / abs(avg_r_loss)
    expectancy = None
    if win_rate is not None and avg_r_win is not None and avg_r_loss is not None:
        expectancy = win_rate * avg_r_win - (1 - win_rate) * abs(avg_r_loss)

    sector_pnl: dict[str, float] = {}
    regime_pnl: dict[str, float] = {}
    regime_counts: dict[str, int] = {}
    regime_wins: dict[str, int] = {}
    for t in trades:
        if t.sector:
            sector_pnl[t.sector] = round(sector_pnl.get(t.sector, 0.0) + t.pnl, 2)
        if t.regime_at_entry:
            regime_pnl[t.regime_at_entry] = round(regime_pnl.get(t.regime_at_entry, 0.0) + t.pnl, 2)
            regime_counts[t.regime_at_entry] = regime_counts.get(t.regime_at_entry, 0) + 1
            if t.is_win:
                regime_wins[t.regime_at_entry] = regime_wins.get(t.regime_at_entry, 0) + 1

    regime_win_rate = {
        r: round(regime_wins.get(r, 0) / regime_counts[r], 4)
        for r in regime_counts
    }

    return Aggregates(
        n=n,
        n_wins=n_w,
        n_losses=n_l,
        win_rate=round(win_rate, 4) if win_rate is not None else None,
        avg_r_win=round(avg_r_win, 4) if avg_r_win is not None else None,
        avg_r_loss=round(avg_r_loss, 4) if avg_r_loss is not None else None,
        payoff_ratio=round(payoff, 4) if payoff is not None else None,
        expectancy=round(expectancy, 4) if expectancy is not None else None,
        total_pnl=round(sum(t.pnl for t in trades), 2),
        sector_pnl=sector_pnl,
        regime_pnl=regime_pnl,
        regime_win_rate=regime_win_rate,
    )


def aggregate_since(trades: list[ClosedTrade], since: date) -> Aggregates:
    return aggregate([t for t in trades if t.exit_date >= since])


# ---------- CLI ----------

def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    cmd = sys.argv[1]
    trades = load_closed_trades()

    if cmd == "list-closed":
        print(json.dumps([t.as_jsonable() for t in trades], indent=2))
    elif cmd == "list-pending":
        print(json.dumps([p.as_jsonable() for p in load_pending_orders()], indent=2))
    elif cmd == "stats":
        print(json.dumps(aggregate(trades).as_dict(), indent=2))
    elif cmd == "stats-since":
        if len(sys.argv) < 3:
            print("usage: stats-since YYYY-MM-DD", file=sys.stderr)
            return 2
        since = date.fromisoformat(sys.argv[2])
        print(json.dumps(aggregate_since(trades, since).as_dict(), indent=2))
    elif cmd == "count":
        print(len(trades))
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
