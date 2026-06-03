"""Walk-forward backtest orchestrator.

Loops over trading days, asks the entry simulator what to open, applies all
exit rules to existing positions, and tracks an equity curve. Reuses the
production-side regime classifier and ATR computation so the backtest
exercises the SAME math the live bot will.

Public API:
  BacktestConfig — knobs (window, equity, max positions, fees, etc.)
  BacktestResult — populated by run()
  Engine.run(config) -> BacktestResult
"""
from __future__ import annotations

import math
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

# Reuse production modules.
_HERE = Path(__file__).resolve().parent
_SCRIPTS = _HERE.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(_HERE))

import regime as rg  # noqa: E402
from market_data import compute_atr  # noqa: E402
from universe import sector_of  # noqa: E402

from entry_simulator import EntryIntent  # noqa: E402
from exit_engine import (  # noqa: E402
    ExitStrategy, FixedTrail, Position, apply_post_strategy_rules,
    get_strategy, unrealized_pct,
)


@dataclass
class _PendingOrder:
    """In-engine bookkeeping for an unfilled EntryIntent (Phase G)."""
    intent: EntryIntent
    bars_remaining: int


@dataclass
class BacktestConfig:
    start: date
    end: date
    starting_equity: float = 100_000.0
    max_positions: int = 6
    max_position_pct: float = 0.20
    # Production rule (buy_gate.MAX_PER_SECTOR=2). The Phase C sweep proved this
    # adds +5-6pp vs an uncapped baseline at the same trade frequency.
    max_per_sector: int = 2
    exit_strategy: str = "atr_2_5x"   # key in exit_engine.STRATEGIES
    apply_circuit_breakers: bool = True   # account-level DD gates
    apply_regime_gating: bool = True      # block entries in Defensive, etc.
    apply_stress_shocks: bool = False     # C4 — see backtest.stress
    stress_shock_prob: float = 0.015      # probability per bar
    stress_shock_range: tuple[float, float] = (-0.15, -0.10)
    stress_seed: int = 42
    fee_per_trade: float = 0.0
    slippage_pct: float = 0.0
    # Exit-rule overrides (default to TRADING-STRATEGY.md values).
    time_stop_days: int = 10
    time_stop_band: tuple[float, float] = (-3.0, 3.0)
    # ---- Realism toggles (audit 2026-05-29) ----
    # All default False → legacy behavior, so existing reports/tests are
    # unchanged. Turn on to model the live rules the bot actually trades under.
    enforce_cash_cap: bool = False            # #1: no leverage; deployed cost basis <= cash
    respect_deployment_target: bool = False   # #1b: also cap at the regime deployment_target
    enforce_entry_caps: bool = False          # #2: regime trade_slots + N new trades / week
    max_new_trades_per_week: int = 3
    enforce_regime_persistence: bool = False  # #3: regime must persist >=3 bars before posture change
    stop_gap_fill: bool = False               # #4: gap-down stops fill at the open, not the stop price
    # ---- Remediation knobs (audit 2026-06-03) ----
    # All default None/off → legacy behavior; existing reports/tests unchanged.
    risk_cap_pct: float | None = None         # A3: floor share count so per-trade risk <= this fraction of equity
    max_sector_deployment_pct: float | None = None  # A2: cap total cost basis per sector ETF (BROAD exempt)
    min_rr_at_entry: float | None = None      # A4: skip entries whose proxy R:R falls below this
    rr_target_pct: float = 0.20               # A4 proxy target = entry × (1 + rr_target_pct)


@dataclass
class ClosedTradeRecord:
    symbol: str
    entry_date: date
    exit_date: date
    entry_price: float
    exit_price: float
    initial_stop: float
    shares: int
    pnl: float
    r_multiple: float
    sector: str
    regime_at_entry: str
    exit_reason: str

    def as_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "entry_date": self.entry_date.isoformat(),
            "exit_date": self.exit_date.isoformat(),
            "entry_price": round(self.entry_price, 4),
            "exit_price": round(self.exit_price, 4),
            "initial_stop": round(self.initial_stop, 4),
            "shares": self.shares,
            "pnl": round(self.pnl, 2),
            "r_multiple": round(self.r_multiple, 4),
            "sector": self.sector,
            "regime_at_entry": self.regime_at_entry,
            "exit_reason": self.exit_reason,
        }


@dataclass
class BacktestResult:
    config: BacktestConfig
    trades: list[ClosedTradeRecord] = field(default_factory=list)
    equity_curve: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    regime_history: list[tuple[date, str]] = field(default_factory=list)
    lock_triggered: bool = False
    final_equity: float = 0.0
    peak_equity: float = 0.0


# ---------- Indicator pre-compute ----------

def _precompute_indicators(bars: dict[str, pd.DataFrame], period: int = 14) -> dict[str, pd.DataFrame]:
    """Augment each symbol's DataFrame with rolling ATR + SMA columns.

    Columns added:
      atr_14  : Wilder's ATR
      sma_50  : 50-day SMA
      sma_200 : 200-day SMA
      ret_10  : 10-day percent return
      ret_20  : 20-day percent return
    """
    out: dict[str, pd.DataFrame] = {}
    for sym, df in bars.items():
        if df.empty or len(df) < 30:
            continue
        df = df.copy()
        high = df["High"].astype(float)
        low = df["Low"].astype(float)
        close = df["Close"].astype(float)
        prev_close = close.shift(1)
        tr = pd.concat(
            [(high - low), (high - prev_close).abs(), (low - prev_close).abs()],
            axis=1,
        ).max(axis=1)
        df["atr_14"] = tr.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()
        df["sma_50"] = close.rolling(window=50).mean()
        df["sma_200"] = close.rolling(window=200).mean()
        df["ret_10"] = close.pct_change(10) * 100
        df["ret_20"] = close.pct_change(20) * 100
        out[sym] = df
    return out


# ---------- Regime classification on a given bar ----------

def _classify_regime_on(date_idx: pd.Timestamp,
                        spy: pd.DataFrame,
                        vix: pd.DataFrame) -> str:
    """Use the production rule-based classifier on historical SPY + VIX."""
    if date_idx not in spy.index:
        return "Neutral"
    spy_close = float(spy.at[date_idx, "Close"])
    spy_sma = float(spy.at[date_idx, "sma_200"]) if not pd.isna(spy.at[date_idx, "sma_200"]) else spy_close
    spy_20d = float(spy.at[date_idx, "ret_20"]) if not pd.isna(spy.at[date_idx, "ret_20"]) else 0.0
    # Find the most recent VIX value at or before date_idx.
    vix_subset = vix[vix.index <= date_idx]
    if vix_subset.empty:
        return "Neutral"
    vix_close = float(vix_subset["Close"].iloc[-1])
    return rg.classify_market(vix_close, spy_close, spy_sma, spy_20d)


# ---------- Remediation sizing/entry helpers (audit 2026-06-03) ----------

def _sized_shares(equity: float, max_position_pct: float, fill_price: float,
                  entry_basis: float, stop_price: float,
                  risk_cap_pct: float | None) -> int:
    """Flat-% share count, optionally floored by a per-trade risk cap (A3).

    Flat sizing risks more on wide-ATR names (MU's 15% stop risked ~2x CAT's 8%
    stop at the same 20% dollar size). The risk cap equalizes per-trade $ risk:
    shares = min(20%-dollars / price, risk_cap%·equity / per-share-risk).
    """
    if fill_price <= 0:
        return 0
    shares = int(math.floor(equity * max_position_pct / fill_price))
    if risk_cap_pct is not None:
        per_share_risk = entry_basis - stop_price
        if per_share_risk > 0:
            risk_shares = int(math.floor(risk_cap_pct * equity / per_share_risk))
            shares = min(shares, risk_shares)
    return shares


def _passes_min_rr(entry_basis: float, stop_price: float,
                   min_rr: float | None, target_pct: float) -> bool:
    """A4 entry filter. Proxy R:R = (target_pct·entry) / (entry − stop).

    The exit engine has no profit target, so R:R is only testable as an entry
    gate against a fixed proxy target. True if the gate is disabled or passes.
    """
    if min_rr is None:
        return True
    per_share_risk = entry_basis - stop_price
    if per_share_risk <= 0:
        return False
    reward = entry_basis * target_pct
    return (reward / per_share_risk) >= min_rr


def _sector_room(sector_deployed: dict[str, float], sec: str, cost: float,
                 equity: float, cap_pct: float | None) -> bool:
    """A2 per-sector $-cap. True if adding `cost` keeps the sector within cap
    (or the cap is disabled / the symbol is a cross-sector BROAD ETF)."""
    if cap_pct is None or sec == "BROAD":
        return True
    return sector_deployed.get(sec, 0.0) + cost <= equity * cap_pct


# ---------- Engine ----------

class Engine:
    def __init__(self, bars: dict[str, pd.DataFrame],
                 entry_simulator=None):
        """
        bars: dict[symbol -> OHLC DataFrame], pre-indicators applied if you
              want (otherwise the engine will compute them).
        entry_simulator: callable (bars, current_date, regime, sectors_state, open_symbols, equity)
                         returning list[(symbol, entry_price)] to OPEN today.
                         If None, no entries occur — used for testing exit-only paths.
        """
        self.bars = _precompute_indicators(bars)
        self.entry_simulator = entry_simulator
        if "SPY" not in self.bars or "^VIX" not in self.bars:
            raise ValueError("backtest requires SPY and ^VIX bars to classify regime")

    def run(self, config: BacktestConfig) -> BacktestResult:
        spy = self.bars["SPY"]
        vix = self.bars["^VIX"]
        # Union of all trading days across SPY (the calendar).
        cal = spy.loc[(spy.index.date >= config.start) & (spy.index.date <= config.end)].index

        equity = config.starting_equity
        peak_equity = equity
        prior_equity = equity
        equity_pts: list[tuple[pd.Timestamp, float]] = []
        positions: dict[str, Position] = {}
        # Phase G: in-flight limit/stop orders awaiting a fill or TTL expiry.
        pending_orders: dict[str, _PendingOrder] = {}
        result = BacktestResult(config=config, final_equity=equity, peak_equity=peak_equity)

        rng = np.random.default_rng(config.stress_seed) if config.apply_stress_shocks else None
        raw_regimes: list[str] = []
        effective_regime: str | None = None
        # #2 weekly entry-cap tracking.
        current_week: tuple[int, int] | None = None
        opens_this_week = 0

        for i, ts in enumerate(cal):
            day = ts.date()
            raw_regime = _classify_regime_on(ts, spy, vix)
            raw_regimes.append(raw_regime)
            # #3 anti-whipsaw: only let the posture change once the new regime
            # has persisted >= PERSISTENCE_BARS_REQUIRED bars. Disabled → the
            # effective regime tracks the raw bar classification (legacy).
            if config.enforce_regime_persistence:
                if effective_regime is None:
                    effective_regime = raw_regime
                elif raw_regime != effective_regime:
                    streak = 0
                    for r in reversed(raw_regimes):
                        if r == raw_regime:
                            streak += 1
                        else:
                            break
                    if streak >= rg.PERSISTENCE_BARS_REQUIRED:
                        effective_regime = raw_regime
            else:
                effective_regime = raw_regime
            regime = effective_regime
            result.regime_history.append((day, regime))

            # #2 reset the weekly new-trade counter on each new ISO week.
            iso = ts.isocalendar()
            wk = (iso.year, iso.week)
            if wk != current_week:
                current_week = wk
                opens_this_week = 0

            # ---- Process exits on existing positions ----
            symbols_to_close: list[tuple[str, float, str]] = []
            for sym, pos in list(positions.items()):
                df = self.bars.get(sym)
                if df is None or ts not in df.index:
                    continue
                row = df.loc[ts]
                bar_high = float(row["High"])
                bar_low = float(row["Low"])
                bar_close = float(row["Close"])
                atr_now = float(row["atr_14"]) if not pd.isna(row["atr_14"]) else None

                # Optional stress shock — make the bar low much worse.
                if rng is not None and rng.random() < config.stress_shock_prob:
                    shock = rng.uniform(*config.stress_shock_range)
                    shocked_low = bar_close * (1 + shock)
                    bar_low = min(bar_low, shocked_low)
                    bar_close = shocked_low

                pos.bars_held += 1
                pos.peak_close = max(pos.peak_close, bar_close, bar_high)

                strategy = get_strategy(config.exit_strategy)
                decision = apply_post_strategy_rules(
                    pos, bar_high, bar_low, bar_close, regime, strategy, atr_now,
                    time_stop_days=config.time_stop_days,
                    time_stop_band=config.time_stop_band,
                )
                if decision.close:
                    exit_px = decision.exit_price
                    # #4 gap realism: a trailing-stop hit assumes a fill exactly
                    # at the stop, but if the bar OPENED below the stop the real
                    # fill is the (worse) open, not the stop price.
                    if config.stop_gap_fill and decision.reason == "trailing_stop":
                        open_px = (
                            float(row["Open"])
                            if "Open" in row and not pd.isna(row["Open"])
                            else bar_close
                        )
                        if open_px < exit_px:
                            exit_px = open_px
                    symbols_to_close.append((sym, exit_px, decision.reason))
                elif decision.new_stop_price is not None:
                    pos.current_stop_pct = decision.new_stop_pct
                    pos.current_stop_price = decision.new_stop_price

            for sym, exit_price, reason in symbols_to_close:
                pos = positions.pop(sym)
                pnl = (exit_price - pos.entry_price) * pos.shares - 2 * config.fee_per_trade
                risk_per_share = pos.entry_price - pos.initial_stop
                r_mult = (exit_price - pos.entry_price) / risk_per_share if risk_per_share > 0 else 0.0
                equity += pnl
                result.trades.append(ClosedTradeRecord(
                    symbol=sym, entry_date=pos.entry_date, exit_date=day,
                    entry_price=pos.entry_price, exit_price=exit_price,
                    initial_stop=pos.initial_stop, shares=pos.shares, pnl=pnl,
                    r_multiple=r_mult, sector=pos.sector,
                    regime_at_entry=pos.regime_at_entry, exit_reason=reason,
                ))

            # ---- Account-level circuit breakers (Phase A1) ----
            # Mark-to-market equity at today's close. The realized-only `equity`
            # excludes open positions' unrealized P&L, so comparing it against
            # the prior bar's MTM equity produced false daily-DD / drawdown
            # readings whenever a position carried unrealized gains (e.g. a flat
            # day on a +4% position read as −3.8% and tripped the freeze). The
            # gates must compare MTM-to-MTM, the same equity basis used for the
            # curve and for the live risk_gates EOD comparison.
            current_unrealized = 0.0
            for _sym, _pos in positions.items():
                _df = self.bars.get(_sym)
                if _df is None or ts not in _df.index:
                    continue
                current_unrealized += (float(_df.at[ts, "Close"]) - _pos.entry_price) * _pos.shares
            mtm_now = equity + current_unrealized

            entries_blocked = False
            if config.apply_circuit_breakers:
                daily_pct = (mtm_now - prior_equity) / prior_equity * 100 if prior_equity > 0 else 0.0
                if daily_pct <= -3.0:
                    entries_blocked = True
                drawdown_pct = (mtm_now - peak_equity) / peak_equity * 100 if peak_equity > 0 else 0.0
                if drawdown_pct <= -10.0:
                    result.lock_triggered = True
                    entries_blocked = True
            if config.apply_regime_gating and regime == "Defensive":
                entries_blocked = True

            # ---- Process PENDING orders from prior bars (Phase G) ----
            # Walk every pending limit/stop order placed on a prior bar and
            # try to fill it on today's bar. Day-TIF orders that don't fill
            # this bar have their TTL decremented; expired ones are dropped.
            strategy_for_fills = get_strategy(config.exit_strategy)
            filled_intents: list[tuple[EntryIntent, float]] = []
            for sym in list(pending_orders.keys()):
                po = pending_orders[sym]
                df = self.bars.get(sym)
                if df is None or ts not in df.index:
                    po.bars_remaining -= 1
                    if po.bars_remaining <= 0:
                        pending_orders.pop(sym, None)
                    continue
                row = df.loc[ts]
                bar_low = float(row["Low"])
                bar_high = float(row["High"])
                bar_open = float(row["Open"]) if "Open" in row and not pd.isna(row["Open"]) else float(row["Close"])
                fill_price: float | None = None
                if po.intent.setup_type == "PULLBACK":
                    # Buy-limit: fills if the bar trades down to the limit.
                    # If the bar opens BELOW the limit (gap-down), we get filled
                    # at the open — better-than-limit fill, matching reality.
                    if bar_low <= po.intent.planned_entry:
                        fill_price = min(bar_open, po.intent.planned_entry)
                elif po.intent.setup_type == "BREAKOUT":
                    # Buy-stop: fills if the bar trades up through the stop.
                    if bar_high >= po.intent.planned_entry:
                        fill_price = max(bar_open, po.intent.planned_entry)
                else:  # MOMENTUM
                    fill_price = bar_open

                if fill_price is not None:
                    filled_intents.append((po.intent, fill_price))
                    pending_orders.pop(sym, None)
                else:
                    po.bars_remaining -= 1
                    if po.bars_remaining <= 0:
                        pending_orders.pop(sym, None)

            # Sector exposure tally (excludes BROAD ETFs from the cap).
            # sector_counts = open positions per sector (Phase C count cap);
            # sector_deployed = cost basis per sector (A2 $-cap).
            sector_counts: dict[str, int] = {}
            sector_deployed: dict[str, float] = {}
            for p in positions.values():
                if p.sector and p.sector != "BROAD":
                    sector_counts[p.sector] = sector_counts.get(p.sector, 0) + 1
                    sector_deployed[p.sector] = sector_deployed.get(p.sector, 0.0) + p.entry_price * p.shares

            # #1 deployment / leverage cap. `deployed` is cost basis of open
            # positions; new opens may not push it past `deploy_cap` (cash and/or
            # the regime deployment target). float('inf') → legacy uncapped.
            deployed = sum(p.entry_price * p.shares for p in positions.values())
            _caps: list[float] = []
            if config.enforce_cash_cap:
                _caps.append(equity)
            if config.respect_deployment_target:
                dep_t = rg.POSTURE.get(regime, {}).get("deployment_target", 1.0)
                _caps.append(equity * dep_t)
            deploy_cap = min(_caps) if _caps else float("inf")

            # #2 per-week new-trade cap = min(N/week, regime trade_slots).
            if config.enforce_entry_caps:
                regime_slots = rg.POSTURE.get(regime, {}).get("trade_slots", config.max_positions)
                weekly_cap = min(config.max_new_trades_per_week, regime_slots)
            else:
                weekly_cap = config.max_positions  # effectively unlimited vs max_positions

            # Promote filled intents to open positions, respecting caps.
            for intent, fill_price in filled_intents:
                if intent.symbol in positions:
                    continue
                if len(positions) >= config.max_positions:
                    break
                if config.enforce_entry_caps and opens_this_week >= weekly_cap:
                    break
                df = self.bars.get(intent.symbol)
                sec = sector_of(intent.symbol) or "UNKNOWN"
                if sec != "BROAD" and sector_counts.get(sec, 0) >= config.max_per_sector:
                    continue
                atr_at_entry = float(df.at[ts, "atr_14"]) if not pd.isna(df.at[ts, "atr_14"]) else None
                # Initial_stop is derived from the PLANNED entry, not the realized fill —
                # mirrors the Phase G rule that the original-risk level is immutable.
                stop_pct, stop_price = strategy_for_fills.initial_stop(
                    intent.planned_entry, atr_at_entry
                )
                # A4 R:R gate — proxy target vs ATR stop (risk basis = planned entry).
                if not _passes_min_rr(intent.planned_entry, stop_price,
                                      config.min_rr_at_entry, config.rr_target_pct):
                    continue
                # A3 per-trade risk cap layered on flat-% sizing.
                shares = _sized_shares(equity, config.max_position_pct, fill_price,
                                       intent.planned_entry, stop_price, config.risk_cap_pct)
                if shares <= 0:
                    continue
                realized = fill_price * (1 + config.slippage_pct / 100)
                cost = realized * shares
                # #1 reject the fill if it would breach the deployment / cash cap
                # (mirrors buy_gate's "cost <= cash" — skip rather than partial-fill).
                if deployed + cost > deploy_cap:
                    continue
                # A2 per-sector $-cap.
                if not _sector_room(sector_deployed, sec, cost, equity, config.max_sector_deployment_pct):
                    continue
                positions[intent.symbol] = Position(
                    symbol=intent.symbol, entry_date=day, entry_price=realized,
                    initial_stop=stop_price, shares=shares,
                    sector=sec, regime_at_entry=regime, sizing_method="flat_20pct",
                    current_stop_pct=stop_pct, current_stop_price=stop_price,
                    peak_close=realized, bars_held=0,
                )
                deployed += cost
                opens_this_week += 1
                if sec != "BROAD":
                    sector_counts[sec] = sector_counts.get(sec, 0) + 1
                    sector_deployed[sec] = sector_deployed.get(sec, 0.0) + cost
                equity -= config.fee_per_trade

            # ---- Process new entries via the simulator ----
            if (
                self.entry_simulator is not None
                and not entries_blocked
                and not result.lock_triggered
                and len(positions) < config.max_positions
            ):
                slots = config.max_positions - len(positions)
                proposed = self.entry_simulator(
                    bars=self.bars, current_date=ts, regime=regime,
                    open_symbols=set(positions.keys()) | set(pending_orders.keys()),
                    equity=equity,
                    slots=slots,
                )

                strategy = get_strategy(config.exit_strategy)
                opened_this_bar = 0
                for proposal in proposed:
                    if opened_this_bar >= slots:
                        break
                    # Phase G: simulator may return an EntryIntent dataclass
                    # (limit/stop, queued in pending_orders) or the legacy
                    # (sym, price) tuple (immediate market fill). Duck-type on
                    # `setup_type` rather than isinstance — Python sees two
                    # distinct EntryIntent classes when the engine and tests
                    # import via different module paths (entry_simulator vs.
                    # backtest.entry_simulator), so isinstance breaks.
                    if hasattr(proposal, "setup_type"):
                        if proposal.symbol in positions or proposal.symbol in pending_orders:
                            continue
                        sec_check = sector_of(proposal.symbol) or "UNKNOWN"
                        if sec_check != "BROAD" and sector_counts.get(sec_check, 0) >= config.max_per_sector:
                            continue
                        pending_orders[proposal.symbol] = _PendingOrder(
                            intent=proposal, bars_remaining=proposal.ttl_bars,
                        )
                        opened_this_bar += 1
                        continue

                    if config.enforce_entry_caps and opens_this_week >= weekly_cap:
                        break
                    sym, entry_price = proposal
                    if sym in positions:
                        continue
                    df = self.bars.get(sym)
                    if df is None or ts not in df.index:
                        continue
                    sec = sector_of(sym) or "UNKNOWN"
                    # Sector cap (BROAD ETFs are exempt — they're cross-sector).
                    if sec != "BROAD" and sector_counts.get(sec, 0) >= config.max_per_sector:
                        continue
                    atr_at_entry = float(df.at[ts, "atr_14"]) if not pd.isna(df.at[ts, "atr_14"]) else None
                    stop_pct, stop_price = strategy.initial_stop(entry_price, atr_at_entry)
                    # A4 R:R gate — proxy target vs ATR stop (risk basis = entry price).
                    if not _passes_min_rr(entry_price, stop_price,
                                          config.min_rr_at_entry, config.rr_target_pct):
                        continue
                    # A3 per-trade risk cap layered on flat-% sizing.
                    shares = _sized_shares(equity, config.max_position_pct, entry_price,
                                           entry_price, stop_price, config.risk_cap_pct)
                    if shares <= 0:
                        continue
                    fill_price = entry_price * (1 + config.slippage_pct / 100)
                    cost = fill_price * shares
                    # #1 deployment / cash cap (skip rather than partial-fill).
                    if deployed + cost > deploy_cap:
                        continue
                    # A2 per-sector $-cap.
                    if not _sector_room(sector_deployed, sec, cost, equity, config.max_sector_deployment_pct):
                        continue
                    positions[sym] = Position(
                        symbol=sym, entry_date=day, entry_price=fill_price,
                        initial_stop=stop_price, shares=shares,
                        sector=sec, regime_at_entry=regime, sizing_method="flat_20pct",
                        current_stop_pct=stop_pct, current_stop_price=stop_price,
                        peak_close=fill_price, bars_held=0,
                    )
                    deployed += cost
                    opens_this_week += 1
                    if sec != "BROAD":
                        sector_counts[sec] = sector_counts.get(sec, 0) + 1
                        sector_deployed[sec] = sector_deployed.get(sec, 0.0) + cost
                    opened_this_bar += 1
                    equity -= config.fee_per_trade

            # ---- Mark-to-market equity ----
            unrealized = 0.0
            for sym, pos in positions.items():
                df = self.bars.get(sym)
                if df is None or ts not in df.index:
                    continue
                bar_close = float(df.at[ts, "Close"])
                unrealized += (bar_close - pos.entry_price) * pos.shares
            mtm_equity = equity + unrealized
            equity_pts.append((ts, mtm_equity))
            peak_equity = max(peak_equity, mtm_equity)
            prior_equity = mtm_equity

        # Force-close anything still open at end-of-window at last-close price.
        for sym, pos in list(positions.items()):
            df = self.bars.get(sym)
            if df is None or df.empty:
                continue
            last_ts = df.index[-1]
            exit_price = float(df.at[last_ts, "Close"])
            pnl = (exit_price - pos.entry_price) * pos.shares
            risk_per_share = pos.entry_price - pos.initial_stop
            r_mult = (exit_price - pos.entry_price) / risk_per_share if risk_per_share > 0 else 0.0
            equity += pnl
            result.trades.append(ClosedTradeRecord(
                symbol=sym, entry_date=pos.entry_date, exit_date=last_ts.date(),
                entry_price=pos.entry_price, exit_price=exit_price,
                initial_stop=pos.initial_stop, shares=pos.shares, pnl=pnl,
                r_multiple=r_mult, sector=pos.sector,
                regime_at_entry=pos.regime_at_entry, exit_reason="end_of_window",
            ))

        if equity_pts:
            result.equity_curve = pd.Series(
                {ts: eq for ts, eq in equity_pts}, name="equity"
            )
        result.final_equity = equity
        result.peak_equity = peak_equity
        return result
