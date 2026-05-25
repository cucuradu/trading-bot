"""Reference implementation of the buy-side gate, mirroring memory/TRADING-STRATEGY.md.

Kept in tests/ rather than scripts/ because Claude (the bot) does the gating in
natural language during each routine — this module exists to UNIT-TEST that the
rules are unambiguous and the math is right. It is also imported by /trade as a
sanity check.

Checks (Phase A):
  - Universe membership (A7)             -> hard reject if not in TRADING_UNIVERSE
  - Lock file present (A1)               -> hard reject
  - Account daily-DD response (A1)       -> hard reject if freeze_entries_48h
  - Account weekly-DD response (A1)      -> hard reject if freeze_until_monday
  - Max correlation with existing (A3)   -> reject if > 0.70
  - Earnings blackout (A4)               -> reject if 0 < days_to_earnings < 5
                                            and catalyst_is_earnings is False
  - Existing rules: positions, weekly count, position %, cash, PDT, catalyst, stock
"""
from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

# scripts/universe.py is the single source of truth for TRADING_UNIVERSE.
_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
from universe import TRADING_UNIVERSE  # noqa: E402


MAX_POSITIONS = 6
MAX_WEEKLY_TRADES = 3
MAX_POSITION_PCT = 0.20
MAX_DAY_TRADE_COUNT = 3  # PDT room on sub-$25k accounts
MAX_CORRELATION_WITH_EXISTING = 0.70
EARNINGS_BLACKOUT_DAYS = 5
MAX_PER_SECTOR = 2  # Phase C finding: sector cap adds +5-6pp return, same trade count


@dataclass(frozen=True)
class AccountState:
    equity: float
    cash: float
    open_position_count: int
    weekly_trade_count: int
    day_trade_count: int
    # Phase A1 inputs — caller fills from scripts/risk_gates.py check output.
    lock_file_present: bool = False
    daily_dd_response: str = "none"   # "none" | "tighten_trails" | "freeze_entries_48h"
    weekly_dd_response: str = "none"  # "none" | "freeze_until_monday"


@dataclass(frozen=True)
class ProposedBuy:
    symbol: str
    shares: int
    ask_price: float
    catalyst_documented: bool
    is_stock: bool = True
    # Phase A3/A4 inputs — caller fills from scripts/market_data.py.
    # None means "not measured"; in production, the caller MUST populate these.
    max_correlation_with_existing: float | None = None
    days_to_earnings: int | None = None
    catalyst_is_earnings: bool = False
    # Phase C finding: sector concentration cap.
    # Caller populates from current Alpaca positions + scripts/universe.py sector_of().
    # None means "not measured"; in production, MUST populate.
    open_positions_in_same_sector: int | None = None


@dataclass(frozen=True)
class GateResult:
    allowed: bool
    failures: tuple[str, ...]


def check_buy(account: AccountState, trade: ProposedBuy) -> GateResult:
    failures: list[str] = []
    cost = trade.shares * trade.ask_price
    sym = trade.symbol.strip().upper()

    # A1 — system-level kill switches (checked first; they override everything)
    if account.lock_file_present:
        failures.append("LOCK file present — drawdown lock active, manual unlock required")

    if account.daily_dd_response == "freeze_entries_48h":
        failures.append("daily DD ≤ −3% → entries frozen 48h")

    if account.weekly_dd_response == "freeze_until_monday":
        failures.append("weekly DD ≤ −5% → entries frozen until next Monday")

    # A7 — universe filter
    if sym not in TRADING_UNIVERSE:
        failures.append(
            f"{sym} is not in TRADING_UNIVERSE (40-ticker whitelist) — see scripts/universe.py"
        )

    # Original rules
    if not trade.is_stock:
        failures.append("instrument is not a stock (NO OPTIONS rule)")

    if account.open_position_count + 1 > MAX_POSITIONS:
        failures.append(
            f"would exceed max positions ({account.open_position_count} + 1 > {MAX_POSITIONS})"
        )

    if account.weekly_trade_count + 1 > MAX_WEEKLY_TRADES:
        failures.append(
            f"would exceed weekly trade cap ({account.weekly_trade_count} + 1 > {MAX_WEEKLY_TRADES})"
        )

    if cost > account.equity * MAX_POSITION_PCT:
        failures.append(
            f"position cost ${cost:.2f} > {int(MAX_POSITION_PCT * 100)}% of equity (${account.equity * MAX_POSITION_PCT:.2f})"
        )

    if cost > account.cash:
        failures.append(f"position cost ${cost:.2f} > available cash ${account.cash:.2f}")

    if account.day_trade_count >= MAX_DAY_TRADE_COUNT:
        failures.append(
            f"day_trade_count {account.day_trade_count} >= {MAX_DAY_TRADE_COUNT} (PDT)"
        )

    if not trade.catalyst_documented:
        failures.append("no catalyst documented in today's RESEARCH-LOG")

    # A3 — correlation cap
    if trade.max_correlation_with_existing is not None:
        if trade.max_correlation_with_existing > MAX_CORRELATION_WITH_EXISTING:
            failures.append(
                f"max 30d correlation with existing positions "
                f"{trade.max_correlation_with_existing:.2f} > {MAX_CORRELATION_WITH_EXISTING:.2f}"
            )

    # A4 — earnings blackout
    if trade.days_to_earnings is not None and trade.days_to_earnings >= 0:
        if trade.days_to_earnings < EARNINGS_BLACKOUT_DAYS and not trade.catalyst_is_earnings:
            failures.append(
                f"earnings in {trade.days_to_earnings} day(s) "
                f"(< {EARNINGS_BLACKOUT_DAYS}d blackout) and catalyst is not earnings"
            )

    # Phase C — sector concentration cap (set after backtest sweep showed
    # +5-6pp / 2yr improvement vs uncapped baseline).
    if trade.open_positions_in_same_sector is not None:
        if trade.open_positions_in_same_sector >= MAX_PER_SECTOR:
            failures.append(
                f"already {trade.open_positions_in_same_sector} positions in this sector "
                f"(cap {MAX_PER_SECTOR})"
            )

    return GateResult(allowed=len(failures) == 0, failures=tuple(failures))
