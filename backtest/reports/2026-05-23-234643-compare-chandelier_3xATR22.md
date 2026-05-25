# Backtest report — 2026-05-23-234643-compare-chandelier_3xATR22

- Window: **2024-01-01 → 2025-12-31**
- Starting equity: **$100,000.00**
- Exit strategy: **`chandelier_3xATR22`**
- Max positions: 6 | Max position %: 20%
- Circuit breakers: on | Regime gating: on | Stress shocks: off
- Drawdown lock triggered: **YES**
- Final equity: **$105,862.92** | Peak equity: $121,384.09

## Headline metrics vs. benchmarks

| Strategy | Total | Annual | Sharpe | MaxDD | Trades | WinRate | Profit Factor | Expectancy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **chandelier_3xATR22** | +5.86% | +2.90% | 0.36 | -13.10% | 51 | 47.1% | 1.25 | 0.146 |
| SPY buy-hold | +44.28% | +20.20% | 1.21 | -19.00% | — | — | — | — |
| SPY 200-SMA trend | +34.49% | +16.04% | 1.34 | -10.02% | — | — | — | — |
| Equal-weight random (5) | +22.36% | +10.66% | 0.67 | -18.39% | — | — | — | — |

## R-multiple summary

- avg_R_win: 0.803
- avg_R_loss: -0.439
- payoff_ratio: 1.83

## Sector P&L attribution

| Sector | P&L ($) |
|---|---:|
| XLC | +6,849.00 |
| XLP | +4,451.29 |
| XLK | +2,549.25 |
| XLU | +2,172.16 |
| XLV | +2,151.30 |
| XLRE | +477.62 |
| XLB | +261.56 |
| XLE | -275.31 |
| BROAD | -1,125.72 |
| XLF | -1,463.90 |
| XLI | -2,693.77 |
| XLY | -7,490.55 |

## Regime-conditional stats

| Regime | N | Win rate | P&L ($) |
|---|---:|---:|---:|
| Neutral | 35 | 51.4% | +11,264.12 |
| Caution | 5 | 20.0% | -2,465.41 |
| Bull | 11 | 45.5% | -2,935.78 |

## Exit reason distribution

| Reason | Count |
|---|---:|
| time_stop | 26 |
| trailing_stop | 23 |
| hard_cut | 2 |

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
| 2024-04-29 | DIS | XLC | Neutral | 112.95 | 112.08 | -0.11 | -177.48 | time_stop |
| 2024-05-03 | XOM | XLE | Neutral | 109.02 | 115.09 | +0.80 | +1,262.04 | trailing_stop |
| 2024-07-01 | XLU | XLU | Neutral | 31.81 | 33.90 | +0.94 | +1,521.16 | trailing_stop |
| 2024-07-17 | GOOGL | XLC | Neutral | 154.86 | 181.32 | +2.44 | +3,942.09 | trailing_stop |
| 2024-07-24 | TSLA | XLY | Bull | 251.51 | 218.75 | -0.87 | -3,079.24 | trailing_stop |
| 2024-08-02 | IWM | BROAD | Bull | 220.29 | 212.63 | -0.50 | -827.72 | trailing_stop |
| 2024-08-02 | JPM | XLF | Bull | 210.28 | 201.24 | -0.61 | -1,021.21 | trailing_stop |
| 2024-08-02 | TSLA | XLY | Neutral | 232.10 | 207.67 | -0.70 | -2,443.00 | hard_cut |
| 2024-08-05 | UNH | XLV | Bull | 558.53 | 569.96 | +0.29 | +480.06 | time_stop |
| 2024-08-05 | AAPL | XLK | Bull | 223.96 | 211.05 | -0.82 | -1,368.02 | trailing_stop |
| 2024-08-05 | XLRE | XLRE | Bull | 40.91 | 40.65 | -0.09 | -151.32 | time_stop |
| 2024-08-26 | XLU | XLU | Neutral | 36.87 | 37.96 | +0.42 | +651.00 | time_stop |
| 2024-08-26 | MA | XLF | Neutral | 455.69 | 468.64 | +0.41 | +621.60 | time_stop |
| 2024-09-06 | LLY | XLV | Neutral | 950.53 | 896.47 | -0.63 | -1,243.40 | trailing_stop |
| 2024-09-11 | META | XLC | Neutral | 521.12 | 511.83 | -0.20 | -390.18 | time_stop |
| 2024-09-17 | UNH | XLV | Neutral | 565.29 | 577.96 | +0.31 | +494.13 | time_stop |
| 2024-10-04 | KO | XLP | Neutral | 68.17 | 70.17 | +0.42 | +648.00 | time_stop |
| 2024-10-07 | XLP | XLP | Neutral | 78.75 | 80.66 | +0.35 | +536.71 | time_stop |
| 2024-10-11 | TSLA | XLY | Caution | 240.83 | 217.14 | -0.74 | -2,203.57 | trailing_stop |
| 2024-10-21 | AVGO | XLK | Caution | 175.08 | 179.99 | +0.26 | +628.48 | time_stop |
| 2024-10-21 | CAT | XLI | Caution | 398.25 | 390.48 | -0.28 | -435.12 | time_stop |
| 2024-10-21 | META | XLC | Caution | 584.78 | 575.16 | -0.24 | -365.56 | time_stop |
| 2024-10-21 | HD | XLY | Caution | 408.06 | 406.40 | -0.06 | -89.64 | time_stop |
| 2024-10-31 | NVDA | XLK | Neutral | 143.71 | 132.76 | -0.73 | -1,664.40 | hard_cut |
| 2024-11-01 | XLRE | XLRE | Neutral | 41.56 | 42.74 | +0.41 | +628.94 | time_stop |
| 2024-11-01 | XOM | XLE | Neutral | 124.08 | 115.39 | -1.00 | -1,537.35 | trailing_stop |
| 2024-11-04 | NFLX | XLC | Neutral | 77.21 | 75.55 | -0.28 | -468.65 | time_stop |
| 2024-11-04 | JPM | XLF | Neutral | 223.00 | 219.78 | -0.21 | -315.56 | time_stop |
| 2024-11-05 | CAT | XLI | Neutral | 390.48 | 383.37 | -0.26 | -398.16 | time_stop |
