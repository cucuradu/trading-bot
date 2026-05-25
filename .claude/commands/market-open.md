---
description: Market-open execution — place planned trades + trailing stops
---

Local run of the market-open workflow. Resolve today's date: `DATE=$(date +%Y-%m-%d)`.

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
- If `tighten_trails` is true → reduce every existing trailing stop's trail_percent by 30% (e.g., 10% → 7%).
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
- Total positions after trade ≤ 6
- Trades this week ≤ 3
- Position cost ≤ 20% of equity
- Catalyst documented in today's RESEARCH-LOG
- `daytrade_count` leaves room (PDT: 3/5 rolling business days)
- Entry passes `entries_blocked` check from STEP 0
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

STEP 5 — Execute the buys (market orders, day TIF):
```
bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"N","side":"buy","type":"market","time_in_force":"day"}'
```
Wait for fill confirmation before placing the stop.

STEP 6 — Immediately place the ATR-based trailing stop GTC for each new position:
```
bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"N","side":"sell","type":"trailing_stop","trail_percent":"<stop_pct from STEP 4>","time_in_force":"gtc"}'
```
If Alpaca rejects with PDT error, fall back to a fixed stop using the `stop_price` from STEP 4:
```
bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"N","side":"sell","type":"stop","stop_price":"<stop_price from STEP 4>","time_in_force":"gtc"}'
```
If also blocked, queue the stop in TRADE-LOG as "PDT-blocked, set tomorrow AM".

If `scripts/alpaca.sh` exits 42 (failsafe), STOP, send WhatsApp alert, do not retry.

STEP 7 — Append each trade to `memory/TRADE-LOG.md`. Write TWO things:

1. The canonical OPEN line on its own line (used by exit-side parsing to recover entry + initial_stop + regime + sector):
   ```
   - OPEN YYYY-MM-DD: SYM entry=PRICE initial_stop=STOP_PRICE shares=N regime_entry=REGIME sector=XL? sizing=METHOD thesis="..."
   ```
   Fields:
   - `entry` = realized fill price (not the pre-trade quote).
   - `initial_stop` = the `stop_price` from STEP 4. **Never change this value** — R-multiple computation on close depends on it being the original level.
   - `regime_entry` = today's resolved market regime from STEP 0 (Bull|Neutral|Caution).
   - `sector` = `python scripts/universe.py sector SYM` (XLK|XLF|.../BROAD).
   - `sizing` = `method` from STEP 4b (`flat_20pct` or `half_kelly`).
   - `thesis` = short quoted free-form string.

2. The usual prose summary block for human readability (date, ticker, ATR, stop_pct, target, R:R, full thesis paragraph).

STEP 8 — Notification (only if a trade was placed):
```
bash scripts/whatsapp.sh "<tickers, shares, fill prices, one-line why>"
```
