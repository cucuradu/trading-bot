# Backtest report — 2026-05-24-133151-compare-chandelier_3xATR22

- Window: **2024-01-01 → 2025-12-31**
- Starting equity: **$100,000.00**
- Exit strategy: **`chandelier_3xATR22`**
- Max positions: 6 | Max position %: 20%
- Circuit breakers: on | Regime gating: on | Stress shocks: off
- Drawdown lock triggered: **YES**
- Final equity: **$116,330.86** | Peak equity: $126,879.07

## Headline metrics vs. benchmarks

| Strategy | Total | Annual | Sharpe | MaxDD | Trades | WinRate | Profit Factor | Expectancy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **chandelier_3xATR22** | +16.33% | +7.89% | 0.88 | -9.88% | 45 | 62.2% | 1.93 | 0.298 |
| SPY buy-hold | +44.28% | +20.20% | 1.21 | -19.00% | — | — | — | — |
| SPY 200-SMA trend | +34.49% | +16.04% | 1.34 | -10.02% | — | — | — | — |
| Equal-weight random (5) | +22.36% | +10.66% | 0.67 | -18.39% | — | — | — | — |

## R-multiple summary

- avg_R_win: 0.771
- avg_R_loss: -0.481
- payoff_ratio: 1.60

## Sector P&L attribution

| Sector | P&L ($) |
|---|---:|
| XLC | +7,842.11 |
| XLP | +7,499.87 |
| XLK | +4,839.69 |
| XLU | +2,193.86 |
| XLV | +2,132.77 |
| XLE | +1,262.04 |
| XLRE | +491.70 |
| XLB | +261.56 |
| BROAD | -1,156.38 |
| XLF | -1,158.59 |
| XLI | -1,860.49 |
| XLY | -6,017.28 |

## Regime-conditional stats

| Regime | N | Win rate | P&L ($) |
|---|---:|---:|---:|
| Neutral | 34 | 67.7% | +19,499.22 |
| Bull | 11 | 45.5% | -3,168.36 |

## Exit reason distribution

| Reason | Count |
|---|---:|
| trailing_stop | 23 |
| time_stop | 22 |

## Closed trades

| Exit date | Symbol | Sector | Regime | Entry | Exit | R | P&L | Reason |
|---|---|---|---|---:|---:|---:|---:|---|
| 2024-01-17 | AVGO | XLK | Neutral | 108.54 | 110.37 | +0.23 | +336.54 | time_stop |
| 2024-01-17 | JPM | XLF | Neutral | 172.08 | 167.09 | -0.41 | -578.84 | time_stop |
| 2024-01-19 | CAT | XLI | Neutral | 292.71 | 285.28 | -0.36 | -505.24 | time_stop |
| 2024-01-22 | IWM | BROAD | Neutral | 199.52 | 196.54 | -0.21 | -298.00 | time_stop |
| 2024-01-23 | HD | XLY | Neutral | 345.08 | 350.78 | +0.24 | +324.90 | time_stop |
| 2024-01-31 | AVGO | XLK | Neutral | 122.05 | 119.24 | -0.32 | -454.72 | trailing_stop |
| 2024-02-05 | META | XLC | Neutral | 381.78 | 461.66 | +2.99 | +4,073.98 | trailing_stop |
| 2024-02-14 | NFLX | XLC | Neutral | 57.58 | 57.93 | +0.07 | +121.78 | time_stop |
| 2024-02-20 | NVDA | XLK | Neutral | 59.65 | 68.58 | +1.93 | +2,953.10 | trailing_stop |
| 2024-02-21 | LLY | XLV | Neutral | 630.88 | 737.26 | +2.41 | +3,297.76 | trailing_stop |
| 2024-03-08 | COST | XLP | Neutral | 650.65 | 747.73 | +2.13 | +2,912.28 | trailing_stop |
| 2024-03-11 | NVDA | XLK | Bull | 79.09 | 86.27 | +0.77 | +1,982.04 | trailing_stop |
| 2024-03-11 | META | XLC | Bull | 481.74 | 482.73 | +0.03 | +44.48 | trailing_stop |
| 2024-03-11 | LLY | XLV | Bull | 771.92 | 740.59 | -0.52 | -877.25 | trailing_stop |
| 2024-03-11 | WMT | XLP | Bull | 59.60 | 60.66 | +0.25 | +387.96 | time_stop |
| 2024-03-25 | XLB | XLB | Neutral | 45.18 | 45.70 | +0.16 | +261.56 | time_stop |
| 2024-03-25 | WMT | XLP | Neutral | 60.66 | 60.57 | -0.02 | -33.66 | time_stop |
| 2024-04-04 | NVDA | XLK | Neutral | 85.77 | 86.29 | +0.05 | +136.23 | trailing_stop |
| 2024-04-12 | DIS | XLC | Bull | 107.68 | 115.08 | +0.98 | +1,494.44 | trailing_stop |
| 2024-04-12 | JPM | XLF | Neutral | 188.29 | 186.87 | -0.11 | -169.89 | trailing_stop |
| 2024-04-25 | CAT | XLI | Neutral | 363.91 | 342.40 | -0.84 | -1,355.25 | trailing_stop |
| 2024-04-25 | META | XLC | Neutral | 500.23 | 469.23 | -0.72 | -1,425.90 | trailing_stop |
| 2024-05-03 | XOM | XLE | Neutral | 109.02 | 115.09 | +0.80 | +1,262.04 | trailing_stop |
| 2024-05-06 | KO | XLP | Neutral | 60.55 | 62.35 | +0.42 | +685.80 | time_stop |
| 2024-05-20 | NVDA | XLK | Neutral | 92.14 | 94.78 | +0.22 | +654.72 | time_stop |
| 2024-05-21 | TSLA | XLY | Neutral | 184.76 | 186.60 | +0.07 | +228.16 | time_stop |
| 2024-05-23 | AAPL | XLK | Neutral | 181.71 | 186.88 | +0.41 | +651.42 | time_stop |
| 2024-07-01 | XLU | XLU | Neutral | 31.81 | 33.90 | +0.94 | +1,521.16 | trailing_stop |
| 2024-07-17 | GOOGL | XLC | Neutral | 154.86 | 181.32 | +2.44 | +3,942.09 | trailing_stop |
| 2024-07-18 | COST | XLP | Neutral | 756.45 | 833.90 | +1.46 | +2,323.59 | trailing_stop |
| 2024-07-24 | TSLA | XLY | Bull | 251.51 | 218.75 | -0.87 | -3,210.27 | trailing_stop |
| 2024-08-02 | IWM | BROAD | Bull | 220.29 | 212.63 | -0.50 | -858.38 | trailing_stop |
| 2024-08-02 | JPM | XLF | Bull | 210.28 | 201.24 | -0.61 | -1,057.36 | trailing_stop |
| 2024-08-05 | UNH | XLV | Bull | 558.53 | 569.96 | +0.29 | +502.92 | time_stop |
| 2024-08-05 | AAPL | XLK | Bull | 223.96 | 211.05 | -0.82 | -1,419.64 | trailing_stop |
| 2024-08-05 | XLRE | XLRE | Bull | 40.91 | 40.65 | -0.09 | -157.30 | time_stop |
| 2024-08-05 | TSLA | XLY | Neutral | 232.10 | 199.48 | -0.94 | -3,360.07 | trailing_stop |
| 2024-08-26 | XLU | XLU | Neutral | 36.87 | 37.96 | +0.42 | +672.70 | time_stop |
| 2024-08-26 | MA | XLF | Neutral | 455.69 | 468.64 | +0.41 | +647.50 | time_stop |
| 2024-09-06 | LLY | XLV | Neutral | 950.53 | 896.47 | -0.63 | -1,297.46 | trailing_stop |
| 2024-09-11 | META | XLC | Neutral | 521.12 | 511.83 | -0.20 | -408.76 | time_stop |
| 2024-09-17 | UNH | XLV | Neutral | 565.29 | 577.96 | +0.31 | +506.80 | time_stop |
| 2024-10-04 | KO | XLP | Neutral | 68.17 | 70.17 | +0.42 | +670.00 | time_stop |
| 2024-10-07 | XLP | XLP | Neutral | 78.75 | 80.66 | +0.35 | +553.90 | time_stop |
| 2024-11-01 | XLRE | XLRE | Neutral | 41.56 | 42.74 | +0.41 | +649.00 | time_stop |
