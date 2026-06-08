---
description: Market-open execution — place planned trades + trailing stops
---

Local run of the market-open workflow. Resolve today's date: `DATE=$(date +%Y-%m-%d)`.

STEP 0a — **Sync to latest main BEFORE any other step.**
```
git pull --rebase origin main
```
The cloud sandbox starts on a fresh `claude/*` feature branch that may NOT
include commits other routines pushed since the sandbox snapshot was taken.
Without this pull, STEP 1's memory reads can see stale RESEARCH-LOG /
TRADE-LOG. Real incident 2026-05-28: market-open silently halted at STEP 1
("today's RESEARCH-LOG missing") because pre-market had committed it 46 min
earlier and the market-open sandbox did not include that commit. Pull is
idempotent and takes <2s. If it fails (merge conflict — should never happen
on a fresh sandbox clone), abort with WhatsApp: "ROUTINE git pull failed".

STEP 0 — System kill switches FIRST. If any of these fire, do not proceed.
```
# Drawdown lock — if memory/LOCK exists, refuse all orders.
python scripts/risk_gates.py lock-status
# Exit 42 = locked → send WhatsApp alert and STOP.

# Daily/weekly account-level circuit breakers.
python scripts/risk_gates.py check

# Re-resolve regime (it can flip between pre-market and open).
python scripts/ml_insights.py resolve
```
Parse the JSON outputs.
- If `entries_blocked` is true → do not place buys today (but you may still place protective stops if currently missing).
- If `tighten_trails` is true → tighten every trailing stop's trail_percent by 30% (e.g., 10% → 7%), but a tighten must NEVER lower the absolute stop. Cancel+replace resets the HWM, so gate each one through `python scripts/trail_tighten.py safe-stop --old-stop S_old --current PRICE --new-pct PCT` and follow its `action` (see midday STEP 4).
- If `lock_file_present` is true → send WhatsApp "LOCK file present, drawdown lock active" and STOP.
- If `market.regime == "Defensive"` (from ml_insights resolve) → **skip all new entries today** even if pre-market had ideas. Existing positions stay; only protective sells allowed.
- Compare the regime resolved here against the one in today's RESEARCH-LOG header. If they differ, log the flip and downgrade the day's `trade_slots` to the minimum of both values (conservative posture).

STEP 1 — Read memory for today's plan:
- `memory/TRADING-STRATEGY.md`
- TODAY's entry in `memory/RESEARCH-LOG.md` (if missing, run `/pre-market` first — never trade without documented research)
- Tail of `memory/TRADE-LOG.md` (for weekly trade count)
- `python scripts/research.py macro` — today's macro paragraph (single read; cheap)
- For each ticker in today's plan: `python scripts/research.py ticker-notes SYM` — running dossier (so you enter consistent with the bot's thesis on that name, not just the morning's catalyst)

STEP 2 — Re-validate with live data:
```
bash scripts/alpaca.sh account
bash scripts/alpaca.sh positions
bash scripts/alpaca.sh quote <each planned ticker>
```

STEP 3 — Hard-check rules BEFORE every order. Skip any trade that fails and log the reason:
- Symbol is in the trading universe: `python scripts/universe.py is_member SYM` (exit 0 = allowed). Symbols outside the universe are FORBIDDEN — log and skip.
- Symbol is NOT already an open position AND NOT already a PENDING order (`python scripts/trade_log.py list-pending` to check). Duplicate entries would be unintended pyramiding (Phase H, deferred).
- Total positions after trade ≤ 6 (PENDING orders do NOT count yet; only filled OPEN positions)
- Trades this week ≤ 3 (count CLOSED + OPEN lines only — PENDING-not-yet-filled does not consume a slot)
- Position cost ≤ 20% of equity
- Catalyst documented in today's RESEARCH-LOG
- `daytrade_count` leaves room (PDT: 3/5 rolling business days)
- Entry passes `entries_blocked` check from STEP 0
- **Gap guard (Phase G3)** — read the planned entry from today's RESEARCH-LOG candidate block (the **R:R math** line). Compare to current ask:
  - `current > planned × 1.03` (gap up >3% past plan) → SKIP. Append `- SKIPPED YYYY-MM-DD: SYM reason=gap_above_plan current=$X planned=$Y` to TRADE-LOG and add to watchlist for tomorrow:
    `python scripts/watchlist.py add SYM --setup <setup> --entry <planned> --stop <initial_stop> --thesis "<short>"`
  - `current < planned × 0.97` (gap down >3% below plan) → PROCEED but recompute `stop_pct` (the gap broadens the realized ATR%) and place the limit at the new lower ask, not the stale planned price.
- **Earnings blackout (A4)** — `python scripts/market_data.py earnings SYM`. If `in_blackout` is true AND the documented catalyst is NOT earnings, SKIP this trade.
- **Correlation cap (A3)** — for each candidate SYM, run:
  ```
  python scripts/market_data.py max-correlation-with SYM <existing_sym_1> <existing_sym_2> ...
  ```
  If `max_correlation > 0.70`, SKIP this trade (the candidate is too redundant with what we already hold). If there are no existing positions, this check is a no-op.
- **Sector cap (Phase C finding)** — for each candidate SYM, look up its sector and count how many existing positions are in the same sector:
  ```
  CAND_SECTOR=$(python scripts/universe.py sector SYM)
  # count existing positions whose sector matches CAND_SECTOR
  ```
  If `count >= 2`, SKIP — backtest sweep showed this single rule adds +5-6pp of return over 2 years by preventing sector concentration. BROAD ETFs (SPY/QQQ/IWM/DIA) are exempt from this cap.

STEP 4 — Compute the **ATR-based stop width** for each accepted candidate (Phase A2):
```
python scripts/market_data.py stop-for-entry SYM
```
Capture the `stop_pct` (clamped to [7, 15]) and the `stop_price`. This replaces the fixed 10% rule.

STEP 4b — Compute the **position size** per Phase D4 (Half-Kelly when N≥30, else flat 20%):
```
python scripts/risk_gates.py check          # capture current_equity
python scripts/sizing.py recommend <regime> <equity>
```
Use `size_dollars` from the JSON output to compute shares: `shares = floor(size_dollars / ask_price)`. The output's `method` field will be either `"flat_20pct"` or `"half_kelly"` — log this verbatim into TRADE-LOG.

If `method == "half_kelly"` AND this is the first trade after the switchover (yesterday's TRADE-LOG showed `method=flat_20pct`), send a one-off WhatsApp alert: `"Half-Kelly sizing now ACTIVE — W=X.XX, R=Y.YY, expectancy=Z.ZZ"`.

STEP 5 — Place the entry as a single **OTO** order (Phase G1). The entry leg's shape depends on the **Setup type** label in today's RESEARCH-LOG candidate block. Alpaca arms the trailing stop on entry fill — no separate stop placement step needed.

**PULLBACK** — buy-limit at planned entry:
```
bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"N","side":"buy","type":"limit","limit_price":"<planned_entry>","time_in_force":"day","order_class":"oto","stop_loss":{"trail_percent":"<stop_pct from STEP 4>"}}'
```

**BREAKOUT** — buy-stop above resistance:
```
bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"N","side":"buy","type":"stop","stop_price":"<resistance × 1.001>","time_in_force":"day","order_class":"oto","stop_loss":{"trail_percent":"<stop_pct from STEP 4>"}}'
```

**MOMENTUM** — market at open (reserved for binary-event days):
```
bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"N","side":"buy","type":"market","time_in_force":"day","order_class":"oto","stop_loss":{"trail_percent":"<stop_pct from STEP 4>"}}'
```

Capture the returned `id` (parent order_id) for the PENDING line.

PDT-rejection fallback: replace `"trail_percent": "X"` with `"stop_price": "<stop_price from STEP 4>"` (fixed stop child). If also blocked, submit the entry alone (no OTO), record PENDING with `stop=PDT-blocked-set-tomorrow`.

If `scripts/alpaca.sh` exits 42 (failsafe), STOP, send WhatsApp alert, do not retry.

STEP 6 — Append to `memory/TRADE-LOG.md`:

1. Canonical **PENDING** line (promoted to OPEN on fill by daily-summary):
   ```
   - PENDING YYYY-MM-DD: SYM order_id=<id from STEP 5> type=<limit|stop|market> entry=PLANNED_PRICE initial_stop=STOP_PRICE shares=N regime_entry=REGIME sector=XL? sizing=METHOD thesis="..."
   ```
   Fields:
   - `order_id` = parent order id from STEP 5.
   - `type` = limit (PULLBACK), stop (BREAKOUT), or market (MOMENTUM).
   - `entry` = planned price (daily-summary overwrites with realized fill).
   - `initial_stop` = derived from `stop_pct` × planned entry (STEP 4). **Never change this value** — R-multiple math depends on the original level.
   - `regime_entry` = today's resolved regime.
   - `sector` = `python scripts/universe.py sector SYM`.
   - `sizing` = `method` from STEP 4b.
   - `thesis` = short quoted string.

2. For MOMENTUM market orders that fill immediately, ALSO append the canonical OPEN line right away (so midday and others don't wait):
   ```
   - OPEN YYYY-MM-DD: SYM order_id=<id> entry=FILL_PRICE initial_stop=STOP_PRICE shares=N regime_entry=REGIME sector=XL? sizing=METHOD thesis="..." (carries forward from PENDING)
   ```

3. The usual prose summary block (Setup type, ATR, stop_pct, target, R:R, full thesis).

STEP 7 — Notification (if an order was placed, even pending):
```
bash scripts/whatsapp.sh << 'WAEOF'
<tickers, shares, order type, planned entry, trail %, fill status — heredoc>
WAEOF
```
