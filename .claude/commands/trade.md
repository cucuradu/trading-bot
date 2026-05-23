---
description: Manual trade helper with strategy-rule validation. Usage — /trade SYMBOL SHARES buy|sell
---

Execute a manual trade with full rule validation. Refuse if any rule fails.

Args: `SYMBOL SHARES SIDE` (buy or sell). If missing, ask.

1. Pull state: `bash scripts/alpaca.sh account`, `bash scripts/alpaca.sh positions`, `bash scripts/alpaca.sh quote SYMBOL` (capture ask price P).
2. For BUY, validate the buy-side gate from `memory/TRADING-STRATEGY.md`:
   - Total positions after fill ≤ 6
   - Trades this week + 1 ≤ 3
   - SHARES × P ≤ 20% of equity
   - SHARES × P ≤ available cash
   - `daytrade_count` < 3
   - Catalyst documented in today's `memory/RESEARCH-LOG.md` (ask for thesis if missing)
   If any fail, STOP and print the failed checks.
3. For SELL, confirm position exists with right qty. No other checks.
4. Print the order JSON + validation results, ask "execute? (y/n)".
5. On confirm:
   ```
   bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"N","side":"buy|sell","type":"market","time_in_force":"day"}'
   ```
6. For BUYs, immediately place 10% trailing stop GTC:
   ```
   bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"N","side":"sell","type":"trailing_stop","trail_percent":"10","time_in_force":"gtc"}'
   ```
7. Append to `memory/TRADE-LOG.md` with full thesis, entry, stop, target, R:R.
8. `bash scripts/whatsapp.sh "<trade details one-liner>"`.

If `scripts/alpaca.sh` exits 42 (failsafe), STOP, send WhatsApp alert, do not retry.
