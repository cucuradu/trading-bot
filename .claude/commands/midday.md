---
description: Midday scan — cut losers, tighten winner stops, thesis check
---

Local run of the midday scan. Resolve today's date: `DATE=$(date +%Y-%m-%d)`.

STEP 1 — Read memory:
- `memory/TRADING-STRATEGY.md` (exit rules)
- Tail of `memory/TRADE-LOG.md` (entries, original thesis per position, stops)
- Today's `memory/RESEARCH-LOG.md` entry

STEP 2 — Pull current state:
```
bash scripts/alpaca.sh positions
bash scripts/alpaca.sh orders
```

STEP 3 — Cut losers immediately. For every position with `unrealized_plpc ≤ -0.07`:
```
bash scripts/alpaca.sh close SYM
bash scripts/alpaca.sh cancel ORDER_ID    # cancel its trailing stop
```
Log the exit to TRADE-LOG: exit price, realized P&L, "cut at −7% per rule".

STEP 4 — Tighten trailing stops on winners. For each eligible position, cancel the old trailing stop and place a new one:
- Up ≥ +20% → `trail_percent: "5"`
- Up ≥ +15% → `trail_percent: "7"`

Never tighten within 3% of current price. Never move a stop down.

STEP 5 — Thesis check. If a thesis broke intraday, cut the position even if not at −7% yet. Document reasoning in TRADE-LOG.

STEP 6 — Optional intraday research via `scripts/gemini.sh` if something is moving sharply with no obvious cause. Append an afternoon addendum to RESEARCH-LOG.

STEP 7 — Notification (only if action was taken):
```
bash scripts/whatsapp.sh "<action summary>"
```

If `scripts/alpaca.sh` exits 42 (failsafe), STOP, send WhatsApp alert, do not retry.
