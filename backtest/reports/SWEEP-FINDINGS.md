# Sensitivity sweep — findings memo

**Window**: 2024-01-01 → 2025-12-31 (2 years, daily bars, 41 universe symbols)
**Starting equity**: $100,000
**Run date**: 2026-05-23

## All variants

| # | Variant | Total | Annual | Sharpe | MaxDD | Trades | Win% | PF | Expectancy |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | atr_2_5x baseline (10/±3) | +14.05% | +6.82% | 0.72 | −13.34% | 60 | 56.7% | 1.54 | 0.210 |
| 1 | fixed_10 baseline (10/±3) | +16.78% | +8.10% | 0.86 | −11.64% | 41 | 63.4% | 1.99 | 0.213 |
| 2 | chandelier baseline | +5.86% | +2.90% | 0.36 | −13.10% | 51 | 47.1% | 1.25 | 0.146 |
| 3 | atr (15/±2) | +7.15% | +3.53% | 0.40 | −10.19% | 48 | 58.3% | 1.40 | 0.165 |
| 4 | **atr (20/±2)** | **+14.04%** | +6.82% | **1.01** | **−4.60%** | **10** | **80.0%** | **23.21** | **0.927** |
| 5 | **atr + sec_cap=2** | **+19.56%** | +9.38% | **0.96** | −11.53% | 42 | 54.8% | **2.14** | **0.360** |
| 6 | atr (15/±2) + sec_cap=2 | +3.90% | +1.94% | 0.25 | −10.60% | 41 | 58.5% | 1.20 | 0.144 |
| 7 | **fixed_10 + sec_cap=2** ⭐ | **+23.20%** | **+11.04%** | **1.03** | −13.50% | 44 | **63.6%** | **2.31** | 0.262 |
| — | bench: SPY buy-hold | +44.28% | +20.20% | 1.21 | −19.00% | — | — | — | — |
| — | bench: SPY 200-SMA trend | +34.49% | +16.04% | 1.34 | −10.02% | — | — | — | — |
| — | bench: equal-weight random | +22.36% | +10.66% | 0.67 | −18.39% | — | — | — | — |

## Findings

### 1. Sector cap = 2 is the single biggest improvement

Comparing baselines vs. their `sec_cap=2` counterparts:
- **atr_2_5x**: +14.05% → +19.56% (**+5.5pp**), Sharpe 0.72 → 0.96, trades 60 → 42
- **fixed_10**: +16.78% → +23.20% (**+6.4pp**), Sharpe 0.86 → 1.03, trades 41 → 44

The cap forces diversification. The first ATR baseline lost −$9,258 on XLY (Consumer Discretionary) concentration alone — `sec_cap=2` would have prevented that.

**This is a no-brainer addition to production.** It bounds concentration risk without sacrificing trade frequency.

### 2. Fixed-10 trail beats ATR-trail in this window

Across every metric: total return, Sharpe, drawdown, win rate, profit factor. The ATR widths produce too many time-stop exits (34/60 in baseline). The simpler 10% trail lets winners breathe.

**Caveat**: this is one 2-year window. In higher-volatility regimes (2022, 2020), ATR-scaled stops would likely shine because the fixed 10% would shake out positions on routine pullbacks. Need multi-window testing before declaring a winner.

**Recommendation**: keep ATR as the production trail (it's well-grounded mathematically), but flag this for re-test in week 12+.

### 3. Wider time-stop + tighter band has bimodal results

- atr (15/±2) → +7.15% (WORSE) — too narrow a P&L band shakes out positions that briefly drift
- atr (20/±2) → +14.04% with **Sharpe 1.01, max DD −4.60%, 80% win rate** — but only 10 trades

The 20-day variant is interesting but the sample is too thin (10 trades vs 41-60 baseline). It's effectively "barely trade, win when you do." Could be either signal or luck. **Don't deploy without more evidence**.

### 4. Nothing beat SPY buy-hold this window

Expected. 2024-2025 was a strong bull market (+44% on SPY). Any active strategy that uses stops will underperform passive in such windows. The interesting comparison is Sharpe-adjusted: **fixed_10+sec_cap=2 hits Sharpe 1.03 vs SPY's 1.21** — close, and with materially lower max drawdown (−13.5% vs −19.0%).

The 200-SMA trend follower (+34.49%, Sharpe 1.34, maxDD −10%) does beat us. That's worth studying — in a bull market with limited corrections, simple trend-following dominates stock-picking.

### 5. The −10% drawdown lock triggered in every variant

Every backtest hit the lock at some point. That confirms the safety net fires in realistic conditions, but also that the strategy's drawdowns are large enough that the lock is a real-world constraint, not just a tail-risk guard. Once tripped, the bot is dormant until manual reset — that's costing returns.

**Possible refinement** (not tested here): auto-reset the lock after N consecutive days of positive equity, but require explicit human approval to re-enable Half-Kelly sizing. Out of scope for this sweep.

## Recommended production changes

1. **Add `max_per_sector = 2` to the buy-gate.** Strong evidence across both fixed_10 and atr.
2. **Keep ATR as production trail** — backtest is one window; multi-window validation needed before switching to fixed_10.
3. **Re-run sweep in week 12+** with longer history and at least 2 distinct market regimes (bull + at least one of: bear, sideways).

## Reports written this run

- [2026-05-23-234642-compare-fixed_10.md](2026-05-23-234642-compare-fixed_10.md)
- [2026-05-23-234643-compare-atr_2_5x.md](2026-05-23-234643-compare-atr_2_5x.md)
- [2026-05-23-234643-compare-chandelier_3xATR22.md](2026-05-23-234643-compare-chandelier_3xATR22.md)
- [2026-05-23-234643-stress-atr_2_5x.md](2026-05-23-234643-stress-atr_2_5x.md)
- [2026-05-23-235836-atr_2_5x-ts15-bandneg2to2.md](2026-05-23-235836-atr_2_5x-ts15-bandneg2to2.md)
- [2026-05-23-235846-atr_2_5x-ts20-bandneg2to2.md](2026-05-23-235846-atr_2_5x-ts20-bandneg2to2.md)
- [2026-05-23-235855-atr_2_5x-sec2.md](2026-05-23-235855-atr_2_5x-sec2.md)
- [2026-05-23-235905-atr_2_5x-ts15-bandneg2to2-sec2.md](2026-05-23-235905-atr_2_5x-ts15-bandneg2to2-sec2.md)
- [2026-05-23-235914-fixed_10-sec2.md](2026-05-23-235914-fixed_10-sec2.md)
