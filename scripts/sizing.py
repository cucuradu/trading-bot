#!/usr/bin/env python3
"""Position sizing — flat 20% until N=30 closed trades, then Half-Kelly (Phase D4).

The switchover is automatic. Once `memory/TRADE-LOG.md` contains 30 canonical
CLOSED lines (see scripts/trade_log.py), the bot starts sizing each new entry
by Half-Kelly with regime modulation:

    f       = W - (1 - W) / R                  # Kelly fraction
    f_half  = max(0, f) * 0.5
    raw_pct = f_half * 100 * regime_factor
    size_pct = clamp(8.0, 20.0, raw_pct)

where:
  W = win_rate over all closed trades
  R = avg_R_win / |avg_R_loss|        (payoff ratio)
  regime_factor: Bull=1.0, Neutral=0.85, Caution=0.5, Defensive=0.0

Defensive blocks entries at the buy-gate, so the 0.0 factor is a defense in
depth — sizing should never be reached in that regime, but if it is, the
result floor is 8% (which the gate still rejects since entries_blocked=true).

Usage:
  python scripts/sizing.py recommend REGIME              # JSON; uses default 100k equity
  python scripts/sizing.py recommend REGIME EQUITY       # JSON: full sizing audit
  python scripts/sizing.py shares SIZE_DOLLARS ENTRY STOP EQUITY [RISK_CAP_PCT]
                                                         # B5: risk-capped share count
  python scripts/sizing.py method                        # "flat_20pct" or "half_kelly"
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path


_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
from trade_log import ClosedTrade, load_closed_trades  # noqa: E402


N_THRESHOLD = 30
FLOOR_PCT = 8.0
CAP_PCT = 20.0
KELLY_HALF_FACTOR = 0.5
# B5 (audit 2026-06-03): per-trade risk cap as % of equity. The 2026-06-03
# backtest sweep (REMEDIATION-FINDINGS.md, A3) showed 2.0% improves both return
# and drawdown vs flat-20% in 2024, 2025, combined, and both stress runs. Flat
# dollar sizing risked 2.9% on MU's 15% stop vs 1.5% on CAT's 8% stop; this
# equalizes per-trade $ risk by flooring the share count.
RISK_CAP_PCT = 2.0

REGIME_FACTORS: dict[str, float] = {
    "Bull": 1.0,
    "Neutral": 0.85,
    "Caution": 0.50,
    "Defensive": 0.0,
}


@dataclass(frozen=True)
class SizingResult:
    method: str                # "flat_20pct" | "half_kelly"
    size_pct: float            # final, clamped, regime-modulated
    n_closed: int
    regime: str
    regime_factor: float
    # Kelly internals (None when method == "flat_20pct")
    win_rate: float | None
    avg_r_win: float | None
    avg_r_loss: float | None
    payoff_ratio: float | None
    kelly_f: float | None
    half_kelly_raw_pct: float | None     # before regime modulation
    pre_clamp_pct: float | None          # after regime modulation, before floor/cap
    clamped: bool
    explanation: str

    def as_dict(self) -> dict:
        return asdict(self)


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def compute_size(regime: str, trades: list[ClosedTrade]) -> SizingResult:
    """Pure sizing decision — no I/O.

    Inputs:
      regime — one of {Bull, Neutral, Caution, Defensive} (others default to Neutral)
      trades — closed-trade list from scripts/trade_log.py

    Returns SizingResult with full audit trail.
    """
    n = len(trades)
    regime_factor = REGIME_FACTORS.get(regime, REGIME_FACTORS["Neutral"])

    if n < N_THRESHOLD:
        # Flat 20% — current behavior, no Kelly until we have enough data.
        return SizingResult(
            method="flat_20pct",
            size_pct=CAP_PCT,
            n_closed=n,
            regime=regime,
            regime_factor=regime_factor,
            win_rate=None,
            avg_r_win=None,
            avg_r_loss=None,
            payoff_ratio=None,
            kelly_f=None,
            half_kelly_raw_pct=None,
            pre_clamp_pct=None,
            clamped=False,
            explanation=f"N={n} < {N_THRESHOLD}: flat {CAP_PCT:.1f}% cap (Kelly disabled)",
        )

    wins = [t for t in trades if t.is_win]
    losses = [t for t in trades if not t.is_win]
    n_w, n_l = len(wins), len(losses)
    win_rate = n_w / n
    avg_r_win = sum(t.r_multiple for t in wins) / n_w if n_w else 0.0
    avg_r_loss = sum(t.r_multiple for t in losses) / n_l if n_l else 0.0

    # Degenerate cases: no wins or no losses → cannot compute Kelly safely.
    if n_w == 0 or n_l == 0 or avg_r_loss == 0:
        return SizingResult(
            method="half_kelly",
            size_pct=FLOOR_PCT,
            n_closed=n,
            regime=regime,
            regime_factor=regime_factor,
            win_rate=round(win_rate, 4),
            avg_r_win=round(avg_r_win, 4) if n_w else None,
            avg_r_loss=round(avg_r_loss, 4) if n_l else None,
            payoff_ratio=None,
            kelly_f=None,
            half_kelly_raw_pct=None,
            pre_clamp_pct=None,
            clamped=True,
            explanation=(
                f"degenerate sample (n_wins={n_w}, n_losses={n_l}); "
                f"defaulting to floor {FLOOR_PCT:.1f}%"
            ),
        )

    payoff = avg_r_win / abs(avg_r_loss)
    kelly_f = win_rate - (1 - win_rate) / payoff
    half_kelly_raw_pct = max(0.0, kelly_f) * KELLY_HALF_FACTOR * 100
    pre_clamp_pct = half_kelly_raw_pct * regime_factor
    size_pct = _clamp(pre_clamp_pct, FLOOR_PCT, CAP_PCT)
    clamped = (pre_clamp_pct != size_pct)

    return SizingResult(
        method="half_kelly",
        size_pct=round(size_pct, 4),
        n_closed=n,
        regime=regime,
        regime_factor=regime_factor,
        win_rate=round(win_rate, 4),
        avg_r_win=round(avg_r_win, 4),
        avg_r_loss=round(avg_r_loss, 4),
        payoff_ratio=round(payoff, 4),
        kelly_f=round(kelly_f, 4),
        half_kelly_raw_pct=round(half_kelly_raw_pct, 4),
        pre_clamp_pct=round(pre_clamp_pct, 4),
        clamped=clamped,
        explanation=(
            f"N={n} >= {N_THRESHOLD}: W={win_rate:.2%}, R={payoff:.2f}, "
            f"f={kelly_f:.4f}, half_kelly_raw={half_kelly_raw_pct:.2f}%, "
            f"regime={regime}({regime_factor:.2f}x), "
            f"final={size_pct:.2f}%"
            + (" [clamped]" if clamped else "")
        ),
    )


def recommended_size_pct(regime: str, equity: float | None = None,
                         trades: list[ClosedTrade] | None = None) -> dict:
    """Convenience wrapper: load closed trades from memory/TRADE-LOG.md and decide.

    Returns the SizingResult plus a derived `size_dollars` field (when equity is
    provided) so the caller can compute share count directly.
    """
    closed = trades if trades is not None else load_closed_trades()
    result = compute_size(regime, closed)
    out = result.as_dict()
    if equity is not None:
        out["equity"] = equity
        out["size_dollars"] = round(equity * result.size_pct / 100, 2)
    return out


def risk_capped_shares(size_dollars: float, entry_price: float, stop_price: float,
                       equity: float, risk_cap_pct: float = RISK_CAP_PCT) -> dict:
    """B5 — final share count = min(sizing-dollar count, per-trade-risk count).

    The risk count is floor(risk_cap_pct%·equity / (entry − stop)), so a wide-ATR
    stop shrinks the position to hold per-trade $ risk at the cap. Returns a full
    audit so the routine can log which bound applied.
    """
    if entry_price <= 0:
        return {"shares": 0, "bound": "invalid_price", "risk_cap_pct": risk_cap_pct}
    flat_shares = int(size_dollars // entry_price)
    per_share_risk = entry_price - stop_price
    risk_cap_shares: int | None = None
    bound = "size"
    shares = flat_shares
    if per_share_risk > 0:
        risk_cap_shares = int((risk_cap_pct / 100 * equity) // per_share_risk)
        if risk_cap_shares < flat_shares:
            shares = risk_cap_shares
            bound = "risk_cap"
    shares = max(0, shares)
    risk_dollars = round(shares * per_share_risk, 2) if per_share_risk > 0 else None
    return {
        "shares": shares,
        "flat_shares": flat_shares,
        "risk_cap_shares": risk_cap_shares,
        "per_share_risk": round(per_share_risk, 4),
        "risk_dollars": risk_dollars,
        "risk_pct_of_equity": round(100 * risk_dollars / equity, 3) if risk_dollars and equity else None,
        "risk_cap_pct": risk_cap_pct,
        "bound": bound,
    }


def _detect_current_method() -> str:
    return "half_kelly" if len(load_closed_trades()) >= N_THRESHOLD else "flat_20pct"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    cmd = sys.argv[1]
    if cmd == "method":
        print(_detect_current_method())
        return 0

    if cmd == "recommend":
        if len(sys.argv) < 3:
            print("usage: recommend REGIME [EQUITY]", file=sys.stderr)
            return 2
        regime = sys.argv[2]
        equity = float(sys.argv[3]) if len(sys.argv) >= 4 else None
        print(json.dumps(recommended_size_pct(regime, equity), indent=2))
        return 0

    if cmd == "shares":
        # B5: apply the per-trade risk cap on top of the sizing-dollar count.
        if len(sys.argv) < 6:
            print("usage: shares SIZE_DOLLARS ENTRY STOP EQUITY [RISK_CAP_PCT]", file=sys.stderr)
            return 2
        size_dollars, entry, stop, equity = (float(sys.argv[i]) for i in range(2, 6))
        cap = float(sys.argv[6]) if len(sys.argv) >= 7 else RISK_CAP_PCT
        print(json.dumps(risk_capped_shares(size_dollars, entry, stop, equity, cap), indent=2))
        return 0

    print(f"unknown command: {cmd}", file=sys.stderr)
    print(__doc__, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
