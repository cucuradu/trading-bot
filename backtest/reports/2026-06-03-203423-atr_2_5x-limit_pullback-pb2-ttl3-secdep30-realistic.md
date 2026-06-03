# Backtest report — 2026-06-03-203423-atr_2_5x-limit_pullback-pb2-ttl3-secdep30-realistic

- Window: **2024-01-02 → 2024-06-28**
- Starting equity: **$100,000.00**
- Exit strategy: **`atr_2_5x`**
- Max positions: 6 | Max position %: 20%
- Circuit breakers: on | Regime gating: on | Stress shocks: off
- Drawdown lock triggered: **no**
- Final equity: **$120,930.06** | Peak equity: $121,521.06

## Headline metrics vs. benchmarks

| Strategy | Total | Annual | Sharpe | MaxDD | Trades | WinRate | Profit Factor | Expectancy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **atr_2_5x** | +20.93% | +47.14% | 3.07 | -4.38% | 23 | 52.2% | 5.33 | 0.537 |
| SPY buy-hold | +15.14% | +33.18% | 2.75 | -5.35% | — | — | — | — |
| SPY 200-SMA trend | +12.70% | +27.51% | 2.55 | -5.35% | — | — | — | — |
| Equal-weight random (5) | +19.79% | +44.33% | 2.97 | -4.59% | — | — | — | — |

## R-multiple summary

- avg_R_win: 1.298
- avg_R_loss: -0.294
- payoff_ratio: 4.41

## Sector P&L attribution

| Sector | P&L ($) |
|---|---:|
| XLK | +15,712.86 |
| XLI | +2,806.17 |
| XLC | +1,324.00 |
| XLF | +948.69 |
| XLV | +432.98 |
| XLY | -47.12 |
| XLE | -247.51 |

## Regime-conditional stats

| Regime | N | Win rate | P&L ($) |
|---|---:|---:|---:|
| Bull | 13 | 69.2% | +19,703.79 |
| Neutral | 10 | 30.0% | +1,226.28 |

## Exit reason distribution

| Reason | Count |
|---|---:|
| trailing_stop | 12 |
| time_stop | 9 |
| end_of_window | 2 |

## Closed trades

| Exit date | Symbol | Sector | Regime | Entry | Exit | R | P&L | Reason |
|---|---|---|---|---:|---:|---:|---:|---|
| 2024-01-16 | MS | XLF | Neutral | 92.02 | 86.74 | -0.82 | -1,146.19 | trailing_stop |
| 2024-01-29 | XBI | XLV | Neutral | 91.55 | 90.80 | -0.11 | -163.85 | time_stop |
| 2024-01-31 | AVGO | XLK | Neutral | 106.37 | 118.94 | +1.69 | +2,364.62 | trailing_stop |
| 2024-02-13 | NFLX | XLC | Neutral | 56.43 | 55.45 | -0.24 | -340.42 | time_stop |
| 2024-02-13 | NOW | XLK | Neutral | 154.30 | 151.65 | -0.25 | -344.44 | trailing_stop |
| 2024-02-20 | NVDA | XLK | Bull | 70.40 | 68.51 | -0.36 | -537.32 | trailing_stop |
| 2024-02-21 | LLY | XLV | Bull | 692.08 | 738.08 | +0.95 | +1,334.12 | trailing_stop |
| 2024-03-08 | NVDA | XLK | Bull | 68.01 | 88.13 | +3.35 | +5,976.43 | trailing_stop |
| 2024-03-11 | META | XLC | Bull | 456.87 | 485.15 | +0.91 | +1,216.00 | trailing_stop |
| 2024-03-11 | LLY | XLV | Bull | 754.90 | 744.73 | -0.20 | -264.54 | trailing_stop |
| 2024-03-11 | GE | XLI | Bull | 125.93 | 130.49 | +0.52 | +729.58 | trailing_stop |
| 2024-03-28 | TMO | XLV | Bull | 587.44 | 581.21 | -0.15 | -230.56 | time_stop |
| 2024-04-02 | MU | XLK | Bull | 92.62 | 121.01 | +3.54 | +6,643.54 | trailing_stop |
| 2024-04-16 | GOOGL | XLC | Bull | 152.38 | 154.40 | +0.19 | +304.99 | time_stop |
| 2024-04-19 | GE | XLI | Bull | 137.15 | 147.58 | +1.09 | +1,752.01 | trailing_stop |
| 2024-04-19 | ORCL | XLK | Neutral | 121.86 | 115.15 | -0.79 | -1,268.27 | trailing_stop |
| 2024-05-01 | XOM | XLE | Neutral | 117.29 | 116.03 | -0.15 | -247.51 | time_stop |
| 2024-05-15 | GE | XLI | Neutral | 161.20 | 163.47 | +0.17 | +324.58 | time_stop |
| 2024-05-21 | TSLA | XLY | Neutral | 186.98 | 186.60 | -0.02 | -47.12 | time_stop |
| 2024-06-07 | AMGN | XLV | Bull | 308.25 | 305.02 | -0.15 | -242.19 | time_stop |
| 2024-06-07 | GOOGL | XLC | Bull | 173.38 | 174.46 | +0.09 | +143.43 | time_stop |
| 2024-06-28 | SPGI | XLF | Neutral | 408.59 | 446.00 | +1.31 | +2,094.88 | end_of_window |
| 2024-06-28 | AAPL | XLK | Bull | 187.22 | 210.62 | +1.79 | +2,878.30 | end_of_window |
