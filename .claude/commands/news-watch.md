---
description: On-demand catalyst scan for one ticker. Usage — /news-watch SYMBOL [DAYS]
---

Surface today's catalyst picture for a single ticker. Read-only. No orders, no file writes.

Args: `SYMBOL` (required), `DAYS` (optional, default 3).

1. **Universe check** — `python scripts/universe.py is_member SYMBOL`. Exit 1 → refuse with "outside universe".

2. **Multi-source pull** (cheap, parallel):
   ```
   python scripts/news_sources.py finnhub-news SYMBOL DAYS
   python scripts/news_sources.py finnhub-analyst SYMBOL
   python scripts/news_sources.py finnhub-insider SYMBOL
   python scripts/news_sources.py edgar SYMBOL
   python scripts/news_sources.py google-news "SYMBOL"
   ```
   Missing API keys return `[]` silently — proceed.

3. **Prior thesis** (so you don't surface news that contradicts the running view without flagging):
   ```
   python scripts/research.py ticker-notes SYMBOL
   python scripts/research.py latest-on SYMBOL 7
   ```

4. **Earnings window** — `python scripts/market_data.py earnings SYMBOL`. Flag if `in_blackout` is true.

5. **One Gemini synthesis call** (single batched prompt — do not chain):
   ```
   bash scripts/gemini.sh --synth "Catalyst scan SYMBOL last DAYS days. Inputs (raw JSON pasted): <step 2 outputs>. Prior thesis: <step 3>. Earnings: <step 4>. Output 4 short bullets:
   1. Net catalyst tone (bullish/neutral/bearish + 1 line why)
   2. Single highest-conviction new fact since prior thesis
   3. Any thesis-breaking item (if none, say 'none')
   4. Action read: HOLD / TIGHTEN / TRIM / EXIT — pick one"
   ```

6. **Output to user only** (no TRADE-LOG, no RESEARCH-LOG, no WhatsApp):
   - Earnings status one-liner
   - Gemini's 4 bullets verbatim
   - Source URLs (top 3 by confidence)

If `bash scripts/alpaca.sh` is ever needed here — you're doing it wrong. This is research-only.
