#!/usr/bin/env python3
"""Pre-open gap guard (Phase G3).

Market-open's STEP 3 calls this once per candidate to decide whether to:
  - SKIP the entry (gap up too far past plan → adds chase risk)
  - PROCEED at the planned price (gap is within tolerance)
  - PROCEED_LOWER at the current ask + recompute stop (price gapped DOWN
    past the plan, so the planned limit would be stale and the realized
    ATR% widened)

Default tolerance: 3% in either direction. Configurable for backtest.

Usage:
  python scripts/gap_guard.py evaluate PLANNED CURRENT
  python scripts/gap_guard.py evaluate 138.50 145.10
  # → {"action": "skip", "ratio": 1.0477, "reason": "gap_above_plan ..."}
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass


DEFAULT_TOLERANCE = 0.03


@dataclass(frozen=True)
class GapDecision:
    action: str          # "skip" | "proceed" | "proceed_lower"
    ratio: float         # current / planned
    reason: str

    def as_dict(self) -> dict:
        return {"action": self.action, "ratio": round(self.ratio, 4), "reason": self.reason}


def evaluate(planned: float, current: float, tolerance: float = DEFAULT_TOLERANCE) -> GapDecision:
    """Decide whether a candidate's planned entry is still actionable.

    `planned` is the entry price from the pre-market RESEARCH-LOG block.
    `current` is the most recent ask from `scripts/alpaca.sh quote SYM` at
    market-open. `tolerance` is the symmetric +/- gap threshold (default 3%).
    """
    if planned <= 0:
        raise ValueError(f"planned must be positive, got {planned!r}")
    if current <= 0:
        raise ValueError(f"current must be positive, got {current!r}")
    if not (0 < tolerance < 1):
        raise ValueError(f"tolerance must be in (0, 1), got {tolerance!r}")

    ratio = current / planned
    upper = 1.0 + tolerance
    lower = 1.0 - tolerance
    if ratio > upper:
        return GapDecision(
            action="skip",
            ratio=ratio,
            reason=f"gap_above_plan current={current:.2f} planned={planned:.2f} ratio={ratio:.4f}",
        )
    if ratio < lower:
        return GapDecision(
            action="proceed_lower",
            ratio=ratio,
            reason=(
                f"gap_below_plan current={current:.2f} planned={planned:.2f} ratio={ratio:.4f}; "
                "place limit at current ask and recompute stop_pct"
            ),
        )
    return GapDecision(
        action="proceed",
        ratio=ratio,
        reason=f"within_tolerance ratio={ratio:.4f} tolerance={tolerance:.4f}",
    )


def main() -> int:
    p = argparse.ArgumentParser(prog="gap_guard.py", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sp = sub.add_parser("evaluate", help="decide skip / proceed / proceed_lower")
    sp.add_argument("planned", type=float, help="planned entry from RESEARCH-LOG")
    sp.add_argument("current", type=float, help="current ask from alpaca quote")
    sp.add_argument("--tolerance", type=float, default=DEFAULT_TOLERANCE,
                    help=f"symmetric gap tolerance (default {DEFAULT_TOLERANCE})")
    args = p.parse_args()
    if args.cmd == "evaluate":
        d = evaluate(args.planned, args.current, args.tolerance)
        print(json.dumps(d.as_dict(), indent=2))
        return 0 if d.action != "skip" else 0  # exit 0 in all cases; consumer parses JSON
    return 1


if __name__ == "__main__":
    sys.exit(main())
