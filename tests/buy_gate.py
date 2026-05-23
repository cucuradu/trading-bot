"""Reference implementation of the buy-side gate, mirroring memory/TRADING-STRATEGY.md.

Kept in tests/ rather than scripts/ because Claude (the bot) does the gating in
natural language during each routine — this module exists to UNIT-TEST that the
rules are unambiguous and the math is right. It is also imported by /trade as a
sanity check.
"""
from __future__ import annotations

from dataclasses import dataclass


MAX_POSITIONS = 6
MAX_WEEKLY_TRADES = 3
MAX_POSITION_PCT = 0.20
MAX_DAY_TRADE_COUNT = 3  # PDT room on sub-$25k accounts


@dataclass(frozen=True)
class AccountState:
    equity: float
    cash: float
    open_position_count: int
    weekly_trade_count: int
    day_trade_count: int


@dataclass(frozen=True)
class ProposedBuy:
    symbol: str
    shares: int
    ask_price: float
    catalyst_documented: bool
    is_stock: bool = True


@dataclass(frozen=True)
class GateResult:
    allowed: bool
    failures: tuple[str, ...]


def check_buy(account: AccountState, trade: ProposedBuy) -> GateResult:
    failures: list[str] = []
    cost = trade.shares * trade.ask_price

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

    return GateResult(allowed=len(failures) == 0, failures=tuple(failures))
