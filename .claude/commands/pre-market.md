---
description: Pre-market research — pro-level multi-source brief written to RESEARCH-LOG.md + WhatsApp digest
---

Local run of the pre-market workflow.

STEP 0a — **Compute today's calendar in shell** (Gemini hallucinates date math; we resolve it deterministically here):
```bash
CAL_JSON=$(python scripts/trading_calendar.py status)
DATE=$(echo "$CAL_JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['today'])")
TODAY_HUMAN=$(echo "$CAL_JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['today_human'])")
NEXT_TRADING_DAY=$(echo "$CAL_JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['next_trading_day_human'])")
NEXT_TRADING_DAY_ISO=$(echo "$CAL_JSON" | python3 -c "import json,sys;print(json.load(sys.stdin)['next_trading_day'])")
IS_HOLIDAY=$(echo "$CAL_JSON" | python3 -c "import json,sys;print('yes' if json.load(sys.stdin)['is_us_holiday'] else 'no')")
echo "Today: $TODAY_HUMAN (US holiday: $IS_HOLIDAY) | Next trading day: $NEXT_TRADING_DAY ($NEXT_TRADING_DAY_ISO)"
```

Pass `$DATE`, `$TODAY_HUMAN`, `$NEXT_TRADING_DAY` into every Gemini prompt
that references "today" or "next session". Use the literal values in the
RESEARCH-LOG header — never let Gemini compute the date itself.

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

STEP 0 — System kill switches FIRST. Refuse to run pre-market research if a lock is active (saves Gemini quota; no point researching if we can't trade).
```
python scripts/risk_gates.py lock-status     # exit 42 = LOCK present, send WhatsApp and STOP
python scripts/risk_gates.py check           # parse JSON; remember entries_blocked for STEP 4
```

If the `check` JSON includes a `lock_auto_recovered` field (Phase C auto-recovery cleared the LOCK on this run), record a one-line note in today's RESEARCH-LOG entry (STEP 6) and include it in the WhatsApp alert at STEP 7 so the user notices the bot resumed trading.

**Phase E — pre-macro-event deployment cap.** If `check` JSON returns `pre_macro_event.cap_active == true`, cap **total** cost-basis deployment for today at 40% of equity. Two practical effects:

- Reduce the day's trade ideas to MIN(`market.trade_slots`, 2) — never propose 3 candidates when the cap is active.
- The RESEARCH-LOG header MUST include a line like
  `**Pre-macro:** cap_active (event: <event_name> on <event_date>) → 40% deployment cap` so audits show the bot saw the event.
- The WhatsApp brief MUST include a line `Pre-macro: <event> in <N>d → cap 40%`.

This is a hard system gate (like LOCK), not Claude discretion. See TRADING-STRATEGY.md "Pre-macro-event deployment cap (Phase E)".

STEP 1 — Resolve today's regime (hybrid ML → rule fallback, Phase B):
```
python scripts/ml_insights.py resolve
```
Parse the JSON. Capture:
- `source`: `"ml"` (local PC produced ml-insights.json today) or `"rule_fallback"` (using scripts/regime.py)
- `fallback_reason`: only when source=rule_fallback — log this so the user notices local PC drift
- `market.regime`: Bull | Neutral | Caution | Defensive
- `market.deployment_target` and `market.trade_slots` — caps today's research and order count
- `sectors`: per-ticker regime map. Sector-Bear tickers must NOT be researched as buy candidates.

If `market.regime == "Defensive"`, skip generating new trade ideas entirely — write only the regime line + a one-paragraph note + decision: HOLD, and skip STEP 4b–4e (no need to spend research quota on a no-trade day).

STEP 2 — Read memory for context:
- `memory/TRADING-STRATEGY.md`
- Tail (~100 lines) of `memory/TRADE-LOG.md`
- Tail (~100 lines) of `memory/RESEARCH-LOG.md`
- `python scripts/research.py macro` — yesterday's macro paragraph (single paragraph; cheap)

STEP 3 — Pull live paper account state:
```
bash scripts/alpaca.sh account
bash scripts/alpaca.sh positions
bash scripts/alpaca.sh orders
```

STEP 4 — Macro context via Gemini (default Flash; grounded search). Five queries cover the macro picture:
```
bash scripts/gemini.sh "WTI / Brent crude oil price right now and major moves today, with one cited source"
bash scripts/gemini.sh "S&P 500 futures premarket today $DATE plus VIX level and 30-year Treasury yield (current regime: <regime>)"
bash scripts/gemini.sh "Top stock market catalysts and earnings before market open $DATE — cite sources and dates"
bash scripts/gemini.sh "US economic calendar today $DATE: CPI PPI FOMC jobs data — cite the release schedule"
bash scripts/gemini.sh "Recent news on currently-held tickers: <list from positions>"
```

**STEP 4-bis — Macro-print reader (event days only).** If `python scripts/risk_gates.py check` returned `pre_macro_event.within_24h=true` OR `pre_macro_event.days_to_event=0`, query the realized print BEFORE candidate selection (the pre-market cron fires shortly after the 8:30 ET release):
```
bash scripts/gemini.sh "actual realized print today $DATE for <event_name from pre_macro_event> (consensus expectation, actual number, beat/miss, market reaction first 10 minutes) — cite Bloomberg/Reuters/CNBC."
```
Paste the result into the **Macro Framework** section. If the print was hot (above consensus) AND today's regime is Bull/Neutral, downgrade `trade_slots` by 1 for the day (defensive posture). If benign, proceed as planned.

```
```
If `scripts/gemini.sh` exits 3, fall back to native WebSearch and note the fallback in the log entry.

Also use `python scripts/market_data.py sector-momentum` for the sector picture (no API quota). Cross-check against the regime classifier's `sectors` block — they should largely agree; if they don't, flag it.

STEP 4b — Build today's shortlist (Phase F: data-driven multi-factor screener;
Phase G2: carry-forward watchlist):

0. Read the carry-forward watchlist (Phase G2). Candidates whose limit/stop
   didn't fill in the last 3 trading days are tracked here:
   ```
   python scripts/watchlist.py list
   ```
   Empty list is fine. Otherwise each entry's symbol gets a small bonus to its
   screener `ml_score` (+0.5) when assembling the shortlist. Apply normal
   filters (sector regime, earnings blackout). Watchlist survivors belong at
   the top of the shortlist — the thesis was already validated; we're just
   re-trying the entry.

1. Resolve candidate ranking via STEP 1's `universe_ranking`:
   - If `source=ml` → `universe_ranking` is the XGBoost top-N from the local PC.
   - If `source=rule_fallback` → `universe_ranking` is now populated by the local 7-factor screener (`scripts/screener.py`) scanning the full ~70-ticker universe (Phase F). Read the same field — no branching needed.
   - If `universe_ranking` is empty (both ML and screener failed), fall back to the old behavior: top-1 momentum ticker in each of two leading sectors from `sector-momentum`, plus one catalyst name.

2. Build the deep-dive shortlist directly from the screener:
   ```
   python scripts/screener.py shortlist --slots $TRADE_SLOTS
   ```
   Returns ≤6 names already filtered for:
   - sector not in Bear regime
   - not already an open position
   - sector cap (≤2 same-sector existing positions; BROAD ETFs exempt)
   - max pairwise correlation ≤ 0.70 with each previously-picked candidate
   - liquidity (avg daily $-volume ≥ $50M), not penny (≥ $5), ATR% ≤ 8%

3. Augment with **at most one** catalyst-driven add from STEP 4 macro queries, ONLY if:
   - it is in `python scripts/universe.py list`
   - it survives the screener's sanity gates (run `python scripts/screener.py explain SYM` to check)
   - its catalyst is dated within the next 14 days
   - **its sector is NOT already at the 2-position cap** when combined with the screener's existing picks (count screener picks + currently open + catalyst-add per sector; if any sector hits 3, drop the catalyst-add)
   Otherwise skip — do not force an off-ranking name.

4. Filter: must not be in earnings blackout unless catalyst IS earnings
   (`python scripts/market_data.py earnings SYM`).

5. Run the STEP 4c–4f deep-dive (gather / synthesize / critique / historical-analog)
   on the resulting shortlist (5–6 candidates). The final order-execution cap stays
   `min(trade_slots, 3)` — extras become tomorrow's pre-warmed candidates.

STEP 4b-bis — write a diagnostics line to RESEARCH-LOG so we can audit the screener:
```
Screener: source=<ml|local_screener_v1>, ranked N tickers, top 10 = [SYM1(score), SYM2(score), ...]
```

STEP 4c — Gather multi-source raw research for each shortlisted ticker (Pass 1):
```
python scripts/research.py gather <SYM1> [<SYM2> ...]
```
Pulls in parallel from: NewsAPI (mainstream), Finnhub (company news + analyst changes + insider Form 4), SEC EDGAR (8-K / 10-Q / 4 filings), Google News RSS, Reddit (sentiment). Missing keys degrade gracefully — that source returns `[]` and is noted in the entry footer.

STEP 4d — Synthesize per candidate (Pass 2; Gemini 2.5 Pro, structured output):
```
python scripts/research.py synthesize <SYM>
```
Returns markdown with: Bull case (cited), Bear case (cited), Disconfirming evidence to watch for, Catalysts ahead (next 14d, dated), one-line takeaway. The synthesis prompt enforces ≥1-citation per Bull/Bear bullet — unsourced claims are dropped. Run once per candidate.

STEP 4e — Adversarial critique (Pass 3; Gemini 2.5 Pro at higher temperature):
```
python scripts/research.py critique <SYM>
```
Returns: strongest counter to the bull case, list of any unsourced claims found, the single most-likely invalidator over the next 5 trading days. If the critique materially undermines the synthesis (Claude judges), demote or drop the candidate.

STEP 4e-bis — **Investigate further when uncertain (do not skip).** The 5 sources + 3 LLM passes are a FLOOR, not a ceiling. If any of the following triggers fire, run ad-hoc follow-up queries BEFORE writing the RESEARCH-LOG entry:

- **Synthesis and critique disagree** on direction (bull says buy, critique presents a strong invalidator the bull didn't address).
- **Source disagreement**: tier-1 (NewsAPI/Finnhub) says one thing, Reddit/Google News say another.
- **Sparse data**: fewer than 5 unique records across all sources, or no EDGAR/Finnhub records in 14 days.
- **Unfamiliar catalyst**: a news item references a regulatory, macro, or geopolitical concept you don't have prior context on.
- **Macro divergence**: the resolved regime contradicts the per-ticker thesis (e.g., Defensive regime but candidate looks bullish in isolation).
- **Stale TICKER-NOTES**: the Thesis line for this ticker is older than 7 trading days.

Tools for follow-up:
```
bash scripts/gemini.sh "<targeted question; cite sources and dates>"     # free Flash, grounded
bash scripts/gemini.sh --smart "<deeper question>"                       # Pro if quota left; auto-falls back to Flash+CoT on 429
python scripts/news_sources.py newsapi-query "<targeted query>"
python scripts/news_sources.py finnhub-news SYM 14
python scripts/news_sources.py edgar SYM
python scripts/research.py latest-on SYM 30                              # 30 days of prior mentions
python scripts/market_data.py {quote|atr|correlation|earnings} SYM
```

Document the follow-up in the RESEARCH-LOG entry under a new heading `### Follow-up investigation` with: the trigger that fired, the queries run, what changed in the decision. The Gemini cache means repeated queries are free.

Budget guard: stop adding follow-up queries once Claude's input token count exceeds ~20k for this session — at that point the marginal value is low. Better to defer to /trade time, where you can re-fetch fresh research on the specific candidate.

STEP 4f — Historical analog (one Gemini 2.5 Pro call per pre-market):
```
python scripts/research.py historical-analog <<< "$MACRO_SUMMARY"
```
Where `$MACRO_SUMMARY` is a 4-6 line digest of today's regime + VIX + key yield + breadth + sector leadership. The response is the **Historical Analog** section of the RESEARCH-LOG entry.

STEP 5 — Constrain trade ideas to the universe:
- Reference `python scripts/universe.py list` for the 40-ticker whitelist. ANY trade idea must be on this list.
- Skip tickers whose sector is `Bear` in STEP 1's regime resolution.
- Honor today's `trade_slots`: if `trade_slots == 0` (Defensive), write zero trade ideas. If `trade_slots == 1`, write at most 1.

STEP 6 — Write a dated entry to `memory/RESEARCH-LOG.md` using the **pro-level template** below. The entry MUST start with a regime header line so audits and the daily summary can grep it:

```markdown
## YYYY-MM-DD — Pre-market

**Regime:** <Bull|Neutral|Caution|Defensive> (source: <ml|rule_fallback>, slots: N, deployment: XX%) <fallback reason if applicable>

### Account
- Equity / Cash / Buying power / Daytrade count / Open positions / Open orders

### Macro Framework
[One paragraph capturing: regime, key yield level (30y), USD trend, oil, breadth, VIX term structure, dominant theme. Diff explicitly vs yesterday's MACRO-FRAMEWORK paragraph: "vs yesterday: yields ±Xbp; oil ±X%; regime unchanged/flipped".]

### Sector Picture
- Top 3 / bottom 3 sectors by 1mo momentum, with regime tag from STEP 1
- Note any disagreement between sector-momentum (yfinance) and the ml-insights sectors block

### Candidates

For each shortlisted candidate (cap 3):

#### SYM (SECTOR_ETF, $XXX.XX ±X.X% premarket)

**Setup:** above/below 200-SMA (X.X%), 50-SMA distance (X.X%). ATR(14)=$X.XX (X.X% of price); stop_pct_2_5x=X.X% (clamped to [7, 15]).

**Sources scanned (N):** X NewsAPI / Y Finnhub / Z EDGAR / W Reddit / V Gemini.

[Paste the synthesize output verbatim — Bull case (cited), Bear case (cited), Disconfirming evidence, Catalysts ahead, one-line takeaway.]

**Critique:** [Paste the critique output's "Strongest counter" + "Single most-likely invalidator" lines.]

**Position-aware (if entered $20k):**
- Sector exposure post-entry: X% (currently Y%)
- 30d correlation with existing positions: from `python scripts/market_data.py max-correlation-with SYM <existing>`
- Sector cap status: X/2 (Phase C rule)

**R:R math:** entry $X / stop $X (-X.X%) / target $X (+X.X%) / R:R X.X:1 / max risk $X.

**Setup type (Phase G1):** PULLBACK | BREAKOUT | MOMENTUM
- **PULLBACK** — mean-reversion thesis (bounce off MA, dip-buy at support). Market-open places a **buy-limit** at the planned entry.
- **BREAKOUT** — confirmation above resistance (52w-high break, base break). Market-open places a **buy-stop** at resistance + 0.1–0.2%.
- **MOMENTUM** — open-with-strength; reserved for binary-event days where the print already triggered. Market-open places a **market order at open**. Justify why a limit wouldn't work.

**Entry plan:** PULLBACK → limit $X.XX (day TIF) | BREAKOUT → buy-stop $X.XX (day TIF) | MOMENTUM → market at open

**Decision:** retained / demoted / dropped — one sentence explaining why.

### Historical Analog
[Paste the historical-analog output verbatim.]

### Risk Factors (consolidated)
- 5–7 bullets covering macro, sector, position, calendar, geopolitical

### Decision
TRADE / HOLD with explicit deployment plan (which N candidates, in what order) and any waiting conditions (e.g., "wait 15 min after open before any entry").

### Quota & source usage (footer)
- Gemini calls: N Flash + N Pro
- NewsAPI / Finnhub / EDGAR / Reddit request counts
- Fallback events (sources that returned [] due to missing keys or errors)
```

STEP 6b — Update persistent knowledge files (idempotent updates, not blind appends):

1. **`memory/MACRO-FRAMEWORK.md`** — append a new `## YYYY-MM-DD` section with the **Macro Framework** paragraph from STEP 6. Trim sections older than 30 days into a footnote.

2. **`memory/TICKER-NOTES.md`** — for each shortlisted ticker:
   - Rewrite the `Thesis (YYYY-MM-DD):` line with today's one-line takeaway from the synthesis.
   - Append the strongest 1–2 new catalysts to the **Recent catalysts** list. Cap that list at 5 — older rows move to a `<!-- archive -->` block at the bottom of the section.
   - Append any new **Open thesis questions** surfaced by the critique.

Use `python scripts/research.py ticker-notes SYM` to read the current section before rewriting — never blindly overwrite.

STEP 7 — Compose and send the **pre-market WhatsApp brief**. Always send (this replaces the prior "silent unless urgent" rule). Target 18–25 lines, fits within CallMeBot's URL-length budget:

```
PRE-MARKET • <weekday MMM DD> • <Regime> (VIX X) [<ml|rule>]
══════════════════════════════════
Macro: 30y X.XX% (±Xbp), DXY ±X.X%, WTI $X
<one-line top macro risk>
Breadth: X% univ > 50-SMA; X/11 sectors green

TOP IDEAS (slots N/M):
1. SYM $X.XX | SECTOR_ETF (relative strength tag)
   bull: <2 cited bullets, condensed>
   bear: <2 cited bullets, condensed>
   R:R X.X:1 / stop -X.X% / size $X
2. SYM $X.XX | SECTOR_ETF
   …
3. SYM $X.XX | SECTOR_ETF
   …

Watch: <calendar events; earnings; macro releases>
Analog: <historical-analog one-liner>
RISK: <one-line single most-likely invalidator>
Decision: TRADE N / HOLD
```

**MANDATORY send pattern — use a single-quoted heredoc so dollar amounts pass through bash literally:**

```bash
# Write the brief to a temp file first so we can measure length.
cat > /tmp/wa-pre-market.txt << 'WAEOF'
<paste the entire formatted brief here, including all $ amounts.
 The 'WAEOF' single-quote suppresses bash expansion — $215.33,
 $81.6B, $1,065 etc. all pass through byte-for-byte intact.>
WAEOF

# Length guard (CallMeBot's URL cap is ~1500 chars; 1400 leaves room
# for URL encoding overhead). Auto-shrink if over.
WA_LEN=$(wc -c < /tmp/wa-pre-market.txt)
if [[ $WA_LEN -gt 1400 ]]; then
    # Step 1: trim each candidate's bear/bull bullets to one line each.
    # If still over: drop the 3rd candidate's bullets entirely.
    # If still over: keep only the macro + top-1 candidate + decision.
    # Rewrite /tmp/wa-pre-market.txt and re-measure.
    echo "[shrink] original $WA_LEN > 1400; trimming"
fi

bash scripts/whatsapp.sh < /tmp/wa-pre-market.txt
```

NEVER pass the brief as a quoted argument (`bash scripts/whatsapp.sh "..."`).
Bash will expand `$2…`, `$8…`, `$1…` etc. as positional parameters and eat
the leading digit of every dollar amount — that's the bug we found in the
2026-05-25 brief (NVDA $81.6B → 1.6B, $215.33 → 15.33, LLY $1,065 → 065).

If `lock_auto_recovered` fired in STEP 0, prepend a line: `LOCK auto-recovered: <reason>`.

If today is a market holiday or markets closed (CHECK BEFORE sending), still send the brief but mark the header as `(markets CLOSED)` and set Decision to HOLD with no orders.

If `scripts/gemini.sh` returned exit 4 (Pro quota exhausted AND Flash fallback failed) on critical calls, send a degraded brief flagged with `[degraded: Gemini quota]` in the header so the user knows depth is reduced.

If `scripts/alpaca.sh` exits 42 (failsafe) at any point in this routine, STOP, send WhatsApp alert, do not retry.
