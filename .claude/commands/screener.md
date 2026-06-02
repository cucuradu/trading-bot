---
description: Ad-hoc universe ranking — re-run the screener outside pre-market. Usage — /screener [shortlist|explain SYM]
---

Run the Phase-A7 screener on demand (the same engine `pre-market` uses).
Read-only. No orders, no file writes.

Args (optional, default `shortlist`):
- `shortlist` — top-K deep-dive list, filtered by sector regime + open positions.
- `rank` — full 70-ticker universe ranking with diagnostics.
- `explain SYM` — per-factor breakdown for one ticker.

1. **Resolve current regime** (so slots + sector filter match what the bot would actually do):
   ```
   python scripts/ml_insights.py resolve
   ```
   Capture `market.trade_slots` and `sectors.*` regimes.

2. **Pull existing position symbols** so the shortlist excludes what's already held:
   ```
   bash scripts/alpaca.sh positions | jq -r '.[].symbol' | paste -sd,
   ```

3. **Run the screener** with the right subcommand:
   - `shortlist`:
     ```
     python scripts/screener.py shortlist --slots <trade_slots> --open <existing_csv>
     ```
   - `rank`:
     ```
     python scripts/screener.py rank --top 15
     ```
   - `explain SYM`:
     ```
     python scripts/screener.py explain SYM
     ```

4. **If today is a macro day** (FOMC/CPI/PPI/PCE/NFP within next 2 trading days), add `--macro-day`:
   ```
   python scripts/trading_calendar.py pre-macro-event | jq -r '.cap_active'
   ```
   `true` → re-run step 3 with `--macro-day` so the defensive factor weights apply.

5. **Print** the screener's JSON output verbatim, plus a one-line summary:
   - shortlist size, top symbol + ml_score, any Bear-sector exclusions noted.

No notification. No memory writes. This skill exists to inspect screener output between routines — promotion to a real trade happens via `/trade` or the next `/market-open` run.