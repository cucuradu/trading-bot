# Backtest report — 2026-05-29-191058-atr_2_5x-limit_pullback-pb2-ttl3

- Window: **2024-01-01 → 2025-12-31**
- Starting equity: **$100,000.00**
- Exit strategy: **`atr_2_5x`**
- Max positions: 6 | Max position %: 20%
- Circuit breakers: on | Regime gating: on | Stress shocks: off
- Drawdown lock triggered: **YES**
- Final equity: **$120,756.82** | Peak equity: $132,302.08

## Headline metrics vs. benchmarks

| Strategy | Total | Annual | Sharpe | MaxDD | Trades | WinRate | Profit Factor | Expectancy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **atr_2_5x** | +20.76% | +9.93% | 1.13 | -9.07% | 39 | 51.3% | 2.20 | 0.353 |
| SPY buy-hold | +44.28% | +20.20% | 1.21 | -19.00% | — | — | — | — |
| SPY 200-SMA trend | +34.49% | +16.04% | 1.34 | -10.02% | — | — | — | — |
| Equal-weight random (5) | +37.33% | +17.26% | 1.00 | -18.19% | — | — | — | — |

## R-multiple summary

- avg_R_win: 1.104
- avg_R_loss: -0.438
- payoff_ratio: 2.52

## Sector P&L attribution

| Sector | P&L ($) |
|---|---:|
| XLK | +24,564.90 |
| XLC | +5,520.45 |
| XLI | +1,816.36 |
| XLV | +286.01 |
| XLE | -172.16 |
| XLF | -4,362.42 |
| XLY | -6,896.31 |

## Regime-conditional stats

| Regime | N | Win rate | P&L ($) |
|---|---:|---:|---:|
| Bull | 17 | 64.7% | +21,737.68 |
| Neutral | 21 | 42.9% | +502.80 |
| Caution | 1 | 0.0% | -1,483.65 |

## Exit reason distribution

| Reason | Count |
|---|---:|
| trailing_stop | 24 |
| time_stop | 15 |

## Closed trades

| Exit date | Symbol | Sector | Regime | Entry | Exit | R | P&L | Reason |
|---|---|---|---|---:|---:|---:|---:|---|
| 2024-01-16 | MS | XLF | Neutral | 92.02 | 87.35 | -0.72 | -1,012.76 | trailing_stop |
| 2024-01-17 | XBI | XLV | Neutral | 88.43 | 87.72 | -0.11 | -159.96 | trailing_stop |
| 2024-01-22 | AMD | XLK | Neutral | 135.71 | 165.54 | +2.57 | +4,384.64 | trailing_stop |
| 2024-01-25 | AMGN | XLV | Neutral | 304.66 | 310.26 | +0.26 | +363.84 | time_stop |
| 2024-01-31 | AVGO | XLK | Neutral | 106.37 | 119.46 | +1.76 | +2,462.03 | trailing_stop |
| 2024-02-05 | META | XLC | Bull | 389.00 | 461.66 | +3.09 | +3,923.75 | trailing_stop |
| 2024-02-13 | AMD | XLK | Neutral | 174.27 | 171.54 | -0.16 | -322.54 | time_stop |
| 2024-02-13 | NFLX | XLC | Neutral | 56.43 | 55.45 | -0.24 | -357.98 | time_stop |
| 2024-02-13 | NOW | XLK | Bull | 154.30 | 151.65 | -0.25 | -362.98 | trailing_stop |
| 2024-02-21 | LLY | XLV | Bull | 692.08 | 738.86 | +0.97 | +1,450.21 | trailing_stop |
| 2024-03-11 | META | XLC | Neutral | 456.87 | 485.15 | +0.91 | +1,329.12 | trailing_stop |
| 2024-03-11 | NVDA | XLK | Bull | 77.51 | 90.58 | +1.72 | +3,712.40 | trailing_stop |
| 2024-03-11 | LLY | XLV | Bull | 754.90 | 744.73 | -0.20 | -295.06 | trailing_stop |
| 2024-03-28 | TMO | XLV | Bull | 587.44 | 581.21 | -0.15 | -243.02 | time_stop |
| 2024-04-02 | MU | XLK | Bull | 92.62 | 121.01 | +3.54 | +7,041.02 | trailing_stop |
| 2024-04-03 | NVDA | XLK | Bull | 86.69 | 88.96 | +0.22 | +603.70 | time_stop |
| 2024-04-18 | MU | XLK | Neutral | 120.00 | 114.09 | -0.48 | -1,206.34 | trailing_stop |
| 2024-04-19 | ORCL | XLK | Bull | 121.86 | 115.15 | -0.79 | -1,348.79 | trailing_stop |
| 2024-04-25 | RTX | XLI | Bull | 99.84 | 101.71 | +0.27 | +457.56 | time_stop |
| 2024-05-01 | XOM | XLE | Neutral | 117.29 | 116.03 | -0.15 | -261.33 | time_stop |
| 2024-05-14 | CVX | XLE | Neutral | 163.00 | 163.61 | +0.05 | +89.17 | time_stop |
| 2024-05-21 | TSLA | XLY | Neutral | 186.98 | 186.60 | -0.02 | -48.64 | time_stop |
| 2024-06-07 | AMGN | XLV | Bull | 308.25 | 305.02 | -0.15 | -248.65 | time_stop |
| 2024-06-07 | GOOGL | XLC | Bull | 173.38 | 174.46 | +0.09 | +148.82 | time_stop |
| 2024-06-13 | GE | XLI | Bull | 153.39 | 157.36 | +0.33 | +631.04 | trailing_stop |
| 2024-06-21 | NVDA | XLK | Bull | 111.62 | 130.91 | +1.88 | +4,146.02 | trailing_stop |
| 2024-07-11 | NFLX | XLC | Bull | 63.60 | 64.87 | +0.28 | +476.74 | trailing_stop |
| 2024-07-18 | AAPL | XLK | Bull | 187.22 | 225.37 | +2.91 | +4,883.11 | trailing_stop |
| 2024-07-24 | TSLA | XLY | Bull | 246.48 | 215.64 | -1.00 | -3,238.19 | trailing_stop |
| 2024-08-05 | SPGI | XLF | Neutral | 477.57 | 467.74 | -0.29 | -521.00 | trailing_stop |
| 2024-08-05 | TSLA | XLY | Neutral | 227.46 | 201.03 | -0.81 | -2,933.22 | trailing_stop |
| 2024-09-10 | NKE | XLY | Neutral | 82.59 | 78.02 | -0.79 | -1,368.43 | trailing_stop |
| 2024-09-10 | JPM | XLF | Caution | 215.89 | 202.88 | -0.86 | -1,483.65 | trailing_stop |
| 2024-09-19 | LLY | XLV | Neutral | 937.40 | 915.04 | -0.34 | -581.35 | time_stop |
| 2024-09-25 | V | XLF | Neutral | 284.67 | 268.66 | -0.80 | -1,345.01 | trailing_stop |
| 2024-10-01 | ORCL | XLK | Neutral | 166.92 | 167.16 | +0.02 | +34.07 | time_stop |
| 2024-10-10 | SBUX | XLY | Neutral | 91.32 | 93.88 | +0.40 | +692.17 | time_stop |
| 2024-10-16 | NOW | XLK | Neutral | 179.69 | 183.77 | +0.37 | +538.56 | time_stop |
| 2024-11-13 | DE | XLI | Neutral | 379.49 | 391.04 | +0.43 | +727.76 | trailing_stop |
