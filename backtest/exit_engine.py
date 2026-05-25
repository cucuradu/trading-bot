"""Exit strategies for the walk-forward backtest.

Three variants implement a common interface so the engine can swap them:
  - FixedTrail     : flat trail_percent (legacy 10% rule, baseline)
  - ATRTrail       : 2.5 × ATR(14), clamped to [7%, 15%] (Phase A2 production rule)
  - ChandelierTrail: high_since_entry − 3 × ATR(22) (tutorial-style alt)

Each strategy implements:
  - on_entry(pos, bar)  -> initial_stop_price
  - on_bar(pos, bar)    -> ExitDecision  (close yes/no, why, new stop level)

The engine layers OTHER rules on top of the strategy decision:
  - hard cut when close ≤ initial_stop (R ≤ −1; phase-C change from fixed −7%)
  - profit tightening at +15%/+20% (strategy may override)
  - time stop after 10 trading days flat (always)
  - regime override (close winners in Defensive regime — orchestrated upstream)

These layered rules live in `apply_post_strategy_rules` so they're testable
independently of the underlying trailing-stop variant.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Protocol


# --- Constants (mirror memory/TRADING-STRATEGY.md) ---

TIME_STOP_DAYS = 10
TIME_STOP_BAND = (-3.0, 3.0)

PROFIT_TIGHTEN_1_THRESHOLD = 15.0   # at +15%, tighten to 7%
PROFIT_TIGHTEN_1_PCT = 7.0
PROFIT_TIGHTEN_2_THRESHOLD = 20.0   # at +20%, tighten to 5%
PROFIT_TIGHTEN_2_PCT = 5.0

ATR_STOP_MULTIPLIER = 2.5
ATR_TIGHTEN_1 = 1.75   # at +15%
ATR_TIGHTEN_2 = 1.25   # at +20%
ATR_FLOOR_PCT = 7.0
ATR_CAP_PCT = 15.0

CHANDELIER_ATR_PERIOD = 22
CHANDELIER_MULT = 3.0


@dataclass
class Position:
    """A single open position in the backtest engine.

    Mutable: peak_close, current_stop_pct, current_stop_price update as bars
    arrive. Entry-time fields (entry_date, entry_price, initial_stop) NEVER
    change — R-multiple math depends on the original initial_stop.
    """
    symbol: str
    entry_date: date
    entry_price: float
    initial_stop: float
    shares: int
    sector: str
    regime_at_entry: str
    sizing_method: str
    current_stop_pct: float = 0.0
    current_stop_price: float = 0.0
    peak_close: float = 0.0
    bars_held: int = 0


@dataclass
class ExitDecision:
    close: bool
    exit_price: float | None = None
    reason: str | None = None
    new_stop_pct: float | None = None
    new_stop_price: float | None = None


# ---------- Helpers ----------

def unrealized_pct(pos: Position, last_price: float) -> float:
    if pos.entry_price <= 0:
        return 0.0
    return (last_price - pos.entry_price) / pos.entry_price * 100


def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


# ---------- Strategy interface ----------

class ExitStrategy(Protocol):
    name: str

    def initial_stop(self, entry_price: float, atr_at_entry: float | None) -> tuple[float, float]:
        """Return (stop_pct, stop_price) at entry time."""
        ...

    def update_trail(self, pos: Position, bar_high: float, bar_low: float,
                     bar_close: float, atr_now: float | None) -> tuple[float, float]:
        """Return updated (stop_pct, stop_price) given the current bar.

        Implementations must never move a stop DOWN (anti-whipsaw rule).
        """
        ...


@dataclass
class FixedTrail:
    """Legacy 10% trailing stop. No ATR awareness."""
    name: str = "fixed_10"
    trail_pct: float = 10.0

    def initial_stop(self, entry_price: float, atr_at_entry: float | None) -> tuple[float, float]:
        stop_price = entry_price * (1 - self.trail_pct / 100)
        return self.trail_pct, stop_price

    def update_trail(self, pos: Position, bar_high: float, bar_low: float,
                     bar_close: float, atr_now: float | None) -> tuple[float, float]:
        # Use peak_close to anchor the trail (consistent with Alpaca trailing_stop semantics).
        new_anchor = max(pos.peak_close, bar_close)
        new_stop_price = new_anchor * (1 - pos.current_stop_pct / 100)
        # Never move the stop down.
        new_stop_price = max(pos.current_stop_price, new_stop_price)
        return pos.current_stop_pct, new_stop_price


@dataclass
class ATRTrail:
    """Phase A2 production trail: 2.5 × ATR(14), clamped [7%, 15%]."""
    name: str = "atr_2_5x"
    multiplier: float = ATR_STOP_MULTIPLIER
    floor_pct: float = ATR_FLOOR_PCT
    cap_pct: float = ATR_CAP_PCT

    def initial_stop(self, entry_price: float, atr_at_entry: float | None) -> tuple[float, float]:
        if atr_at_entry is None or atr_at_entry <= 0:
            # No ATR available — fall back to floor.
            stop_pct = self.floor_pct
        else:
            raw = (self.multiplier * atr_at_entry / entry_price) * 100
            stop_pct = _clamp(raw, self.floor_pct, self.cap_pct)
        stop_price = entry_price * (1 - stop_pct / 100)
        return stop_pct, stop_price

    def update_trail(self, pos: Position, bar_high: float, bar_low: float,
                     bar_close: float, atr_now: float | None) -> tuple[float, float]:
        new_anchor = max(pos.peak_close, bar_close)
        new_stop_price = new_anchor * (1 - pos.current_stop_pct / 100)
        new_stop_price = max(pos.current_stop_price, new_stop_price)
        return pos.current_stop_pct, new_stop_price


@dataclass
class ChandelierTrail:
    """Tutorial-style: stop = highest_high_since_entry − 3 × ATR(22).

    Tracks the trail level directly (not a percent), so it adapts to expanding
    volatility differently from the ATR percentage approach.
    """
    name: str = "chandelier_3xATR22"
    multiplier: float = CHANDELIER_MULT
    floor_pct: float = ATR_FLOOR_PCT
    cap_pct: float = ATR_CAP_PCT
    _peak_high: float = field(default=0.0)

    def initial_stop(self, entry_price: float, atr_at_entry: float | None) -> tuple[float, float]:
        if atr_at_entry is None or atr_at_entry <= 0:
            stop_pct = self.floor_pct
            stop_price = entry_price * (1 - stop_pct / 100)
        else:
            stop_price = entry_price - self.multiplier * atr_at_entry
            stop_pct = (entry_price - stop_price) / entry_price * 100
            stop_pct = _clamp(stop_pct, self.floor_pct, self.cap_pct)
            stop_price = entry_price * (1 - stop_pct / 100)
        # Reset per-position peak tracking (each Chandelier instance is shared
        # across positions in the engine, so we use pos.peak_close instead of
        # internal state in update_trail).
        return stop_pct, stop_price

    def update_trail(self, pos: Position, bar_high: float, bar_low: float,
                     bar_close: float, atr_now: float | None) -> tuple[float, float]:
        # Anchor on highest HIGH since entry, not close — the canonical Chandelier rule.
        # We piggy-back pos.peak_close to also track the peak high.
        new_anchor = max(pos.peak_close, bar_high)
        if atr_now is None or atr_now <= 0:
            new_stop_price = new_anchor * (1 - pos.current_stop_pct / 100)
        else:
            raw_stop = new_anchor - self.multiplier * atr_now
            stop_pct_from_anchor = (new_anchor - raw_stop) / new_anchor * 100
            stop_pct_from_anchor = _clamp(stop_pct_from_anchor, self.floor_pct, self.cap_pct)
            new_stop_price = new_anchor * (1 - stop_pct_from_anchor / 100)
        new_stop_price = max(pos.current_stop_price, new_stop_price)
        return pos.current_stop_pct, new_stop_price


# ---------- Post-strategy rule layer ----------

def apply_post_strategy_rules(pos: Position, bar_high: float, bar_low: float,
                              bar_close: float, market_regime: str,
                              strategy: ExitStrategy,
                              atr_now: float | None = None,
                              *,
                              time_stop_days: int = TIME_STOP_DAYS,
                              time_stop_band: tuple[float, float] = TIME_STOP_BAND,
                              ) -> ExitDecision:
    """Apply ALL exit rules on a new bar, in priority order.

    Priority:
      1. Trailing stop hit (intra-bar low <= current_stop_price)
      2. Hard cut when bar_close <= initial_stop (R <= -1 — phase-C change
         from fixed -7%; lets wider ATR stops take full planned risk)
      3. Time stop (default: 10 trading days flat, ±3%)
      4. Regime override (Defensive → close winners, hold losers' stops)
      5. Profit tighten (no close, just stop adjustment)
      6. Trail update via the active strategy (no close)

    The thresholds are tunable so the backtest sensitivity sweep can vary them
    without touching production constants. Defaults match TRADING-STRATEGY.md.
    """
    # 1. Trailing stop hit during the bar?
    if bar_low <= pos.current_stop_price:
        return ExitDecision(
            close=True,
            exit_price=pos.current_stop_price,
            reason="trailing_stop",
        )

    pct = unrealized_pct(pos, bar_close)

    # 2. Hard cut when bar_close <= initial_stop (R <= -1). Previously fixed -7%,
    #    which conflicted with ATR-sized wider stops by cutting positions short
    #    of the risk they were sized for. Phase C change.
    if bar_close <= pos.initial_stop:
        return ExitDecision(close=True, exit_price=bar_close, reason="hard_cut")

    # 3. Time stop.
    if pos.bars_held >= time_stop_days and time_stop_band[0] <= pct <= time_stop_band[1]:
        return ExitDecision(close=True, exit_price=bar_close, reason="time_stop")

    # 4. Regime override — close in Defensive only if the position is in profit.
    if market_regime == "Defensive" and pct > 0:
        return ExitDecision(close=True, exit_price=bar_close, reason="regime_defensive")

    # 5. Profit-tighten — never move stop down.
    new_stop_pct = pos.current_stop_pct
    if pct >= PROFIT_TIGHTEN_2_THRESHOLD:
        if isinstance(strategy, ATRTrail) and atr_now is not None and atr_now > 0:
            atr_pct_now = atr_now / bar_close * 100
            new_stop_pct = max(PROFIT_TIGHTEN_2_PCT, atr_pct_now * ATR_TIGHTEN_2)
        else:
            new_stop_pct = min(pos.current_stop_pct, PROFIT_TIGHTEN_2_PCT)
    elif pct >= PROFIT_TIGHTEN_1_THRESHOLD:
        if isinstance(strategy, ATRTrail) and atr_now is not None and atr_now > 0:
            atr_pct_now = atr_now / bar_close * 100
            new_stop_pct = max(PROFIT_TIGHTEN_1_PCT, atr_pct_now * ATR_TIGHTEN_1)
        else:
            new_stop_pct = min(pos.current_stop_pct, PROFIT_TIGHTEN_1_PCT)

    # If we tightened, recompute stop price from current peak.
    if new_stop_pct != pos.current_stop_pct:
        # Take a snapshot Position with the new pct, then re-trail.
        # We must never widen — only shrink toward current price.
        anchor = max(pos.peak_close, bar_close)
        tighter_stop_price = anchor * (1 - new_stop_pct / 100)
        # Don't move down even when tightening.
        tighter_stop_price = max(pos.current_stop_price, tighter_stop_price)
        return ExitDecision(
            close=False,
            new_stop_pct=new_stop_pct,
            new_stop_price=tighter_stop_price,
            reason="profit_tighten",
        )

    # 6. Default trail update via the strategy.
    new_pct, new_price = strategy.update_trail(pos, bar_high, bar_low, bar_close, atr_now)
    if new_price != pos.current_stop_price:
        return ExitDecision(
            close=False,
            new_stop_pct=new_pct,
            new_stop_price=new_price,
            reason="trail_update",
        )
    return ExitDecision(close=False, reason="hold")


# ---------- Strategy registry ----------

STRATEGIES: dict[str, type[ExitStrategy]] = {
    "fixed_10": FixedTrail,
    "atr_2_5x": ATRTrail,
    "chandelier_3xATR22": ChandelierTrail,
}


def get_strategy(name: str) -> ExitStrategy:
    if name not in STRATEGIES:
        raise ValueError(f"unknown exit strategy '{name}'. Available: {sorted(STRATEGIES)}")
    return STRATEGIES[name]()
