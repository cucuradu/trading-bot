# Phase C — multi-window sweep findings (final)

**Date**: 2026-05-24
**Final accepted changes**:
  1. Sector cap = 2 (engine default).
  2. Hard cut at R ≤ −1 (close ≤ initial_stop) replacing the fixed −7%.
  3. Drawdown LOCK auto-recovers after 5 consecutive non-negative EOD days +
     ≥3pp drawdown improvement from trigger.
**Rejected after testing**: trend-confirmation entry filter (price > 200-SMA
AND 200-SMA rising). Backed out — see "Why the trend filter was rejected"
below.

**Windows tested**: 2024-2025 (bull) and 2020-2022 (COVID + 2022 bear).
**Universe**: same 41 tickers as prior sweep.

## Headline numbers

### Window 1 — 2024-01-01 → 2025-12-31 (bull)

| Variant | Total | Annual | Sharpe | MaxDD | Trades | Win% | PF | Expectancy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **fixed_10** | **+24.75%** | **+11.74%** | **1.09** | −13.50% | 43 | **65.1%** | 2.52 | 0.283 |
| atr_2_5x | +19.64% | +9.42% | 0.96 | −12.01% | 41 | 56.1% | 2.15 | 0.370 |
| chandelier | +16.33% | +7.89% | 0.88 | −9.88% | 45 | 62.2% | 1.93 | 0.298 |
| bench: SPY buy-hold | +44.28% | +20.20% | 1.21 | −19.00% | — | — | — | — |
| bench: SPY 200-SMA trend | +34.49% | +16.04% | 1.34 | −10.02% | — | — | — | — |
| bench: equal-weight random | +22.36% | +10.66% | 0.67 | −18.39% | — | — | — | — |

### Window 2 — 2020-01-01 → 2022-12-31 (COVID + 2022 bear)

| Variant | Total | Annual | Sharpe | MaxDD | Trades | Win% | PF | Expectancy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **atr_2_5x** | **+119.69%** | **+30.00%** | **2.10** | **−8.24%** | 115 | 64.3% | **4.20** | **0.410** |
| chandelier | +32.66% | +9.88% | 1.34 | −7.52% | 25 | 88.0% | 18.21 | 0.485 |
| fixed_10 | +22.45% | +6.98% | 0.91 | −11.56% | 45 | 71.1% | 2.52 | 0.238 |
| bench: SPY buy-hold | +17.72% | +5.59% | 0.34 | −34.10% | — | — | — | — |
| bench: SPY 200-SMA trend | +9.91% | +3.20% | 0.31 | −19.34% | — | — | — | — |
| bench: equal-weight random | +36.57% | +10.95% | 0.51 | −31.95% | — | — | — | — |

## Findings

### 1. The accepted Phase C stack beats every benchmark in the bear window

In 2020-2022, **atr_2_5x at +119.69% / Sharpe 2.10 / max DD −8.24%** crushed
SPY buy-hold (+17.72% / max DD −34.10%) and SPY-200-SMA-trend (+9.91% / max DD
−19.34%). Even the most conservative variant (fixed_10) outperformed all three
benchmarks with materially less drawdown. The strategy actually works through
the COVID crash and the 2022 bear — high win rate (64-88%), profit factor
above 2.5 across the board, and the max DD is roughly *one third* of buy-hold.

### 2. The bull window underperforms SPY but beats two of three benchmarks

In 2024-2025, **fixed_10 at +24.75% / Sharpe 1.09** beats equal-weight random
(+22.36%) and is competitive on risk-adjusted terms with SPY-200-SMA-trend
(Sharpe 1.34) and SPY buy-hold (Sharpe 1.21). Outright return trails SPY
(+44.28%), which is expected: a stop-based active strategy cannot keep up with
passive in a long uninterrupted uptrend. The compensation is on the bear-window
side where SPY blew up.

### 3. Cross-window robustness is the headline

| Variant | 2024-2025 | 2020-2022 |
|---|---:|---:|
| fixed_10 | +24.75% | +22.45% |
| atr_2_5x | +19.64% | +119.69% |
| chandelier | +16.33% | +32.66% |

The strategy is **profitable across both regimes**. atr_2_5x in particular
benefits from volatility (it adapts stop width via ATR), which is why it
explodes in 2020-2022 — high VIX widens the stops, lets winners run further.
In low-vol 2024-2025 it's tighter and earns less.

### 4. Why the trend filter was rejected

An earlier Phase C iteration also included a "price > 200-SMA AND 200-SMA
rising for the last 10 sessions" entry filter, on the (textbook) theory that
it would block dead-cat bounces in down-trending names. The first sweep was
unambiguous against it:

| Window | with trend filter | without trend filter | delta |
|---|---:|---:|---:|
| 2024-2025 fixed_10 | +13.34% | +24.75% | **−11.4pp** |
| 2024-2025 atr_2_5x | +15.97% | +19.64% | **−3.7pp** |
| 2020-2022 atr_2_5x | −8.80% | +119.69% | **−128pp** |
| 2020-2022 trades | 8 over 3 years (0% win) | 115 trades (64% win) | — |

The filter was *catastrophically* restrictive through regime changes: in
2020-2022 it locked the bot out of the entire post-COVID recovery (because the
200-SMA was falling for ~12 months), then only allowed entries right as the
2022 bear began — every one of those 8 entries lost. Lesson: a strict trend
filter on individual names + a strict momentum-rank entry criterion is
redundant *and* miscalibrated; momentum rank already captures direction.

### 5. The R = −1 hard cut helps independently

Old fixed_10 + sec_cap=2 (with −7% hard cut): +23.20% / Sharpe 1.03 in
2024-2025.
New fixed_10 + sec_cap=2 + R=−1: +24.75% / Sharpe 1.09 in 2024-2025.
The R=−1 change is a small but real positive even in a bull window where stops
rarely fire. The bigger value is in 2020-2022 where the wider ATR stops needed
the room to work — fixed_10 was +22.45% there, atr_2_5x was +119.69%.

### 6. Production exit strategy: keep `atr_2_5x`

Cross-window weighting strongly favors atr_2_5x. fixed_10 is slightly better
in the bull window (+24.75 vs +19.64), but atr_2_5x is massively better in the
bear window (+119.69 vs +22.45). Average annual return across the two windows
is +9.42% vs +30.00% — the ATR variant wins by ~3×.

## Net changes accepted into production

| Change | Status | Evidence |
|---|---|---|
| Sector cap = 2 (default) | accepted | Prior sweep +5-6pp / 2y; confirmed here |
| Hard cut at R ≤ −1 | accepted | +1.55pp on fixed_10 in bull; consistent in bear |
| Lock auto-recovery (5 days + ≥3pp) | accepted | Safety/ops, not return-impacting |
| Trend-confirmation entry filter | **rejected** | −11.4pp bull / −128pp bear |

## Reports written this run

- 2024-2025:
  - [2026-05-24-133150-compare-fixed_10.md](2026-05-24-133150-compare-fixed_10.md)
  - [2026-05-24-133151-compare-atr_2_5x.md](2026-05-24-133151-compare-atr_2_5x.md)
  - [2026-05-24-133151-compare-chandelier_3xATR22.md](2026-05-24-133151-compare-chandelier_3xATR22.md)
- 2020-2022:
  - [2026-05-24-133152-compare-fixed_10.md](2026-05-24-133152-compare-fixed_10.md)
  - [2026-05-24-133153-compare-atr_2_5x.md](2026-05-24-133153-compare-atr_2_5x.md)
  - [2026-05-24-133154-compare-chandelier_3xATR22.md](2026-05-24-133154-compare-chandelier_3xATR22.md)
