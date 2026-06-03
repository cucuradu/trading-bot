# Backtest report — 2026-06-03-203425-atr_2_5x-limit_pullback-pb2-ttl3-minrr2p0-realistic

- Window: **2024-01-02 → 2024-06-28**
- Starting equity: **$100,000.00**
- Exit strategy: **`atr_2_5x`**
- Max positions: 6 | Max position %: 20%
- Circuit breakers: on | Regime gating: on | Stress shocks: off
- Drawdown lock triggered: **no**
- Final equity: **$128,741.53** | Peak equity: $130,345.62

## Headline metrics vs. benchmarks

| Strategy | Total | Annual | Sharpe | MaxDD | Trades | WinRate | Profit Factor | Expectancy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **atr_2_5x** | +28.74% | +67.10% | 3.91 | -3.74% | 23 | 73.9% | 9.18 | 0.734 |
| SPY buy-hold | +15.14% | +33.18% | 2.75 | -5.35% | — | — | — | — |
| SPY 200-SMA trend | +12.70% | +27.51% | 2.55 | -5.35% | — | — | — | — |
| Equal-weight random (5) | +19.79% | +44.33% | 2.97 | -4.59% | — | — | — | — |

## R-multiple summary

- avg_R_win: 1.126
- avg_R_loss: -0.377
- payoff_ratio: 2.98

## Sector P&L attribution

| Sector | P&L ($) |
|---|---:|
| XLK | +19,573.78 |
| XLV | +3,831.63 |
| XLC | +2,267.72 |
| XLI | +2,175.91 |
| XLF | +1,060.92 |
| XLE | -168.44 |

## Regime-conditional stats

| Regime | N | Win rate | P&L ($) |
|---|---:|---:|---:|
| Bull | 14 | 78.6% | +21,739.95 |
| Neutral | 9 | 66.7% | +7,001.57 |

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
| 2024-01-31 | AVGO | XLK | Neutral | 106.37 | 118.94 | +1.69 | +2,364.62 | trailing_stop |
| 2024-02-01 | MU | XLK | Neutral | 83.13 | 85.61 | +0.43 | +595.20 | time_stop |
| 2024-02-13 | NOW | XLK | Bull | 153.83 | 151.65 | -0.20 | -287.64 | trailing_stop |
| 2024-02-20 | LLY | XLV | Neutral | 621.28 | 754.75 | +3.11 | +4,137.46 | trailing_stop |
| 2024-02-20 | NVDA | XLK | Bull | 67.95 | 69.15 | +0.24 | +361.57 | trailing_stop |
| 2024-03-06 | DIS | XLC | Bull | 107.25 | 110.06 | +0.37 | +553.33 | time_stop |
| 2024-03-08 | NVDA | XLK | Bull | 68.01 | 88.13 | +3.35 | +6,258.14 | trailing_stop |
| 2024-03-11 | META | XLC | Bull | 456.87 | 485.15 | +0.91 | +1,244.28 | trailing_stop |
| 2024-03-11 | LLY | XLV | Bull | 738.08 | 744.73 | +0.13 | +186.07 | trailing_stop |
| 2024-03-28 | TMO | XLV | Bull | 587.44 | 581.21 | -0.15 | -236.79 | time_stop |
| 2024-04-02 | MU | XLK | Bull | 92.62 | 121.01 | +3.54 | +6,984.23 | trailing_stop |
| 2024-04-16 | GOOGL | XLC | Bull | 152.38 | 154.40 | +0.19 | +319.13 | time_stop |
| 2024-04-19 | GE | XLI | Bull | 137.15 | 147.58 | +1.09 | +1,835.44 | trailing_stop |
| 2024-04-19 | ORCL | XLK | Neutral | 121.86 | 115.15 | -0.79 | -1,328.66 | trailing_stop |
| 2024-05-01 | XOM | XLE | Neutral | 117.29 | 116.03 | -0.15 | -258.82 | time_stop |
| 2024-05-14 | CVX | XLE | Neutral | 163.00 | 163.61 | +0.05 | +90.38 | time_stop |
| 2024-05-15 | GE | XLI | Neutral | 161.20 | 163.47 | +0.17 | +340.47 | time_stop |
| 2024-06-07 | AMGN | XLV | Bull | 308.25 | 305.02 | -0.15 | -255.11 | time_stop |
| 2024-06-07 | GOOGL | XLC | Bull | 173.38 | 174.46 | +0.09 | +150.98 | time_stop |
| 2024-06-21 | NVDA | XLK | Bull | 119.35 | 127.12 | +0.67 | +1,584.22 | trailing_stop |
| 2024-06-28 | SPGI | XLF | Neutral | 408.59 | 446.00 | +1.31 | +2,207.11 | end_of_window |
| 2024-06-28 | AAPL | XLK | Bull | 187.22 | 210.62 | +1.79 | +3,042.10 | end_of_window |
