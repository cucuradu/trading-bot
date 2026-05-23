---
description: Pre-market research — write today's trade ideas to RESEARCH-LOG.md
---

Local run of the pre-market workflow. Resolve today's date: `DATE=$(date +%Y-%m-%d)`.

STEP 1 — Read memory for context:
- `memory/TRADING-STRATEGY.md`
- Tail (~100 lines) of `memory/TRADE-LOG.md`
- Tail (~100 lines) of `memory/RESEARCH-LOG.md`

STEP 2 — Pull live paper account state:
```
bash scripts/alpaca.sh account
bash scripts/alpaca.sh positions
bash scripts/alpaca.sh orders
```

STEP 3 — Market context via Gemini (free tier, max 5 queries to conserve token budget):
```
bash scripts/gemini.sh "WTI crude oil price right now and major moves today"
bash scripts/gemini.sh "S&P 500 futures premarket today $DATE plus VIX level"
bash scripts/gemini.sh "Top stock market catalysts and earnings before market open $DATE"
bash scripts/gemini.sh "US economic calendar today $DATE: CPI PPI FOMC jobs data"
bash scripts/gemini.sh "Recent news on currently-held tickers: <list from positions>"
```
If `scripts/gemini.sh` exits 3, fall back to native WebSearch and note the fallback in the log entry.

Also use `python scripts/yfinance.py sector-momentum` for the sector picture (no API quota).

STEP 4 — Write a dated entry to `memory/RESEARCH-LOG.md` following the template at the top of that file:
- Account snapshot
- Market context
- 2–3 actionable trade ideas (each with catalyst, entry, stop, target, R:R)
- Risk factors
- Decision: TRADE or HOLD (default HOLD)

STEP 5 — Notification (silent unless urgent: held position already < −7% pre-market, or thesis broken overnight, or major geopolitical event):
```
bash scripts/whatsapp.sh "<one-line alert>"
```
