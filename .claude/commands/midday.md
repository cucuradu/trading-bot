---
description: Midday scan — cut losers, tighten winner stops, thesis check
---

Local run of the midday scan. Resolve today's date: `DATE=$(date +%Y-%m-%d)`.

STEP 0 — System kill switches FIRST.
```
python scripts/risk_gates.py lock-status     # exit 42 = LOCK present, send WhatsApp and STOP
python scripts/risk_gates.py check           # parse JSON
```
If `lock_file_present` is true → only allow protective sells (close positions / cancel stops); refuse any buy. If `tighten_trails` is true → reduce every existing trailing stop trail_percent by 30%. If `daily_dd_response == "freeze_entries_48h"` → close all positions currently in profit (this is the daily −3% response).

If `lock_auto_recovered` is present in the `check` JSON (Phase C auto-recovery cleared the LOCK on this run), include the value as a single line in the STEP 7 WhatsApp alert ("LOCK auto-recovered: <reason>") so the user notices the bot is trading again.

STEP 1 — Read memory:
- `memory/TRADING-STRATEGY.md` (exit rules)
- Tail of `memory/TRADE-LOG.md` (entries, original thesis per position, stops)
- Today's `memory/RESEARCH-LOG.md` entry

STEP 2 — Pull current state:
```
bash scripts/alpaca.sh positions
bash scripts/alpaca.sh orders
```

STEP 3 — Cut losers at R ≤ −1 (Phase C). For each open position, look up the matching `- OPEN ...: SYM ...` line in `memory/TRADE-LOG.md` to recover its `initial_stop`. If `current_price ≤ initial_stop` (i.e., R ≤ −1, the trade has hit its planned stop width), close the position immediately at market — do NOT wait for the GTC trailing stop, which can slip past the level in fast tape:
```
bash scripts/alpaca.sh close SYM
bash scripts/alpaca.sh cancel ORDER_ID    # cancel its trailing stop
```
This replaces the pre-Phase-C fixed −7% cut. The R ≤ −1 rule respects the ATR-based stop width (typically 7–15%), so wider-volatility names get the room they need while tight-volatility names exit faster. PHASE-C-FINDINGS.md confirms this is a small positive in bull regimes and necessary in bear regimes (where wider ATR stops would otherwise be undercut by a flat threshold).

Log the exit to TRADE-LOG with the canonical CLOSED line (Phase D1) on its own line — `scripts/trade_log.py` parses these:
```
- CLOSED YYYY-MM-DD: SYM entry=ENTRY exit=EXIT initial_stop=STOP shares=N regime_entry=REGIME sector=XL? pnl=$X.XX r=R.RR reason="R<=-1 (price hit initial_stop)"
```
Fields:
- `entry`, `initial_stop`, `shares`, `regime_entry`, `sector` come from the original entry row in TRADE-LOG (look it up).
- `exit` is the realized fill price.
- `pnl` = (exit − entry) × shares.
- `r` = (exit − entry) / (entry − initial_stop), rounded to 2 dp. A cut at R ≤ −1 yields `r ≈ -1.0` (slightly worse if the market gapped through the stop level).
- `reason` is a short free-form quoted string.
Underneath, append the usual prose summary for context.

STEP 4 — Tighten trailing stops on winners. For each eligible position, cancel the old trailing stop and place a new one. ATR-aware (Phase A2):

```
# Optional: recompute ATR-based trail width for the current price
python scripts/market_data.py atr SYM   # use stop_pct_1_75x at +15%, stop_pct_1_25x at +20%
```

- Up ≥ +20% → `trail_percent: max(5, stop_pct_1_25x)` (cap at 5% per legacy rule; ATR may widen)
- Up ≥ +15% → `trail_percent: max(7, stop_pct_1_75x)` (cap at 7% per legacy rule; ATR may widen)
- If `tighten_trails` was true in STEP 0 (daily DD ≤ −2%), apply an additional 30% tightening to every active trail.

Never tighten within 3% of current price. Never move a stop down.

STEP 4b — Time stop (Phase A5). For each open position, parse the entry date from `memory/TRADE-LOG.md`. If the position has been open for **≥ 10 trading days** AND `unrealized_plpc` is between **−3% and +3%** (inclusive), close it. Free up capital that's doing nothing.

```
bash scripts/alpaca.sh close SYM
bash scripts/alpaca.sh cancel ORDER_ID   # cancel its trailing stop
```

Log the exit to TRADE-LOG with the canonical CLOSED line (Phase D1, same format as STEP 3), `reason="time stop — 10+ trading days flat"`.

STEP 5 — Thesis check. If a thesis broke intraday, cut the position even if not at −7% yet. Document reasoning in TRADE-LOG and write a canonical CLOSED line with `reason="thesis broken — <short note>"`.

STEP 6 — Optional intraday research via `scripts/gemini.sh` if something is moving sharply with no obvious cause. Append an afternoon addendum to RESEARCH-LOG.

STEP 7 — Notification (only if action was taken):
```
bash scripts/whatsapp.sh << 'WAEOF'
<action summary — heredoc so $ amounts pass through bash literally>
WAEOF
```

If `scripts/alpaca.sh` exits 42 (failsafe), STOP, send WhatsApp alert, do not retry.
