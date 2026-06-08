#!/usr/bin/env python3
"""Safe trailing-stop tighten helper.

The daily-DD -2% gate tells the routine to "tighten trails by 30%". The routine
implements that by cancelling the live trailing stop and placing a fresh one.
But a *fresh* trailing stop resets its high-water mark to the CURRENT price, so a
smaller trail % off a lower HWM can produce an absolute stop BELOW the existing
one — silently violating "never move a stop down" and INCREASING downside on a
drawdown day. (2026-06-05: AMD 12.6%->8.82% moved the stop $477.53 -> $435.72.)

This helper does the arithmetic so the agent can't get it wrong. Given the
existing live stop price, the current price, and the proposed tighter trail %,
it returns the only safe action — never one that lowers protection or sits
within 3% of price.

Usage:
  python scripts/trail_tighten.py safe-stop --old-stop S --current C --new-pct P
"""
from __future__ import annotations

import argparse
import json
import sys

MIN_GAP_PCT = 3.0  # strategy: never place a stop within 3% of current price


def safe_stop(old_stop: float, current: float, new_pct: float) -> dict:
    band = current * (1 - MIN_GAP_PCT / 100)          # tightest compliant resting stop
    fresh = current * (1 - new_pct / 100)             # what cancel+replace would produce
    out = {
        "old_stop": round(old_stop, 2),
        "current": round(current, 2),
        "new_trail_pct": new_pct,
        "fresh_replace_stop": round(fresh, 2),
        "min_gap_floor": round(band, 2),
    }
    if old_stop > band:
        # Position is at/through its existing stop; any compliant resting stop
        # would be below old_stop, so a re-placed trail can only LOWER protection.
        # User policy (2026-06-08): auto-hold and clamp to the tightest compliant
        # stop (the 3% band) — never lower, never silently exit.
        out["action"] = "repair_to_band"
        out["repair_stop"] = round(band, 2)
        out["reason"] = (f"position is at/through its stop (${old_stop:.2f} > "
                         f"{MIN_GAP_PCT:.0f}% band ${band:.2f}); a re-placed trail would only "
                         f"LOWER protection — auto-hold and clamp to a fixed stop at the band "
                         f"${band:.2f} (user policy 2026-06-08), never lower")
    elif fresh < old_stop:
        out["action"] = "keep_existing"
        out["reason"] = (f"a fresh {new_pct}% trail off ${current:.2f} = ${fresh:.2f} "
                         f"is BELOW the live stop ${old_stop:.2f}; replacing would move "
                         "the stop down — keep the existing (higher) stop")
    elif fresh > band:
        out["action"] = "keep_existing"
        out["reason"] = (f"a fresh {new_pct}% trail = ${fresh:.2f} sits within "
                         f"{MIN_GAP_PCT:.0f}% of price (> ${band:.2f}); too tight — "
                         "keep the existing stop")
    else:
        out["action"] = "replace_trailing"
        out["expected_stop"] = round(fresh, 2)
        out["reason"] = (f"safe: fresh stop ${fresh:.2f} ≥ live ${old_stop:.2f} and "
                         f"≤ {MIN_GAP_PCT:.0f}% band ${band:.2f}")
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="trail_tighten.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("safe-stop", help="compute the never-lower tightened stop action")
    s.add_argument("--old-stop", type=float, required=True,
                   help="stop_price of the existing live trailing stop")
    s.add_argument("--current", type=float, required=True, help="current price")
    s.add_argument("--new-pct", type=float, required=True,
                   help="proposed (tighter) trail percent")
    args = p.parse_args(argv)
    print(json.dumps(safe_stop(args.old_stop, args.current, args.new_pct), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
