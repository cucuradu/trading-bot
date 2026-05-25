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
from backtest.entry_simulator import make_top_n_entry_simulator
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


def _run_one(bars: dict, exit_strategy: str, start: date, end: date,
             equity: float, *, stress: bool = False, shock_prob: float = 0.015,
             time_stop_days: int = 10,
             time_stop_band: tuple[float, float] = (-3.0, 3.0),
             max_per_sector: int = 2) -> tuple:
    cfg = BacktestConfig(
        start=start, end=end, starting_equity=equity,
        exit_strategy=exit_strategy,
        time_stop_days=time_stop_days,
        time_stop_band=time_stop_band,
        max_per_sector=max_per_sector,
    )
    if stress:
        cfg = stress_config(cfg, shock_prob=shock_prob)
    engine = Engine(bars, entry_simulator=make_top_n_entry_simulator())
    result = engine.run(cfg)
    return cfg, result


def _common_kwargs(args: argparse.Namespace) -> dict:
    return {
        "time_stop_days": args.time_stop_days,
        "time_stop_band": _parse_time_stop_band(args.time_stop_band),
        "max_per_sector": args.max_per_sector,
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
