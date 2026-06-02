---
description: Ad-hoc correlation check vs existing positions. Usage — /correlation SYM [SYM2 ...]
---

Quick correlation lookup against current open positions (Phase A3 ≤ 0.70 cap).
Read-only.

Args: one or more `SYMBOL`s. If a candidate is passed alone, compare it against
all current positions. If multiple are passed, compute the pairwise matrix
among them.

1. **Universe check** each symbol — `python scripts/universe.py is_member SYM`. Exit 1 → refuse with which symbol failed.

2. **Pull existing positions**:
   ```
   EXISTING=$(bash scripts/alpaca.sh positions | jq -r '.[].symbol' | paste -sd' ')
   ```

3. **Branch on input shape**:
   - **One candidate + existing positions present** (most common):
     ```
     python scripts/market_data.py max-correlation-with CANDIDATE $EXISTING
     ```
     Report `max_correlation`, the symbol it pairs with, and PASS/FAIL vs the 0.70 cap.
   - **One candidate, no existing positions**: print "no open positions — correlation check is a no-op (PASS by default)". Done.
   - **Multiple symbols passed**:
     ```
     python scripts/market_data.py correlation SYM1 SYM2 [SYM3 ...]
     ```
     Print the matrix. Highlight any pair > 0.70.

4. **Output**: JSON from the script + a one-line PASS/FAIL verdict. No memory writes, no notification.

This skill exists so you don't have to remember the exact `max-correlation-with` invocation when sanity-checking a candidate between routines.