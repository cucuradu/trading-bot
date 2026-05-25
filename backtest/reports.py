"""Performance metrics + markdown report writer for backtest results."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd


REPORTS_DIR = Path(__file__).resolve().parent / "reports"
TRADING_DAYS_PER_YEAR = 252


@dataclass
class Metrics:
    total_return_pct: float
    annualized_return_pct: float
    sharpe: float                     # annualized
    max_drawdown_pct: float           # negative number
    win_rate: float | None
    profit_factor: float | None
    expectancy: float | None
    n_trades: int
    avg_r_win: float | None
    avg_r_loss: float | None

    def as_dict(self) -> dict:
        return {
            "total_return_pct": round(self.total_return_pct, 3),
            "annualized_return_pct": round(self.annualized_return_pct, 3),
            "sharpe": round(self.sharpe, 3),
            "max_drawdown_pct": round(self.max_drawdown_pct, 3),
            "win_rate": round(self.win_rate, 4) if self.win_rate is not None else None,
            "profit_factor": round(self.profit_factor, 3) if self.profit_factor is not None else None,
            "expectancy": round(self.expectancy, 4) if self.expectancy is not None else None,
            "n_trades": self.n_trades,
            "avg_r_win": round(self.avg_r_win, 4) if self.avg_r_win is not None else None,
            "avg_r_loss": round(self.avg_r_loss, 4) if self.avg_r_loss is not None else None,
        }


def equity_curve_metrics(curve: pd.Series, trading_days_per_year: int = TRADING_DAYS_PER_YEAR) -> dict:
    """Total return, annualized return, Sharpe, max drawdown for an equity curve."""
    if curve.empty or len(curve) < 2:
        return {
            "total_return_pct": 0.0,
            "annualized_return_pct": 0.0,
            "sharpe": 0.0,
            "max_drawdown_pct": 0.0,
        }
    rets = curve.pct_change().dropna()
    total_ret = curve.iloc[-1] / curve.iloc[0] - 1
    n = len(curve)
    years = n / trading_days_per_year
    ann_ret = (1 + total_ret) ** (1 / max(years, 1e-6)) - 1 if total_ret > -1 else -1.0
    if rets.std(ddof=0) == 0:
        sharpe = 0.0
    else:
        sharpe = float(rets.mean() / rets.std(ddof=0) * np.sqrt(trading_days_per_year))
    running_peak = curve.cummax()
    drawdowns = (curve - running_peak) / running_peak
    max_dd = float(drawdowns.min()) * 100
    return {
        "total_return_pct": float(total_ret * 100),
        "annualized_return_pct": float(ann_ret * 100),
        "sharpe": sharpe,
        "max_drawdown_pct": max_dd,
    }


def trade_metrics(trades: list) -> dict:
    """Win rate, profit factor, expectancy, avg R win/loss from ClosedTradeRecord list."""
    if not trades:
        return {
            "win_rate": None, "profit_factor": None, "expectancy": None,
            "avg_r_win": None, "avg_r_loss": None, "n_trades": 0,
        }
    wins = [t for t in trades if t.r_multiple > 0]
    losses = [t for t in trades if t.r_multiple <= 0]
    n = len(trades)
    win_rate = len(wins) / n
    avg_r_win = (sum(t.r_multiple for t in wins) / len(wins)) if wins else None
    avg_r_loss = (sum(t.r_multiple for t in losses) / len(losses)) if losses else None
    gross_w = sum(t.pnl for t in wins)
    gross_l = abs(sum(t.pnl for t in losses))
    profit_factor = (gross_w / gross_l) if gross_l > 0 else None
    expectancy = None
    if avg_r_win is not None and avg_r_loss is not None:
        expectancy = win_rate * avg_r_win - (1 - win_rate) * abs(avg_r_loss)
    return {
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "expectancy": expectancy,
        "avg_r_win": avg_r_win,
        "avg_r_loss": avg_r_loss,
        "n_trades": n,
    }


def metrics_for_result(result, trading_days_per_year: int = TRADING_DAYS_PER_YEAR) -> Metrics:
    eq = equity_curve_metrics(result.equity_curve, trading_days_per_year)
    tm = trade_metrics(result.trades)
    return Metrics(
        total_return_pct=eq["total_return_pct"],
        annualized_return_pct=eq["annualized_return_pct"],
        sharpe=eq["sharpe"],
        max_drawdown_pct=eq["max_drawdown_pct"],
        win_rate=tm["win_rate"],
        profit_factor=tm["profit_factor"],
        expectancy=tm["expectancy"],
        n_trades=tm["n_trades"],
        avg_r_win=tm["avg_r_win"],
        avg_r_loss=tm["avg_r_loss"],
    )


def metrics_for_curve(curve: pd.Series) -> Metrics:
    """Equity-curve-only metrics (no trade-level stats)."""
    eq = equity_curve_metrics(curve)
    return Metrics(
        total_return_pct=eq["total_return_pct"],
        annualized_return_pct=eq["annualized_return_pct"],
        sharpe=eq["sharpe"],
        max_drawdown_pct=eq["max_drawdown_pct"],
        win_rate=None, profit_factor=None, expectancy=None,
        n_trades=0, avg_r_win=None, avg_r_loss=None,
    )


# ---------- Sector + regime breakdowns ----------

def sector_pnl(trades: list) -> dict[str, float]:
    out: dict[str, float] = {}
    for t in trades:
        out[t.sector] = round(out.get(t.sector, 0.0) + t.pnl, 2)
    return out


def regime_breakdown(trades: list) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for t in trades:
        r = t.regime_at_entry
        if r not in out:
            out[r] = {"n": 0, "wins": 0, "pnl": 0.0}
        out[r]["n"] += 1
        if t.r_multiple > 0:
            out[r]["wins"] += 1
        out[r]["pnl"] = round(out[r]["pnl"] + t.pnl, 2)
    for r in out:
        out[r]["win_rate"] = round(out[r]["wins"] / out[r]["n"], 4) if out[r]["n"] else 0.0
    return out


def exit_reason_breakdown(trades: list) -> dict[str, int]:
    out: dict[str, int] = {}
    for t in trades:
        out[t.exit_reason] = out.get(t.exit_reason, 0) + 1
    return out


# ---------- Markdown report ----------

def _fmt_pct(x: float | None) -> str:
    return f"{x:+.2f}%" if x is not None else "—"


def _fmt_num(x: float | None, prec: int = 3) -> str:
    return f"{x:.{prec}f}" if x is not None else "—"


def write_markdown_report(*, result, benchmarks: dict[str, pd.Series],
                          run_name: str | None = None,
                          out_dir: Path | None = None) -> Path:
    """Write a single backtest result + its benchmark comparison to disk."""
    out_dir = out_dir or REPORTS_DIR
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    suffix = f"-{run_name}" if run_name else ""
    path = out_dir / f"{stamp}{suffix}.md"

    cfg = result.config
    strat_metrics = metrics_for_result(result)
    bench_metrics = {name: metrics_for_curve(s) for name, s in benchmarks.items()}
    sec_pnl = sector_pnl(result.trades)
    reg_break = regime_breakdown(result.trades)
    exit_break = exit_reason_breakdown(result.trades)

    lines: list[str] = []
    push = lines.append
    push(f"# Backtest report — {stamp}{suffix}")
    push("")
    push(f"- Window: **{cfg.start} → {cfg.end}**")
    push(f"- Starting equity: **${cfg.starting_equity:,.2f}**")
    push(f"- Exit strategy: **`{cfg.exit_strategy}`**")
    push(f"- Max positions: {cfg.max_positions} | Max position %: {cfg.max_position_pct * 100:.0f}%")
    push(f"- Circuit breakers: {'on' if cfg.apply_circuit_breakers else 'off'} | "
         f"Regime gating: {'on' if cfg.apply_regime_gating else 'off'} | "
         f"Stress shocks: {'on' if cfg.apply_stress_shocks else 'off'}")
    push(f"- Drawdown lock triggered: **{'YES' if result.lock_triggered else 'no'}**")
    push(f"- Final equity: **${result.final_equity:,.2f}** | Peak equity: ${result.peak_equity:,.2f}")
    push("")
    push("## Headline metrics vs. benchmarks")
    push("")
    push("| Strategy | Total | Annual | Sharpe | MaxDD | Trades | WinRate | Profit Factor | Expectancy |")
    push("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    push(f"| **{cfg.exit_strategy}** | "
         f"{_fmt_pct(strat_metrics.total_return_pct)} | "
         f"{_fmt_pct(strat_metrics.annualized_return_pct)} | "
         f"{_fmt_num(strat_metrics.sharpe, 2)} | "
         f"{_fmt_pct(strat_metrics.max_drawdown_pct)} | "
         f"{strat_metrics.n_trades} | "
         f"{(strat_metrics.win_rate * 100):.1f}% | "
         f"{_fmt_num(strat_metrics.profit_factor, 2)} | "
         f"{_fmt_num(strat_metrics.expectancy, 3)} |")
    for name, m in bench_metrics.items():
        push(f"| {name} | "
             f"{_fmt_pct(m.total_return_pct)} | "
             f"{_fmt_pct(m.annualized_return_pct)} | "
             f"{_fmt_num(m.sharpe, 2)} | "
             f"{_fmt_pct(m.max_drawdown_pct)} | "
             f"— | — | — | — |")

    push("")
    push("## R-multiple summary")
    push("")
    push(f"- avg_R_win: {_fmt_num(strat_metrics.avg_r_win)}")
    push(f"- avg_R_loss: {_fmt_num(strat_metrics.avg_r_loss)}")
    if strat_metrics.avg_r_win and strat_metrics.avg_r_loss:
        push(f"- payoff_ratio: {_fmt_num(strat_metrics.avg_r_win / abs(strat_metrics.avg_r_loss), 2)}")

    push("")
    push("## Sector P&L attribution")
    push("")
    push("| Sector | P&L ($) |")
    push("|---|---:|")
    for sec, pnl in sorted(sec_pnl.items(), key=lambda kv: -kv[1]):
        push(f"| {sec} | {pnl:+,.2f} |")

    push("")
    push("## Regime-conditional stats")
    push("")
    push("| Regime | N | Win rate | P&L ($) |")
    push("|---|---:|---:|---:|")
    for r, info in sorted(reg_break.items(), key=lambda kv: -kv[1]["pnl"]):
        push(f"| {r} | {info['n']} | {info.get('win_rate', 0) * 100:.1f}% | {info['pnl']:+,.2f} |")

    push("")
    push("## Exit reason distribution")
    push("")
    push("| Reason | Count |")
    push("|---|---:|")
    for reason, count in sorted(exit_break.items(), key=lambda kv: -kv[1]):
        push(f"| {reason} | {count} |")

    push("")
    push("## Closed trades")
    push("")
    push("| Exit date | Symbol | Sector | Regime | Entry | Exit | R | P&L | Reason |")
    push("|---|---|---|---|---:|---:|---:|---:|---|")
    for t in result.trades:
        push(f"| {t.exit_date} | {t.symbol} | {t.sector} | {t.regime_at_entry} | "
             f"{t.entry_price:.2f} | {t.exit_price:.2f} | {t.r_multiple:+.2f} | "
             f"{t.pnl:+,.2f} | {t.exit_reason} |")

    path.write_text("\n".join(lines) + "\n")
    return path
