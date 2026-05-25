---
description: End-of-day summary — EOD snapshot + WhatsApp recap
---

Local run of the daily summary. Resolve today's date: `DATE=$(date +%Y-%m-%d)`.

STEP 1 — Read memory for continuity:
- Tail of `memory/TRADE-LOG.md` (find most recent EOD snapshot → yesterday's equity)
- Count TRADE-LOG entries dated today (for "Trades today")
- Count trades Mon–today this week (for the 3/week cap)

STEP 2 — Pull final state of the day:
```
bash scripts/alpaca.sh account
bash scripts/alpaca.sh positions
bash scripts/alpaca.sh orders
```

STEP 3 — Compute metrics:
- Day P&L ($ and %) = today_equity − yesterday_equity
- Phase cumulative P&L ($ and %) = today_equity − starting_equity ($100,000)
- Trades today (list or "none")
- Trades this week (running total)

STEP 4 — Append EOD snapshot to `memory/TRADE-LOG.md`. Include a single-line EOD marker that risk_gates.py can parse for tomorrow's daily-DD check:

```
### MMM DD — EOD Snapshot (Day N, Weekday)
- EOD YYYY-MM-DD: equity $X,XXX.XX
**Portfolio:** $X | **Cash:** $X (X%) | **Day P&L:** ±$X (±X%) | **Phase P&L:** ±$X (±X%)

| Ticker | Shares | Entry | Close | Day Chg | Unrealized P&L | Stop |

**Notes:** one-paragraph plain-english summary.
```

The `- EOD YYYY-MM-DD: equity $X,XXX.XX` line is REQUIRED and machine-read by `scripts/risk_gates.py` — keep the exact format (ISO date, dollar sign, comma thousands separator allowed).

STEP 4b — Update peak-equity watermark (Phase A1 drawdown lock):
```
python scripts/risk_gates.py update-peak <today_equity>
```
This is a no-op if today's equity is not a new high. If a new high, `memory/PEAK-EQUITY.txt` gets bumped.

STEP 4c — Log today's resolved regime (Phase B). Read it from today's RESEARCH-LOG header. Include the source + transition flag in the EOD snapshot so the weekly review can audit:
```
- Regime YYYY-MM-DD: <Bull|Neutral|Caution|Defensive> (source: <ml|rule_fallback>, slots: N)
```

If the regime is different from yesterday's (look back one EOD snapshot), append a one-line "Regime flip: Yesterday → Today" note and include it in the WhatsApp recap.

STEP 4d — Reconcile closed positions (Phase D1). Compare today's `bash scripts/alpaca.sh positions` with yesterday's. For each symbol that was open yesterday but is NOT in today's positions:
- Read the matching OPEN line from TRADE-LOG (search for the most recent `- OPEN ...: SYM ...`).
- Compute exit price from the day's fill records (`bash scripts/alpaca.sh orders` filtered by SYM, status=filled).
- Append a canonical CLOSED line:
  ```
  - CLOSED YYYY-MM-DD: SYM entry=ENTRY exit=EXIT initial_stop=STOP shares=N regime_entry=REGIME sector=XL? pnl=$X.XX r=R.RR reason="trailing stop hit"
  ```
  (`reason` examples: "trailing stop hit", "R<=-1 (price hit initial_stop)", "thesis broken", "time stop")

Verify the parser then accepts it:
```
python scripts/trade_log.py count    # should be incremented by the number closed today
```

STEP 4e — **"Why today happened"** narrative (Gemini, free; one call):
```
bash scripts/gemini.sh "Why did the US stock market move the way it did today $DATE: sector winners + losers; key macro inputs (yields, dollar, oil); single biggest driver. Cite sources."
```
Capture a ~100-word paragraph and paste into the EOD snapshot below the metrics block, under heading **Why today**. This is the durable lesson; tomorrow's pre-market reads it.

STEP 4f — **Position updates** for each currently-held ticker:
- Compare today's news (via `python scripts/research.py latest-on SYM 2`) to the running thesis (`python scripts/research.py ticker-notes SYM`).
- For each, classify: `confirmed` / `unchanged` / `weakened` / `broken`.
- If `weakened` or `broken`, append a one-line row to that ticker's section in `memory/TICKER-NOTES.md` documenting WHY (with source).

STEP 4g — **Tomorrow's calendar**:
- `python scripts/news_sources.py finnhub-earnings 2` — confirmed earnings dates in the next 2 days.
- `bash scripts/gemini.sh "US economic calendar tomorrow: CPI/PPI/FOMC/jobs/Fed speakers — list all releases with their scheduled time ET. Cite the source."`
- Paste both into the EOD snapshot under **Tomorrow's calendar**.

STEP 4h — **Key takeaway**: write ONE sentence (≤25 words) capturing the day's most durable insight (regime change, macro shift, broken thesis, validated pattern). This is what the weekly review will compound on.

STEP 5 — Send ONE WhatsApp message (always, even on no-trade days). Now enriched: ≤ 20 lines including the day's takeaway and tomorrow's headline event:
```
bash scripts/whatsapp.sh "EOD MMM DD • <Regime>
Portfolio: \$X (±X% day, ±X% phase) vs SPY ±X%
Cash: \$X
Trades today: <list or none>
Open positions:
  SYM ±X.X% (stop \$X.XX, thesis: confirmed|weakened|broken)
Why today: <one-line distilled from the Why today paragraph>
Tomorrow's headline: <earnings/macro release with time>
Takeaway: <the STEP 4h sentence>"
```
