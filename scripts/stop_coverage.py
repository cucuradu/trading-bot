#!/usr/bin/env python3
"""Protective-stop coverage check (B1 — naked-position guard).

Every open long position MUST be covered by a live protective sell order
(trailing_stop / stop / stop_limit) for its full share count. The OTO child
that market-open arms on entry can silently fail to register (real incident
2026-06-01: AMD + CAT carried overnight with no stop visible in Alpaca). No
routine verified this — daily-summary STEP 3b assumed the child armed. This
detector surfaces any position whose stop coverage is missing or short so the
routine can re-place it.

Detection only — placing/cancelling orders stays in the routines so every
trading action goes through scripts/alpaca.sh and its live-trading failsafe.

Usage:
  python scripts/stop_coverage.py check
      Shells out to `bash scripts/alpaca.sh positions` and `... orders`.
  python scripts/stop_coverage.py check --positions P.json --orders O.json
      Read from files instead (offline / unit tests).

Output (JSON):
  {
    "covered": bool,                 # true iff every long position is fully covered
    "positions_checked": N,
    "naked": [
      {"symbol", "position_qty", "covered_qty", "shortfall", "stop_order_ids"}
    ]
  }
Exit code 0 always (parse the JSON); the routine decides what to do.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent

# Alpaca order types that protect a long position.
PROTECTIVE_TYPES = {"trailing_stop", "stop", "stop_limit"}


def _alpaca(subcmd: str) -> list:
    """Call the alpaca.sh wrapper and parse its JSON array output."""
    out = subprocess.run(
        ["bash", str(_HERE / "alpaca.sh"), subcmd],
        capture_output=True, text=True, check=True,
    ).stdout
    data = json.loads(out) if out.strip() else []
    return data if isinstance(data, list) else [data]


def _load(path: str | None, subcmd: str) -> list:
    if path:
        data = json.loads(Path(path).read_text())
        return data if isinstance(data, list) else [data]
    return _alpaca(subcmd)


def _order_type(order: dict) -> str:
    # Alpaca returns both `order_type` and the legacy `type`; prefer order_type.
    return str(order.get("order_type") or order.get("type") or "").lower()


def _num(x) -> float:
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def coverage(positions: list, orders: list) -> dict:
    """Pure coverage computation — no I/O. Long positions only (bot never shorts)."""
    # Sum protective sell-order qty per symbol.
    stop_qty: dict[str, float] = {}
    stop_ids: dict[str, list[str]] = {}
    for o in orders:
        if str(o.get("side", "")).lower() != "sell":
            continue
        if _order_type(o) not in PROTECTIVE_TYPES:
            continue
        sym = str(o.get("symbol", "")).upper()
        if not sym:
            continue
        stop_qty[sym] = stop_qty.get(sym, 0.0) + _num(o.get("qty"))
        stop_ids.setdefault(sym, []).append(str(o.get("id", "")))

    naked: list[dict] = []
    checked = 0
    for p in positions:
        sym = str(p.get("symbol", "")).upper()
        qty = _num(p.get("qty"))
        if not sym or qty <= 0:  # skip flat / short (long-only strategy)
            continue
        checked += 1
        covered = stop_qty.get(sym, 0.0)
        if covered + 1e-9 < qty:
            naked.append({
                "symbol": sym,
                "position_qty": qty,
                "covered_qty": covered,
                "shortfall": round(qty - covered, 6),
                "stop_order_ids": stop_ids.get(sym, []),
            })

    return {
        "covered": len(naked) == 0,
        "positions_checked": checked,
        "naked": naked,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="stop_coverage.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    chk = sub.add_parser("check", help="report any long position lacking full stop coverage")
    chk.add_argument("--positions", help="positions JSON file (default: live via alpaca.sh)")
    chk.add_argument("--orders", help="open-orders JSON file (default: live via alpaca.sh)")
    args = p.parse_args(argv if argv is not None else sys.argv[1:])

    positions = _load(args.positions, "positions")
    orders = _load(args.orders, "orders")
    print(json.dumps(coverage(positions, orders), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
