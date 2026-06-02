---
description: Gemini-formatted WhatsApp body from structured input. Token-shift from Claude to Gemini. Usage — /digest <kind>
---

Generate a WhatsApp message body via Gemini instead of having Claude format it
inline. Per CLAUDE.md "delegate to Gemini": prose, table generation, restating
numbers, picking headlines — all of these belong to Gemini, not Claude tokens.

Args: `<kind>` — one of `eod`, `midday`, `position-table`, `pre-market`, `custom`.

For each kind, the skill builds a structured prompt from current state, sends
ONE Gemini call, and emits the response — ready to pipe into `whatsapp.sh`.
**Does not send the message** — that's the caller's job (so the user can
review before push).

### Common preamble (every kind)
```
DATE=$(date +%Y-%m-%d)
ACCOUNT=$(bash scripts/alpaca.sh account)
POSITIONS=$(bash scripts/alpaca.sh positions)
```

### kind = `eod`
Build the End-of-Day recap. One Gemini call, all data inlined:
```
bash scripts/gemini.sh "Format an EOD WhatsApp brief for $DATE.

Account JSON: $ACCOUNT
Positions JSON: $POSITIONS
Day macro line: $(python scripts/research.py macro | head -3)

Output exactly this shape, no preamble:
EOD $DATE
Equity: \$X (DAY_PNL_PCT% day, PHASE_PNL_PCT% phase)
Cash: \$X (CASH_PCT%)
Positions (N):
  SYM | SH | +/-X.X% | stop \$S
Why today (1 sentence):
Tomorrow watch: 1 bullet"
```

### kind = `midday`
```
bash scripts/gemini.sh "Midday WhatsApp update for $DATE.
Positions JSON: $POSITIONS
Output 3 lines max:
  Equity / day P&L
  Any winner > +15% (mention tighten) or loser ≤ initial_stop
  One-line tape read"
```

### kind = `position-table`
Just the table — no narrative. Useful for ad-hoc checks:
```
bash scripts/gemini.sh "Render this positions JSON as a markdown-free WhatsApp table:
$POSITIONS
Columns: SYM | SH | Entry | Now | +/-% | Stop. One header row, one row per position. Right-align numbers via spaces."
```

### kind = `pre-market`
Pull today's RESEARCH-LOG entry and ask Gemini to extract the WhatsApp digest:
```
TODAY_ENTRY=$(awk "/^## $DATE/,/^---/" memory/RESEARCH-LOG.md)
bash scripts/gemini.sh "Compress this pre-market entry into a WhatsApp brief (≤ 8 lines):
$TODAY_ENTRY
Include: regime + slots, top 2 candidates with setup + planned entry + stop, any macro gate today."
```

### kind = `custom`
Read the rest of the user's command line as the brief description, build a
minimal prompt around current account/positions, single Gemini call.

### Output
- Print Gemini's response verbatim.
- Print the exact next command to send it, no extra preamble:
  ```
  bash scripts/whatsapp.sh << 'WAEOF'
  <Gemini output>
  WAEOF
  ```
- Do NOT invoke `whatsapp.sh` yourself — the user reviews first.

Token discipline reminder: ONE Gemini call per invocation. If multiple sections
are needed, batch them into a single numbered prompt — never chain.