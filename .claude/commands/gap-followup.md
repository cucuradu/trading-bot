---
description: Promote yesterday's gap-guard SKIPPED entries to the watchlist. Idempotent.
---

Sweep `memory/TRADE-LOG.md` for `- SKIPPED YYYY-MM-DD: SYM reason=gap_above_plan ...`
lines from the last trading day that aren't already on the watchlist, and add
them so the next `/pre-market` can re-evaluate at the original planned price.

This is a daily-summary helper. The main daily-summary already does this for
*today's* skips; this skill exists for manual catch-up (e.g., after a routine
failure) and for inspection.

1. **Resolve last trading day**:
   ```
   LAST=$(python scripts/trading_calendar.py previous-trading-day 2>/dev/null || date -v-1d +%Y-%m-%d)
   ```
   (Fall back to yesterday calendar-date if the helper isn't present.)

2. **Find candidate SKIPPED lines from `LAST`**:
   ```
   grep "^- SKIPPED $LAST:" memory/TRADE-LOG.md
   ```
   If none → print "no skips to follow up" and stop.

3. **Read current watchlist** to avoid duplicates:
   ```
   python scripts/watchlist.py list
   ```

4. **For each SKIPPED line not already on the watchlist**:
   - Parse: `SYM`, `planned` (from `planned=$Y` field).
   - Look up the matching candidate block in `memory/RESEARCH-LOG.md` entry for `LAST` to recover `setup`, `initial_stop`, and `thesis`.
   - If any of those are missing in the log, skip with a warning — do not invent values.
   - Otherwise add:
     ```
     python scripts/watchlist.py add SYM \
       --setup <PULLBACK|BREAKOUT|MOMENTUM> \
       --entry <planned> \
       --stop <initial_stop> \
       --thesis "<short>"
     ```

5. **Hard cap**: `watchlist.py add` enforces the 6-entry cap. If it refuses, print which symbols couldn't be added and stop — do NOT drop other entries to make room.

6. **Output**: short summary table:
   ```
   Promoted: SYM1 (planned $X), SYM2 (planned $Y)
   Skipped (already on list): SYM3
   Skipped (incomplete RESEARCH-LOG): SYM4
   Watchlist size now: N / 6
   ```

No orders, no notification, no commit.