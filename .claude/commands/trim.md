---
description: Partial exit when a winner exceeds 25% weight + +10% gain (Phase H1). Usage — /trim [SYMBOL]
---

Mechanical partial-exit per the Phase H1 rule in `memory/TRADING-STRATEGY.md`
("Partial exits"). Shows the proposed action and asks for confirmation before
placing.

Args: optional `SYMBOL`. If omitted, scan all positions.

1. **System kill switches FIRST**:
   ```
   python scripts/risk_gates.py lock-status     # exit 42 = LOCK → STOP
   python scripts/risk_gates.py check
   ```
   If `lock_file_present` is true → send WhatsApp "LOCK present, /trim refused" and STOP.
   (Protective sells are normally allowed under LOCK, but a *trim* is discretionary
   and shouldn't fire during a hard drawdown lock — close the full position instead
   if reduction is needed.)

2. **Pull state**:
   ```
   bash scripts/alpaca.sh account
   bash scripts/alpaca.sh positions
   bash scripts/alpaca.sh orders
   ```
   Parse equity `E`, and per position: market value `V`, current price `P_c`,
   shares `S`, avg entry `P_e`, unrealized P&L %.

3. **Apply the Phase H1 trigger** to each position (or the named SYMBOL):
   - `V / E > 0.25` (weight > 25% of equity), AND
   - `unrealized_pnl_pct > +10%`.

   If nothing qualifies → print "no trim candidates" and stop.

4. **Compute shares to sell** per qualifying position:
   ```
   shares_to_sell = ceil((V − 0.18 × E) / P_c)
   shares_remaining = S − shares_to_sell
   pnl_realized_estimate = shares_to_sell × (P_c − P_e)
   ```

5. **Verify the trailing stop coverage** on the residual:
   - Look up the position's open trailing-stop order in step 2's `orders` output.
   - If `stop.qty == S` (full original size), note that the OTO child auto-adjusts
     on partial fills — Alpaca handles it.
   - If `stop.qty < S` (already partial), record `stop_coverage_gap` and flag
     in the proposal — user decides whether to cancel + re-place.

6. **Surface the OPEN line** so the original thesis + initial_stop are visible:
   ```
   grep "^- OPEN .*: SYM" memory/TRADE-LOG.md | tail -1
   ```

7. **Print the proposal** (one block per candidate):
   ```
   TRIM CANDIDATE: SYM
     Current: S shares × $P_c = $V (weight W%, unrealized +X%)
     Propose: sell N shares @ market → residual M shares ($D, weight Y%)
     Realized P&L (est): $X.XX
     Stop child: <"OK — Alpaca auto-adjusts" | "GAP — needs re-place after fill">
     Original thesis: "<from OPEN line>"
     initial_stop: $S (unchanged, R-math reference)
   Confirm? (y/n)
   ```

8. **On confirm**, place the partial sell:
   ```
   bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"N","side":"sell","type":"market","time_in_force":"day"}'
   ```
   If `scripts/alpaca.sh` exits 42 (failsafe), STOP, send WhatsApp alert, do not retry.

9. **If stop_coverage_gap was flagged** in step 5, re-place the trailing stop on the
   residual after the partial sell fills:
   ```
   bash scripts/alpaca.sh cancel <old_stop_order_id>
   bash scripts/alpaca.sh order '{"symbol":"SYM","qty":"M","side":"sell","type":"trailing_stop","trail_percent":"<existing trail %>","time_in_force":"gtc"}'
   ```
   Use the SAME `trail_percent` the original stop had — do not recompute ATR
   here; this is a coverage re-place, not a stop methodology change.

10. **Append to `memory/TRADE-LOG.md`** (canonical Phase H1 format):
    ```
    - TRIM YYYY-MM-DD: SYM exit=FILL_PRICE shares_sold=N remaining_shares=M pnl_realized=$X.XX reason="trim_to_18pct"
    ```
    The original OPEN line stays untouched. Do NOT write a CLOSED line — the
    position is still open.

11. **WhatsApp confirmation** (heredoc so `$` survives):
    ```bash
    bash scripts/whatsapp.sh << 'WAEOF'
    TRIM SYM: sold N @ $P → residual M shares (weight Y%). Realized $X.XX.
    WAEOF
    ```