# IBD Distribution Day Monitor Report

- **As of:** 2026-06-03
- **Overall Risk Level:** **HIGH**
- **Primary Signal Symbol:** SPY
- **Generated At:** 2026-06-03T23:55:32+00:00

## Index Results

### SPY — risk: **HIGH**

- Today is Distribution Day: True
- d5 / d15 / d25 = 1 / 3 / 3
- Cluster: 5/15/25セッション経過以内: 1/3/3
- Trend filters: close_above_21ema=True, close_above_50sma=True, market_below_21ema_or_50ma=False

> SPYは本日Distribution Day該当。 5/15/25セッション経過以内の有効Distribution Dayはそれぞれ 1/3/3 件。 リスク判定: HIGH。

#### Active Distribution Days

| date | close | pct_change | volume_change_pct | age | expires_in | high_since | invalidation_price |
|------|-------|------------|-------------------|-----|------------|------------|---------------------|
| 2026-06-03 | 754.24 | -0.70% | 38.44% | 0 | 25 | 758.8 | 791.952 |
| 2026-05-19 | 733.73 | -0.67% | 13.40% | 10 | 15 | 760.4 | 770.4165 |
| 2026-05-15 | 739.17 | -1.20% | 33.33% | 12 | 13 | 760.4 | 776.1285 |

## Portfolio Action

- **Instrument:** TQQQ
- **Recommended Action:** REDUCE_EXPOSURE
- **Exposure:** current 100% → target 50% (delta -50%)
- **Trailing Stop:** 5%
- **Alternative:** SWITCH_PARTIAL_TO_QQQ

> TQQQ targets 3x daily Nasdaq returns. Distribution Day clusters amplify drawdown risk via daily compounding, so exposure is cut faster than for unleveraged QQQ.

## Audit

- **Data Source:** fmp
- **Symbols:** SPY
- **Audit Flags:** ['no_data_returned']
- **Rule Version:** ibd_dd_v1.0

