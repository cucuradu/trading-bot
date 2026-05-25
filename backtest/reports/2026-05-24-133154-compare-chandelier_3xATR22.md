# Backtest report — 2026-05-24-133154-compare-chandelier_3xATR22

- Window: **2020-01-01 → 2022-12-31**
- Starting equity: **$100,000.00**
- Exit strategy: **`chandelier_3xATR22`**
- Max positions: 6 | Max position %: 20%
- Circuit breakers: on | Regime gating: on | Stress shocks: off
- Drawdown lock triggered: **YES**
- Final equity: **$132,656.38** | Peak equity: $136,093.01

## Headline metrics vs. benchmarks

| Strategy | Total | Annual | Sharpe | MaxDD | Trades | WinRate | Profit Factor | Expectancy |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| **chandelier_3xATR22** | +32.66% | +9.88% | 1.34 | -7.52% | 25 | 88.0% | 18.21 | 0.485 |
| SPY buy-hold | +17.72% | +5.59% | 0.34 | -34.10% | — | — | — | — |
| SPY 200-SMA trend | +9.91% | +3.20% | 0.31 | -19.34% | — | — | — | — |
| Equal-weight random (5) | +36.57% | +10.95% | 0.51 | -31.95% | — | — | — | — |

## R-multiple summary

- avg_R_win: 0.604
- avg_R_loss: -0.387
- payoff_ratio: 1.56

## Sector P&L attribution

| Sector | P&L ($) |
|---|---:|
| XLY | +21,362.15 |
| XLI | +7,438.08 |
| XLV | +1,171.72 |
| XLK | +921.67 |
| XLC | +767.48 |
| XLE | +511.14 |
| XLP | +286.44 |
| XLU | +197.67 |

## Regime-conditional stats

| Regime | N | Win rate | P&L ($) |
|---|---:|---:|---:|
| Caution | 12 | 100.0% | +16,689.48 |
| Neutral | 13 | 76.9% | +15,966.87 |

## Exit reason distribution

| Reason | Count |
|---|---:|
| time_stop | 11 |
| trailing_stop | 10 |
| regime_defensive | 4 |

## Closed trades

| Exit date | Symbol | Sector | Regime | Entry | Exit | R | P&L | Reason |
|---|---|---|---|---:|---:|---:|---:|---|
| 2020-01-16 | TSLA | XLY | Neutral | 30.10 | 32.90 | +1.06 | +1,855.46 | trailing_stop |
| 2020-01-21 | NFLX | XLC | Neutral | 33.58 | 33.81 | +0.10 | +135.66 | time_stop |
| 2020-01-21 | AMZN | XLY | Neutral | 95.14 | 94.60 | -0.08 | -114.24 | time_stop |
| 2020-01-27 | NVDA | XLK | Neutral | 5.93 | 6.03 | +0.26 | +360.60 | trailing_stop |
| 2020-02-03 | AAPL | XLK | Neutral | 74.95 | 76.23 | +0.24 | +339.18 | trailing_stop |
| 2020-02-05 | TSLA | XLY | Neutral | 37.20 | 55.78 | +4.20 | +10,201.01 | trailing_stop |
| 2020-02-10 | XLU | XLU | Neutral | 34.10 | 34.42 | +0.14 | +197.67 | time_stop |
| 2020-02-10 | COST | XLP | Neutral | 309.45 | 313.79 | +0.20 | +286.44 | time_stop |
| 2020-02-20 | TSLA | XLY | Neutral | 51.42 | 58.58 | +0.93 | +3,149.38 | trailing_stop |
| 2020-02-21 | MSFT | XLK | Neutral | 188.70 | 177.35 | -0.86 | -1,361.88 | trailing_stop |
| 2020-02-24 | NFLX | XLC | Neutral | 37.11 | 36.42 | -0.22 | -421.25 | trailing_stop |
| 2020-02-25 | LLY | XLV | Neutral | 132.26 | 137.52 | +0.57 | +794.12 | trailing_stop |
| 2020-02-25 | HD | XLY | Neutral | 231.19 | 237.38 | +0.38 | +544.72 | time_stop |
| 2020-05-15 | NVDA | XLK | Caution | 8.07 | 8.49 | +0.44 | +1,222.59 | regime_defensive |
| 2020-05-15 | HD | XLY | Caution | 236.56 | 239.33 | +0.11 | +271.46 | regime_defensive |
| 2020-05-19 | META | XLC | Caution | 213.18 | 216.88 | +0.17 | +399.60 | regime_defensive |
| 2020-05-19 | NVDA | XLK | Caution | 8.75 | 8.81 | +0.05 | +148.29 | regime_defensive |
| 2020-05-26 | TSLA | XLY | Caution | 54.09 | 54.59 | +0.06 | +216.28 | time_stop |
| 2020-05-28 | XLE | XLE | Caution | 19.05 | 19.47 | +0.15 | +511.14 | time_stop |
| 2020-06-02 | HD | XLY | Caution | 245.35 | 252.71 | +0.30 | +699.20 | time_stop |
| 2020-06-04 | UNH | XLV | Caution | 293.36 | 298.08 | +0.15 | +377.60 | time_stop |
| 2020-06-09 | META | XLC | Caution | 232.20 | 238.67 | +0.28 | +653.47 | time_stop |
| 2020-06-10 | BA | XLI | Caution | 151.39 | 199.07 | +2.10 | +7,438.08 | trailing_stop |
| 2020-06-11 | NVDA | XLK | Caution | 8.72 | 8.80 | +0.07 | +212.89 | time_stop |
| 2020-06-11 | TSLA | XLY | Caution | 54.59 | 65.07 | +1.33 | +4,538.88 | trailing_stop |
