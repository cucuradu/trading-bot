# Backtest report — 2026-06-03-203422-atr_2_5x-limit_pullback-pb2-ttl3-riskcap20-realistic

- Window: **2024-01-02 → 2024-06-28**
- Starting equity: **$100,000.00**
- Exit strategy: **`atr_2_5x`**
- Max positions: 6 | Max position %: 20%
- Circuit breakers: on | Regime gating: on | Stress shocks: off
- Drawdown lock triggered: **no**
- Final equity: **$126,712.26** | Peak equity: $128,293.78

## Headline metrics vs. benchmarks

| Strategy | Total | Annual | Sharpe | MaxDD | Trades | WinRate | Profit Factor | Expectancy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **atr_2_5x** | +26.71% | +61.79% | 3.69 | -4.08% | 24 | 75.0% | 9.25 | 0.662 |
| SPY buy-hold | +15.14% | +33.18% | 2.75 | -5.35% | — | — | — | — |
| SPY 200-SMA trend | +12.70% | +27.51% | 2.55 | -5.35% | — | — | — | — |
| Equal-weight random (5) | +19.79% | +44.33% | 2.97 | -4.59% | — | — | — | — |

## R-multiple summary

- avg_R_win: 0.998
- avg_R_loss: -0.346
- payoff_ratio: 2.88

## Sector P&L attribution

| Sector | P&L ($) |
|---|---:|
| XLK | +17,191.63 |
| XLV | +3,838.09 |
| XLI | +2,597.56 |
| XLC | +2,264.33 |
| XLF | +1,023.51 |
| XLY | -35.72 |
| XLE | -167.14 |

## Regime-conditional stats

| Regime | N | Win rate | P&L ($) |
|---|---:|---:|---:|
| Bull | 15 | 86.7% | +20,109.57 |
| Neutral | 9 | 55.6% | +6,602.69 |

## Exit reason distribution

| Reason | Count |
|---|---:|
| trailing_stop | 12 |
| time_stop | 10 |
| end_of_window | 2 |

## Closed trades

| Exit date | Symbol | Sector | Regime | Entry | Exit | R | P&L | Reason |
|---|---|---|---|---:|---:|---:|---:|---|
| 2024-01-16 | MS | XLF | Neutral | 92.02 | 86.74 | -0.82 | -1,146.19 | trailing_stop |
| 2024-01-31 | AVGO | XLK | Neutral | 106.37 | 118.94 | +1.69 | +2,364.62 | trailing_stop |
| 2024-02-01 | MU | XLK | Neutral | 83.13 | 85.61 | +0.43 | +595.20 | time_stop |
| 2024-02-20 | LLY | XLV | Neutral | 621.28 | 754.75 | +3.11 | +4,137.46 | trailing_stop |
| 2024-02-20 | NVDA | XLK | Bull | 67.95 | 69.15 | +0.24 | +361.57 | trailing_stop |
| 2024-03-05 | AMD | XLK | Bull | 170.75 | 200.42 | +1.62 | +3,264.23 | trailing_stop |
| 2024-03-06 | DIS | XLC | Bull | 107.25 | 110.06 | +0.37 | +556.14 | time_stop |
| 2024-03-11 | META | XLC | Bull | 456.87 | 485.15 | +0.91 | +1,244.28 | trailing_stop |
| 2024-03-11 | LLY | XLV | Bull | 738.08 | 744.73 | +0.13 | +186.07 | trailing_stop |
| 2024-03-11 | GE | XLI | Bull | 125.93 | 130.49 | +0.52 | +793.41 | trailing_stop |
| 2024-03-28 | TMO | XLV | Bull | 587.44 | 581.21 | -0.15 | -236.79 | time_stop |
| 2024-04-02 | MU | XLK | Bull | 92.62 | 121.01 | +3.54 | +6,870.67 | trailing_stop |
| 2024-04-03 | NVDA | XLK | Bull | 86.69 | 88.96 | +0.22 | +494.35 | time_stop |
| 2024-04-16 | GOOGL | XLC | Bull | 152.38 | 154.40 | +0.19 | +315.09 | time_stop |
| 2024-04-19 | GE | XLI | Bull | 137.15 | 147.58 | +1.09 | +1,804.15 | trailing_stop |
| 2024-04-19 | ORCL | XLK | Neutral | 121.86 | 115.15 | -0.79 | -1,315.24 | trailing_stop |
| 2024-05-01 | XOM | XLE | Neutral | 117.29 | 116.03 | -0.15 | -256.31 | time_stop |
| 2024-05-14 | CVX | XLE | Neutral | 163.00 | 163.61 | +0.05 | +89.17 | time_stop |
| 2024-05-21 | TSLA | XLY | Neutral | 186.98 | 186.60 | -0.02 | -35.72 | time_stop |
| 2024-06-07 | AMGN | XLV | Bull | 308.25 | 305.02 | -0.15 | -248.65 | time_stop |
| 2024-06-07 | GOOGL | XLC | Bull | 173.38 | 174.46 | +0.09 | +148.82 | time_stop |
| 2024-06-21 | NVDA | XLK | Bull | 119.35 | 127.12 | +0.67 | +1,560.93 | trailing_stop |
| 2024-06-28 | SPGI | XLF | Neutral | 408.59 | 446.00 | +1.31 | +2,169.70 | end_of_window |
| 2024-06-28 | AAPL | XLK | Bull | 187.22 | 210.62 | +1.79 | +2,995.30 | end_of_window |
