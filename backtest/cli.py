"""Unified backtest CLI.

Usage:
  python -m backtest run --start 2024-01-01 --end 2025-12-31 --exit atr_2_5x
  python -m backtest compare --start 2024-01-01 --end 2025-12-31
  python -m backtest stress --start 2024-01-01 --end 2025-12-31

`run` writes a single report. `compare` runs all three exit strategies
side-by-side and writes one combined report. `stress` enables the shock
generator and reports safety-net behavior.
"""
from __future__ import annotations

import argparse
import sys
from datetime import date
from pathlib import Path

from backtest.benchmarks import (
    equal_weight_random, spy_200sma_trend, spy_buy_hold,
)
from backtest.data import load_universe_bars
from backtest.engine import BacktestConfig, Engine
from backtest.entry_simulator import (
    make_top_n_entry_simulator,
    make_top_n_limit_pullback_simulator,
)
from backtest.reports import (
    REPORTS_DIR, exit_reason_breakdown, metrics_for_curve,
    metrics_for_result, regime_breakdown, sector_pnl,
    write_markdown_report,
)
from backtest.stress import stress_config, summarize_stress


def _parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(prog="python -m backtest")
    sub = p.add_subparsers(dest="cmd", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--start", required=True, help="YYYY-MM-DD")
    common.add_argument("--end", required=True, help="YYYY-MM-DD")
    common.add_argument("--equity", type=float, default=100_000.0)
    common.add_argument("--force-refresh", action="store_true",
                        help="Re-download bars even if cached")
    common.add_argument("--time-stop-days", type=int, default=10,
                        help="Bars before time-stop is eligible (default 10)")
    common.add_argument("--time-stop-band", type=str, default="-3.0,3.0",
                        help="Lower,upper P&L %% band for time-stop (default -3.0,3.0)")
    common.add_argument("--max-per-sector", type=int, default=2,
                        help="Max simultaneous positions per sector (default 2 = production rule, Phase C)")
    common.add_argument("--entry-mode", default="market_on_open",
                        choices=["market_on_open", "limit_pullback"],
                        help="Entry-order model (Phase G1). market_on_open = current "
                             "behavior; limit_pullback = buy-limit at close × (1 - pullback_pct).")
    common.add_argument("--pullback-pct", type=float, default=0.02,
                        help="Limit-entry pullback fraction (default 0.02 = 2%% below close)")
    common.add_argument("--ttl-bars", type=int, default=1,
                        help="Limit-entry day-TIF lifetime in bars (default 1 = day TIF; 3 mimics watchlist carry)")
    # Realism toggles (audit 2026-05-29). Default off = legacy behavior.
    common.add_argument("--realistic", action="store_true",
                        help="Enable ALL live-rule realism toggles at once (cash cap, "
                             "deployment target, entry caps, regime persistence, gap-fill stops)")
    common.add_argument("--enforce-cash-cap", action="store_true",
                        help="#1 No leverage: total cost basis may not exceed cash")
    common.add_argument("--respect-deployment-target", action="store_true",
                        help="#1b Also cap deployment at the regime target (85/75/50/0%%)")
    common.add_argument("--enforce-entry-caps", action="store_true",
                        help="#2 Cap new opens/week at min(3, regime trade_slots)")
    common.add_argument("--enforce-regime-persistence", action="store_true",
                        help="#3 Require a regime to persist >=3 bars before the posture changes")
    common.add_argument("--stop-gap-fill", action="store_true",
                        help="#4 Trailing-stop fills at the bar open when it gapped below the stop")
    # Remediation knobs (audit 2026-06-03). Default None = off = legacy behavior.
    common.add_argument("--risk-cap-pct", type=float, default=None,
                        help="A3 per-trade risk cap as a fraction of equity (e.g. 0.02 = 2%%). Floors flat-20%% sizing.")
    common.add_argument("--max-sector-deployment-pct", type=float, default=None,
                        help="A2 cap on cost basis per sector ETF as a fraction of equity (e.g. 0.30). BROAD exempt.")
    common.add_argument("--min-rr-at-entry", type=float, default=None,
                        help="A4 skip entries whose proxy R:R (target +20%% vs ATR stop) falls below this.")

    run = sub.add_parser("run", parents=[common])
    run.add_argument("--exit", dest="exit_strategy", default="atr_2_5x",
                     choices=["fixed_10", "atr_2_5x", "chandelier_3xATR22"])

    sub.add_parser("compare", parents=[common])

    stress = sub.add_parser("stress", parents=[common])
    stress.add_argument("--exit", dest="exit_strategy", default="atr_2_5x")
    stress.add_argument("--shock-prob", type=float, default=0.015)

    return p.parse_args(argv)


def _parse_time_stop_band(spec: str) -> tuple[float, float]:
    parts = spec.split(",")
    if len(parts) != 2:
        raise ValueError(f"--time-stop-band must be 'lo,hi', got {spec!r}")
    return float(parts[0]), float(parts[1])


def _build_benchmarks(bars: dict, equity: float, start: date, end: date) -> dict:
    return {
        "SPY buy-hold": spy_buy_hold(bars["SPY"], equity, start, end),
        "SPY 200-SMA trend": spy_200sma_trend(bars["SPY"], equity, start, end),
        "Equal-weight random (5)": equal_weight_random(bars, equity, start, end, n_picks=5),
    }


def _make_simulator(entry_mode: str, pullback_pct: float, ttl_bars: int):
    if entry_mode == "limit_pullback":
        return make_top_n_limit_pullback_simulator(
            pullback_pct=pullback_pct, ttl_bars=ttl_bars,
        )
    return make_top_n_entry_simulator()


def _run_one(bars: dict, exit_strategy: str, start: date, end: date,
             equity: float, *, stress: bool = False, shock_prob: float = 0.015,
             time_stop_days: int = 10,
             time_stop_band: tuple[float, float] = (-3.0, 3.0),
             max_per_sector: int = 2,
             entry_mode: str = "market_on_open",
             pullback_pct: float = 0.02,
             ttl_bars: int = 1,
             enforce_cash_cap: bool = False,
             respect_deployment_target: bool = False,
             enforce_entry_caps: bool = False,
             enforce_regime_persistence: bool = False,
             stop_gap_fill: bool = False,
             risk_cap_pct: float | None = None,
             max_sector_deployment_pct: float | None = None,
             min_rr_at_entry: float | None = None) -> tuple:
    cfg = BacktestConfig(
        start=start, end=end, starting_equity=equity,
        exit_strategy=exit_strategy,
        time_stop_days=time_stop_days,
        time_stop_band=time_stop_band,
        max_per_sector=max_per_sector,
        enforce_cash_cap=enforce_cash_cap,
        respect_deployment_target=respect_deployment_target,
        enforce_entry_caps=enforce_entry_caps,
        enforce_regime_persistence=enforce_regime_persistence,
        stop_gap_fill=stop_gap_fill,
        risk_cap_pct=risk_cap_pct,
        max_sector_deployment_pct=max_sector_deployment_pct,
        min_rr_at_entry=min_rr_at_entry,
    )
    if stress:
        cfg = stress_config(cfg, shock_prob=shock_prob)
    engine = Engine(
        bars,
        entry_simulator=_make_simulator(entry_mode, pullback_pct, ttl_bars),
    )
    result = engine.run(cfg)
    return cfg, result


def _common_kwargs(args: argparse.Namespace) -> dict:
    realistic = getattr(args, "realistic", False)
    return {
        "time_stop_days": args.time_stop_days,
        "time_stop_band": _parse_time_stop_band(args.time_stop_band),
        "max_per_sector": args.max_per_sector,
        "entry_mode": args.entry_mode,
        "pullback_pct": args.pullback_pct,
        "ttl_bars": args.ttl_bars,
        "enforce_cash_cap": realistic or args.enforce_cash_cap,
        "respect_deployment_target": realistic or args.respect_deployment_target,
        "enforce_entry_caps": realistic or args.enforce_entry_caps,
        "enforce_regime_persistence": realistic or args.enforce_regime_persistence,
        "stop_gap_fill": realistic or args.stop_gap_fill,
        "risk_cap_pct": args.risk_cap_pct,
        "max_sector_deployment_pct": args.max_sector_deployment_pct,
        "min_rr_at_entry": args.min_rr_at_entry,
    }


def _run_name_suffix(args: argparse.Namespace) -> str:
    """Encode non-default knobs in the run name so reports are distinguishable."""
    bits: list[str] = []
    if args.time_stop_days != 10:
        bits.append(f"ts{args.time_stop_days}")
    if args.time_stop_band != "-3.0,3.0":
        clean = args.time_stop_band.replace(",", "to").replace("-", "neg").replace(".", "p")
        bits.append(f"band{clean}")
    if args.max_per_sector != 2:
        bits.append(f"sec{args.max_per_sector}")
    if args.entry_mode != "market_on_open":
        bits.append(f"{args.entry_mode}-pb{int(args.pullback_pct*100)}-ttl{args.ttl_bars}")
    if getattr(args, "risk_cap_pct", None) is not None:
        bits.append(f"riskcap{int(args.risk_cap_pct*1000)}")
    if getattr(args, "max_sector_deployment_pct", None) is not None:
        bits.append(f"secdep{int(args.max_sector_deployment_pct*100)}")
    if getattr(args, "min_rr_at_entry", None) is not None:
        bits.append(f"minrr{str(args.min_rr_at_entry).replace('.', 'p')}")
    if getattr(args, "realistic", False):
        bits.append("realistic")
    else:
        flag_tags = [
            ("enforce_cash_cap", "cash"),
            ("respect_deployment_target", "deploy"),
            ("enforce_entry_caps", "entrycap"),
            ("enforce_regime_persistence", "persist"),
            ("stop_gap_fill", "gapfill"),
        ]
        on = [tag for attr, tag in flag_tags if getattr(args, attr, False)]
        if on:
            bits.append("+".join(on))
    return ("-" + "-".join(bits)) if bits else ""


def cmd_run(args: argparse.Namespace) -> int:
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    print(f"loading bars for {start} → {end} ...", file=sys.stderr)
    bars = load_universe_bars(start, end, force_refresh=args.force_refresh)
    print(f"  loaded {len(bars)} symbols", file=sys.stderr)

    cfg, result = _run_one(bars, args.exit_strategy, start, end, args.equity,
                           **_common_kwargs(args))
    benches = _build_benchmarks(bars, args.equity, start, end)
    name = args.exit_strategy + _run_name_suffix(args)
    path = write_markdown_report(result=result, benchmarks=benches, run_name=name)
    print(f"wrote {path}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    print(f"loading bars for {start} → {end} ...", file=sys.stderr)
    bars = load_universe_bars(start, end, force_refresh=args.force_refresh)
    print(f"  loaded {len(bars)} symbols", file=sys.stderr)

    benches = _build_benchmarks(bars, args.equity, start, end)
    suffix = _run_name_suffix(args)
    kwargs = _common_kwargs(args)
    for strat in ("fixed_10", "atr_2_5x", "chandelier_3xATR22"):
        print(f"  running {strat} ...", file=sys.stderr)
        _, result = _run_one(bars, strat, start, end, args.equity, **kwargs)
        path = write_markdown_report(
            result=result, benchmarks=benches, run_name=f"compare-{strat}{suffix}",
        )
        print(f"  wrote {path}")
    return 0


def cmd_stress(args: argparse.Namespace) -> int:
    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    print(f"loading bars for {start} → {end} ...", file=sys.stderr)
    bars = load_universe_bars(start, end, force_refresh=args.force_refresh)
    print(f"  loaded {len(bars)} symbols", file=sys.stderr)

    cfg, result = _run_one(
        bars, args.exit_strategy, start, end, args.equity,
        stress=True, shock_prob=args.shock_prob, **_common_kwargs(args),
    )
    benches = _build_benchmarks(bars, args.equity, start, end)
    stress_summary = summarize_stress(result)
    suffix = _run_name_suffix(args)
    path = write_markdown_report(
        result=result, benchmarks=benches, run_name=f"stress-{args.exit_strategy}{suffix}",
    )
    print(f"wrote {path}")
    print("stress summary:")
    for k, v in stress_summary.as_dict().items():
        print(f"  {k}: {v}")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv if argv is not None else sys.argv[1:])
    if args.cmd == "run":
        return cmd_run(args)
    if args.cmd == "compare":
        return cmd_compare(args)
    if args.cmd == "stress":
        return cmd_stress(args)
    raise SystemExit(f"unknown command: {args.cmd}")


if __name__ == "__main__":
    raise SystemExit(main())
