---
description: Manual trade helper with strategy-rule validation. Usage — /trade SYMBOL SHARES buy|sell
---

Execute a manual trade with full rule validation. Refuse if any rule fails.

Args: `SYMBOL SHARES SIDE` (buy or sell). If missing, ask.

0. System kill switches FIRST:
   ```
   python scripts/risk_gates.py lock-status        # exit 42 = LOCK present → STOP
   python scripts/risk_gates.py check              # parse JSON
   python scripts/universe.py is_member SYMBOL     # exit 1 = not in universe → STOP
   ```
   For BUY: if `entries_blocked` is true OR universe membership fails → refuse with the reason. Sells of existing positions are allowed even when entries are blocked (you still need to be able to defend capital).

1. Pull state: `bash scripts/alpaca.sh account`, `bash scripts/alpaca.sh positions`, `bash scripts/alpaca.sh quote SYMBOL` (capture ask price P).

1b. **Surface prior research** before validating — this is the bot's running thesis on the ticker; do NOT propose a buy that contradicts it without acknowledging the contradiction:
   ```
   python scripts/research.py ticker-notes SYMBOL    # running per-ticker dossier
   python scripts/research.py latest-on SYMBOL 7     # last 7 days of RESEARCH-LOG mentions
   python scripts/research.py macro                  # latest macro paragraph
   ```
   If the ticker-notes Thesis line is older than 7 days OR conflicts with the user's reason for trading, REFUSE and ask the user to re-run `/pre-market` so the thesis is current. (Prevents stale-thesis trades that we'd regret.)

2. For BUY, validate the buy-side gate from `memory/TRADING-STRATEGY.md`:
   - Symbol in TRADING_UNIVERSE (already checked in step 0)
   - Total positions after fill ≤ 6
   - Trades this week + 1 ≤ 3
   - SHARES × P ≤ 20% of equity
   - SHARES × P ≤ available cash
   - `daytrade_count` < 3
   - Catalyst documented in today's `memory/RESEARCH-LOG.md` (ask for thesis if missing)
   - **Earnings (A4)**: `python scripts/market_data.py earnings SYMBOL` — if `in_blackout` is true AND catalyst is NOT earnings, refuse.
   - **Correlation (A3)**: if there are existing positions, run:
     ```
     python scripts/market_data.py max-correlation-with SYMBOL <existing_1> <existing_2> ...
     ```
     If `max_correlation > 0.70`, refuse.
   - **Sector cap (Phase C)**: `python scripts/universe.py sector SYMBOL` → look up the candidate's sector. Count existing Alpaca positions in the same sector. If `count >= 2`, refuse. BROAD ETFs (SPY/QQQ/IWM/DIA) are exempt.
   If any fail, STOP and print the failed checks.
3. For SELL, confirm position exists with right qty. No other checks.
4. **Compute ATR stop (A2) for BUYs:**
   ```
   python scripts/market_data.py stop-for-entry SYMBOL
   ```
   Capture `stop_pct` (clamped to [7, 15]) and `stop_price`.
4b. **Compute position size (D4):** read equity from `risk_gates.py check`, get the resolved regime from `ml_insights.py resolve`, then:
   ```
   python scripts/sizing.py recommend <regime> <equity>
   ```
   Use `size_dollars` to derive shares (`floor(size_dollars / ask_price)`). If the user passed an explicit SHARES arg that disagrees with the recommendation by more than 20%, ask for confirmation before placing the order.
5. Print the order JSON + validation results + ATR-based stop + sizing audit, ask "execute? (y/n)".
6. On confirm:
   ```
   bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"N","side":"buy|sell","type":"market","time_in_force":"day"}'
   ```
7. For BUYs, immediately place the ATR-based trailing stop GTC:
   ```
   bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"N","side":"sell","type":"trailing_stop","trail_percent":"<stop_pct>","time_in_force":"gtc"}'
   ```
8. Append to `memory/TRADE-LOG.md`:
   - The canonical OPEN line (same format as market-open skill, Phase D1) — needed so exit-side R-multiple computation works:
     `- OPEN YYYY-MM-DD: SYM entry=PRICE initial_stop=STOP_PRICE shares=N regime_entry=REGIME sector=XL? sizing=METHOD thesis="..."`
   - The prose summary (ATR, stop_pct, target, R:R, full thesis paragraph).
   For SELLs of an existing position: write the canonical CLOSED line (look up the matching OPEN line for entry/initial_stop/regime/sector).
9. `bash scripts/whatsapp.sh "<trade details one-liner>"`.

If `scripts/alpaca.sh` exits 42 (failsafe), STOP, send WhatsApp alert, do not retry.
