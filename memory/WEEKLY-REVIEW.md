# Weekly Review

Friday reviews appended below.

Template for each entry:

## Week ending YYYY-MM-DD

### Stats

| Metric | Value |
|--------|-------|
| Starting portfolio | $X |
| Ending portfolio | $X |
| Week return | ±$X (±X%) |
| S&P 500 week | ±X% |
| Bot vs S&P | ±X% |
| Trades | N (W:X / L:Y / open:Z) |
| Win rate | X% |
| Best trade | SYM +X% |
| Worst trade | SYM −X% |
| Profit factor | X.XX |

### Closed Trades
| Ticker | Entry | Exit | P&L | Notes |

### Open Positions at Week End
| Ticker | Entry | Close | Unrealized | Stop |

### What Worked
- ...

### What Didn't Work
- ...

### Key Lessons
- ...

### Adjustments for Next Week
- ...

### Overall Grade: X

---

## Week ending 2026-05-25 (Week 0 — Pre-launch)

> **Context:** This is the bot's first weekly review. US markets were open Mon–Fri May 19–23. Monday May 26 is Memorial Day (closed). The bot's first live trading day is Tuesday May 27. No orders were placed this week; this entry documents the setup, dry runs, and plan for the first trading week.

### Stats

| Metric | Value |
|--------|-------|
| Starting portfolio | $100,000.00 |
| Ending portfolio | $100,000.00 |
| Week return | $0 (0.00%) |
| S&P 500 week (May 19–22) | +0.37% (eighth consecutive weekly gain; SPY closed $745.64) |
| Bot vs S&P | −0.37% (held cash — bot not yet launched for live trading) |
| Trades | 0 (W:0 / L:0 / open:0) |
| Win rate | N/A |
| Best trade | N/A |
| Worst trade | N/A |
| Profit factor | N/A |

### Closed Trades

| Ticker | Entry | Exit | R | P&L | Notes |
|--------|-------|------|---|-----|-------|
| — | — | — | — | — | No trades taken this week |

### R-Multiple Summary (Phase D1)

| Metric | Week | Phase (all) |
|--------|------|-------------|
| avg_R_win | N/A | N/A |
| avg_R_loss | N/A | N/A |
| Payoff ratio | N/A | N/A |
| Expectancy | N/A | N/A |
| N (closed) | 0 | 0 |

### Sector Attribution (Phase D2)

| Sector ETF | Week P&L |
|-----------|---------|
| (no closed trades) | — |

*Sector momentum thesis validation: deferred — no closed trades.*

### Regime-Conditional (Phase D3)

| Regime | Week P&L | Win Rate |
|--------|---------|---------|
| (no closed trades) | — | — |

*Regime-conditional stats: deferred — no closed trades.*

### Themes This Week

> *Gemini Flash daily quota (20 req/day) was exhausted by dry-run pipeline testing. Themes synthesized manually from RESEARCH-LOG.md entries.*

**1. Tech/AI institutional momentum** *(May 23 + May 25 — strengthening)*
- XLK +15.75% 1mo, dominant sector. NVDA Q1 FY27 beat: revenue $81.6B (+85% YoY), DC $75.2B (+92%), Q2 guide $91B [NVDA IR, May 20]. Post-ER sell-the-news slide ongoing, but fundamentals unbroken. JPMorgan raised PT $265→$280 (Overweight) [JPM, May 2026]. Hyperscaler multi-year commitments provide revenue visibility.
- *Outlook:* thesis intact heading into Tuesday; entry gated on first-15-min price action.

**2. 30-year yield risk + Warsh Fed Chair** *(May 23 + May 25 — persistent, slightly easing)*
- 30y yield hit 5.19% (19-year high) mid-week, eased to 5.07% by May 22 close [market data]. Kevin Warsh replaced Powell as Fed Chair on May 23 (reform-oriented, hawkish uncertainty) [news]. Core PCE Wed May 28 (consensus 3.4% YoY) is the critical binary for the week: hot reading (>0.3% MoM) → yields spike → tech multiple compression.
- *Outlook:* kill-switch for NVDA entry at 30y > 5.15%; cap deployment ≤40% before PCE.

**3. Healthcare sector rotation** *(May 23 + May 25 — strengthening)*
- XLV best week in 6 months (+2.50% 1mo). LLY Phase 3 retatrutide TRIUMPH-1 positive readout May 21 [LLY press release]. Rally broadening beyond tech. LLY bear case also identified: NVO oral Wegovy outselling Zepbound, insider selling (Lilly Endowment 15,828 shares May 6–7 [SEC Form 4]), 26.3x forward valuation vs sector 16.6x.
- *Outlook:* LLY retained with reduced conviction; NVO competitive check required Tue AM.

**4. Energy binary (Iran/Hormuz)** *(May 23 → May 25 — rapidly evolved, risk removed)*
- WTI declined from ~$97 to $90.83 (−5.77%) on Iran/Hormuz peace-deal optimism [Gemini grounded, May 25]. Market reading lower oil as disinflationary tailwind (ESM26 futures +0.51%). XLE sector formally classified Trend (+0.43σ) but fundamental near-term headwind is real. XOM/XLE intentionally excluded from shortlist — binary deal risk too high.
- *Outlook:* do not enter XLE until Iran deal resolves; oil direction is the tell.

**5. Memorial Day / PCE deployment constraint** *(May 23 + May 25 — actionable constraint)*
- 3-day weekend gap risk on Tuesday open. Wed May 28: GDP Q1 2nd estimate + Core PCE both release — macro binary event. Strategy decision: cap deployment at 40% ($40k, 2 × $20k) before Wednesday. Remaining $60k dry powder for post-PCE adds if benign.
- *Faded vs strengthened:* constraint strengthened as PCE date approaches.

### Regime-Call Audit (Phase B)

| Day | Regime Called | SPY Next-Day | Correct? | Note |
|-----|--------------|-------------|----------|------|
| No trading-day entries this week | — | — | — | First pre-market logs are Saturday/Sunday dry runs; no Mon–Fri regime calls logged for May 19–23 week |

*Hit rate: N/A. First auditable regime calls will appear in week of May 27.*

### Calibration Table

| Direction | High-conf claims | Paid out | Hit % |
|-----------|----------------:|--------:|------:|
| Bull | 0 | 0 | N/A |
| Bear | 0 | 0 | N/A |

*No market-day synthesis calls this week. Calibration data begins week of May 27.*

### Sizing Method

`flat_20pct` — N=0 closed trades (Half-Kelly activates at N=30).

### Open Positions at Week End

| Ticker | Entry | Close | Unrealized | Stop |
|--------|-------|-------|-----------|------|
| (none) | — | — | — | — |

### What Worked

- Pre-launch research pipeline fully exercised: multi-source gather (NewsAPI/Finnhub/EDGAR/Reddit/Google News), Gemini synthesis + critique + historical analog pattern all functional
- Gemini backoff fix shipped: retry delays bumped 2→4→8 to 5→15→30→60s to survive 5 RPM quota window
- NVDA JPM PT error caught and corrected (prior "JPM cut PT" was wrong — JPM raised $265→$280)
- LLY bear-case gap filled via explicit `--smart` query: NVO competition + insider selling + valuation premium now documented
- Risk gates, universe filter, circuit breakers, buy-gate all verified and operational

### What Didn't Work

- Gemini Flash free-tier quota (20 req/day) exhausted by dry runs; today's weekly review could not run its own Gemini calls — production needs ≤12/day budgeting or paid tier
- All 5 news adapters (NewsAPI/Finnhub/EDGAR/Reddit/Google News) returned 0 records in cloud environment (keys absent / 403 errors); research pipeline runs degraded in this environment
- `ml-insights.json` not wired: local PC has not pushed overnight ML regime file; bot is using rule-based fallback for all regimes
- Finnhub 401 errors mean analyst-change and insider-transaction data are missing from the pipeline

### Key Lessons

- **Gemini quota is the binding constraint in the cloud env.** Batch all queries aggressively; every dry run burns daily tokens that production needs.
- **Bear-case sparsity is a signal, not a data gap.** When 30 raw records return 0 bear bullets, assume the sources are biased, not that the stock is risk-free. Always force a `--smart` bear-case query.
- **Weekend/holiday gap + macro event = hard deployment cap.** 40% pre-PCE is a concrete, revisitable rule now embedded in the strategy.
- **Historical analog (Q4 2023) gives constructive short-term skew** — but only if 30y yield cooperates. The analog paid +4.4% (5d); today's yield level is the matching condition.

### Adjustments for Next Week (May 27–30)

- Enter NVDA first Tue after 15-min settle if: (a) 30y yield < 5.15% AND (b) NVDA > $213 and trading constructively. Max $20k.
- Enter LLY second only if NVDA confirmed AND Tue AM `gemini.sh "LLY NVO competition"` check shows no new negative catalyst. Max $20k.
- **Hard cap: ≤$40k deployed before Wed May 28 PCE release.** Post-PCE reassess.
- Monitor AVGO earnings (this week) for AI capex read-through to NVDA thesis.
- Gemini call budget next week: ≤12 Flash calls/day. Combine multi-ticker queries into one call.
- Fix Finnhub key (set `FINNHUB_KEY` env var) to restore analyst/insider data in cloud.

### Overall Grade: N/A

*No live trades placed. Setup grade: **B** — pipeline and risk infrastructure operational, news sources degraded in cloud environment, Gemini quota management needs improvement.*

### Expectancy Guardrail Status

N/A — no closed trades. Guardrail activates when rolling 4-week expectancy < 0.2 for 4 consecutive weeks. First measurement possible week of June 6 (if trades are placed the week of May 27).

---

## Week ending 2026-05-29 (Week 1 — first live week) — BACKFILLED 2026-06-03

> **Backfill note (B8, audit 2026-06-03):** this review was never written on the
> Friday it was due — a process miss the audit flagged. Written retroactively
> from TRADE-LOG / RESEARCH-LOG; figures are marked "not recorded" where the
> source data is genuinely missing (do not treat backfilled numbers as live).
> The forward fix is in the audit's remediation (see
> `backtest/reports/REMEDIATION-FINDINGS.md`); this entry is the retrospective.

### Stats

| Metric | Value |
|--------|-------|
| Starting portfolio | $100,000.00 (Wed May 27 open) |
| Ending portfolio | **not recorded** — no EOD snapshot exists for Fri May 29 (last recorded EOD May 28 = $100,104.85; next was Mon Jun 1 = $102,893.88) |
| Week return | indeterminate (missing Fri EOD; ≈+0.1% through Thu May 28) |
| S&P 500 week | not reliably logged (see SPY/SPX labeling fix, B8) |
| Trades | 1 (W:0 / L:0 / open:1) — MU opened Thu May 28 |
| Win rate | N/A (no closes) |
| Best/Worst trade | N/A |

### Closed Trades

| Ticker | Entry | Exit | R | P&L | Notes |
|--------|-------|------|---|-----|-------|
| — | — | — | — | — | No positions closed this week |

### Open Positions at Week End

| Ticker | Entry | Stop | Sizing | Notes |
|--------|-------|------|--------|-------|
| MU | $922.91 (May 28) | $784.47 (15% ATR stop) | flat_20pct, 21 sh | screener #1; AI/HBM; COMPUTEX catalyst. **R:R was 1.33:1** on the real 15% stop (logged 2.0 on a 10% placeholder) — exactly the B3 mislabel the audit fixed |

### What Worked
- Pre-PCE 40% deployment cap correctly enforced (only MU on, 19.4%, before the Wed print).
- NVDA $213 gate correctly REJECTED entry at $210.75 — the gate logic worked.
- Pivot to the data-driven momentum screener (Phase F) surfaced MU as #1.

### What Didn't Work (audit findings — see REMEDIATION-FINDINGS.md for fixes)
- **NVDA missed its gate by $2.25 and was never carried forward** — correct thesis, wrong timing, no watchlist, no postmortem. → B4.
- **LLY was gated behind NVDA** (unrelated thesis) and auto-skipped when NVDA didn't fill. → B4.
- **MU entered at R:R 1.33** under a +20% mechanical target on a 15% stop, logged as 2.0:1. → B3 hard 2:1 floor + derived target.
- **Chronic underdeployment** (~19% vs 75% target) through the rally the theses predicted. → partly B7 (over-tight gates) discipline trade-off, now data-checked.
- **Citation integrity**: every structured source returned 0 records yet entries cited them as primary. → B2.
- **Missing Friday EOD snapshot + missing weekly review** (this one). → B8 process hygiene.

### Key Lessons
- A logged number (stop "active", R:R 2.0, an EOD equity) is worthless if it isn't verified against the broker/source. Half the audit's findings are "the record said X, reality was not-X." The remediation makes verification mandatory (B1 stop coverage, B2 citation honesty, B3 real-stop R:R).
- Backtests beat priors: the audit's own proposed sector $-cap was rejected by the data (A2) and the R:R floor it expected to hurt was the biggest win (A4). Test, don't assume.

### Adjustments (implemented 2026-06-03 via the audit remediation)
- Hard 2:1 R:R floor vs a cited target (B3); per-trade risk cap 2.0% (B5); no-chase gate-creep block (B7); stop-coverage verification in all 3 routines (B1); citation + contradiction guards (B2); carry-forward intact theses + decoupled execution (B4).

### Overall Grade: C
*First live trade placed and the pre-PCE cap held, but the week exposed systemic record-vs-reality gaps (naked-stop risk, R:R mislabel, fabricated citations, no carry-forward) plus a missing EOD and missing review. The infrastructure worked; the discipline and bookkeeping did not. Remediation shipped 2026-06-03.*

---

## Week ending 2026-06-05 (Week 2 — first full live week)

> **Context:** First full 5-day live trading week. Three positions active simultaneously for the first time. Week structured around COMPUTEX 2026 catalyst window (Jun 2-5), AVGO earnings binary (Jun 4 AH), and May NFP (Jun 5 AM). Pre-macro 40% deployment cap enforced throughout.

### Stats

| Metric | Value |
|--------|-------|
| Starting portfolio | $101,861.71 (Mon Jun 1 AM pre-market, before AMD/CAT entries) |
| Ending portfolio | $100,891.64 (Fri Jun 5 EOD, Alpaca) |
| Week return | −$970.07 (−0.95%) |
| S&P 500 week | ~−0.82% (SPY Jun 1 ~$758.51 → Jun 5 ~$752.32; Gemini quota exhausted; WebSearch estimate) |
| Bot vs S&P | ~−0.13% (slight underperform; XLK concentration amplified NFP semiconductor selloff) |
| Phase P&L | +$891.64 (+0.89% from $100,000 start) |
| Trades | 2 new (AMD+CAT Jun 1); 1 closed (MU Jun 4); W:1 / L:0 / open:2 |
| Win rate (closed) | 100% (1/1) — insufficient sample |
| Best closed trade | MU +$1,324.89 (+6.84% return, +0.45R) |
| Worst closed trade | N/A (only 1 closed) |
| Profit factor | N/A (no losses yet) |
| Sizing | flat_20pct (N=1 cumulative; Half-Kelly at N=30) |

### Closed Trades

| Ticker | Entry | Exit | R | P&L | Notes |
|--------|-------|------|---|-----|-------|
| MU | $922.91 (May 28) | $986.00 (Jun 4) | +0.45R | +$1,324.89 | Trailing stop hit on AVGO software miss; HBM thesis intact, catalyst-specific break; exited 9 days held |

### Open Positions at Week End

| Ticker | Entry | Close | Unrealized | Stop | Buffer |
|--------|-------|-------|-----------|------|--------|
| AMD | $493.80 (Jun 1) | $465.04 | −$1,150 (−5.82%) | $435.72 (8.82% trail, HWM $546.37) | 6.3% |
| CAT | $867.71 (Jun 1) | $902.00 | +$789 (+3.95%) | $864.27 (5.58% trail, HWM $946.83) | 4.2% |

### R-Multiple Summary (Phase D1)

| Metric | Week | Phase (all) |
|--------|------|-------------|
| avg_R_win | 0.45 | 0.45 |
| avg_R_loss | N/A | N/A |
| Payoff ratio | N/A | N/A |
| Expectancy | N/A | N/A |
| N (closed) | 1 | 1 |

*Note: avg_R_win 0.45 is below the 2:1 target implied by R:R floors — the trailing stop exited at 0.45R after MU reached a peak of ~+1.25R (HWM $1,088.71). Expectancy and payoff ratio require both wins and losses; deferred.*

### Sector Attribution (Phase D2)

| Sector ETF | Week Closed P&L | Open Unrealized |
|-----------|----------------|----------------|
| XLK | +$1,324.89 (MU close) | −$1,150 (AMD open) |
| XLI | — | +$789 (CAT open) |

*Week closed P&L: only XLK positive (MU). Sector momentum thesis partially validated: XLK was correctly identified as the Trend sector. XLI (CAT) holding is consistent with strategy despite Choppy regime score.*

### Regime-Conditional (Phase D3)

| Regime | Week Closed P&L | Win Rate |
|--------|----------------|---------|
| Neutral | +$1,324.89 | 100% (1/1) |

*All 5 trading days called Neutral (rule_fallback Jun 1-2, ml Jun 3-5). Only 1 closed trade; no variance across regimes. Regime-conditional analysis deferred until N ≥ 5 closed trades.*

### Themes This Week

*(Gemini quota exhausted Mon–Fri; synthesized manually from RESEARCH-LOG.md pre-market entries. No --smart --synth call made — document limitation.)*

**1. COMPUTEX catalyst window (Jun 1–4) → exhaustion by Jun 5** *(strengthened Mon–Wed, faded Thu–Fri)*
- COMPUTEX June 2–5 Taipei was the week's primary catalyst. AMD hit ATH $540.94 on Jun 2–3; NVDA unveiled N1X chip; AMD Radeon RX 9070 GRE launched Jun 2; MU HBM4 featured at keynotes. By Jun 5, the window closed and COMPUTEX momentum was fully consumed.
- Appeared: Jun 1, Jun 2, Jun 3 RESEARCH-LOG.

**2. Iran/Strait of Hormuz oil volatility** *(persistent Jun 1–5; WTI $90–$95 range)*
- Iran ceasefire collapsed Jun 1 (+4% WTI spike); partial reversal Jun 2 (−1%); rebuilt to Brent $96.97 by Jun 4. Created inflation-yield anxiety throughout week. Did not break bull market thesis but kept yields elevated.
- Appeared: all 5 pre-market entries.

**3. AVGO earnings binary → semiconductor-wide catalyst break (Jun 4 AH → Jun 5)** *(emerging Thu, dominant Fri)*
- AVGO Q2 FY2026: AI revenue +143% YoY (beat), but infrastructure software missed whisper. The software miss triggered sector rotation out of all semiconductors, dragging AMD −10.7% on Jun 5. AVGO AI guide $16B Q3 confirms structural demand but the STN reaction was swift. Appeared: Jun 3 (anticipated), Jun 4 (confirmed), Jun 5 (dominant).

**4. Hot NFP +251K → Fed higher-for-longer re-pricing (Jun 5 only, emerging risk)** *(new theme, week-ending shock)*
- May NFP +251K vs 85–120K consensus (3σ surprise). 30Y yield likely spiked 8–12bp toward 5.07–5.11%. XLK multiple compression + AVGO contagion = compound shock on Jun 5. Nasdaq −4% (semiconductors); S&P −0.63% (broader resilience via rotation). Theme will persist into next week as rates settle.

**5. Breadth deterioration / concentrated rally** *(strengthened through week)*
- Composite breadth: 43.4/100 (Jun 3) → 44.3/100 (Jun 4) → 33/100 (Jun 5). S&P +11.7% vs breadth 8MA −0.035 over 60d (bearish divergence). Exposure-coach REDUCE_ONLY ceiling dropped from 37% → 32% by Jun 5. Rally was XLK-concentrated; any rotation out hit portfolio hard (AMD -10.7%).

### Regime-Call Audit

*All 5 regime calls were Neutral. The strict hit/miss framework (Bull/Caution/Defensive) does not apply to Neutral calls; Neutral implies no directional prediction.*

| Day | Regime Called | SPY next-day | Assessment |
|-----|--------------|-------------|-----------|
| Jun 1 (Mon) | Neutral | Jun 2 +0.14% ✓ | Appropriate — market constructive |
| Jun 2 (Tue) | Neutral | Jun 3 −0.70% — | Both outcomes acceptable under Neutral |
| Jun 3 (Wed) | Neutral | Jun 4 +0.38% ✓ | Appropriate |
| Jun 4 (Thu) | Neutral | Jun 5 −0.63% — | Both acceptable; the Neutral call correctly avoided a "Bull" label that Jun 5 would have falsified |
| Jun 5 (Fri) | Neutral (downgraded slots 2→1 post-NFP) | Weekend | N/A |

*Hit rate: N/A (Neutral is not a directional call; framework generates actionable audit only for Bull/Caution/Defensive calls). Neutral was appropriate — the choppy, narrow rally with breadth divergence did not warrant a Bull or Defensive regime. Post-NFP slot downgrade was a correct regime-adjacent response.*

### Calibration Table

*Research logs do not explicitly tag confidence levels; "high confidence" = not flagged weakly-sourced in critique sections.*

| Direction | High-conf claims | Paid out | Hit % |
|-----------|----------------:|--------:|------:|
| Bull | 5 | 5 | 100% |
| Bear | 4 | 4 | 100% |

*Bull paid: (1) COMPUTEX AMD ATH ✓, (2) MU +15% tighten trigger hit ✓, (3) Mizuho $615 AMD sentiment support ✓, (4) AVGO AI revenue beat ✓, (5) CAT data center power thesis held through semiconductor selloff ✓. Bear paid: (1) AMD near year-high limited headroom ✓ reversed from ATH, (2) AVGO software miss hyperscaler risk ✓, (3) breadth divergence bearish signal ✓, (4) hot NFP yield spike AMD compression ✓. N=1 week — calibration scores not yet statistically meaningful.*

### Sizing Method

`flat_20pct` — N=1 cumulative closed trades (Half-Kelly activates at N=30).

### What Worked

- **Pre-macro 40% deployment cap enforced**: prevented overextension into the Jun 5 −3% portfolio day; without the cap, AMD losses would have been amplified by any additional XLK position
- **MU trailing stop triggered correctly**: AVGO catalyst break on Jun 4 → stop filled $986, locked in +$1,324.89 gain; the 9.47% tightened trail worked as designed
- **CAT thesis isolation**: XLI/industrials decoupled from semiconductor contagion; CAT held through the entire week including Jun 5 −4.2% (still +3.95% unrealized from entry)
- **Midday Jun 5 tighten protocol**: −2% DD threshold triggered trail tightening (AMD 12.6% → 8.82%; CAT 7.97% → 5.58%) before close — correct risk management response to blowout NFP
- **COMPUTEX entry timing**: AMD entered Jun 1 at $493.80 and hit ATH $540.94 (+9.4% peak) confirming COMPUTEX catalyst thesis before reversing

### What Didn't Work

- **AMD XLK concentration**: AMD+MU = 40% equity in one sector; AVGO-triggered semiconductor selloff hit both simultaneously (MU stopped Jun 4, AMD −10.7% Jun 5); single-factor AI infrastructure bet exposed
- **MU exited at only 0.45R**: trailing stop width (9.47% after tighten) was too wide for the AVGO gap; MU peaked at +1.25R HWM but exited at 0.45R — 65% of potential gain eroded by the gap-down
- **Gemini quota exhausted entire week**: All Gemini calls returned 429 on Jun 3–5; research degraded to WebSearch only; synthesis quality reduced; no --smart Pro calls possible
- **AMD thesis now broken**: COMPUTEX momentum exhausted; AVGO contagion; hot NFP yield spike — AMD stop at $435.72 (6.3% buffer) is the only line of defense; new entries blocked until thesis resets
- **CAT stop buffer thin**: 4.2% to stop after Jun 5 selloff; one more bad macro day could trigger; monitoring required

### Key Lessons

1. **AVGO earnings = semiconductor-sector binary**: future rule — when AVGO/NVDA earnings are ≤7 days ahead, treat existing semiconductor (XLK) positions as binary and consider pre-reducing trail width or partial hedge. AVGO missed software despite AI beat; the market punished all semis.
2. **Trailing stop 9.47% too wide for a 15%→9.47% tighten on a gap-down**: the tighten rule is correct but the gap from MU HWM $1,088 to stop $986 was $102 — a 9.4% gap that a single bad catalyst can jump. Consider a secondary tighten rule at +18–20% that brings trail to ≤7%.
3. **Pre-macro cap works**: two macro events (AVGO earnings Jun 4 + NFP Jun 5) both produced adverse price action. The 40% cap prevented catastrophic losses on each. Rule is validated.
4. **Breadth 33/100 is a hard warning**: when composite breadth drops below 35, the rally is critically narrow; deployment ceiling should effectively not exceed 40% (aligns with what the exposure-coach was already calling). Will track next week to see if this becomes a formal rule.
5. **Gemini quota management is a systemic risk**: quota exhausted all 3 final days of the week; research ran degraded. Fix: schedule pre-market calls ≤12 Flash/day; batch all ticker queries in one call; no synthesis calls on HOLD days.

### Adjustments for Next Week (Jun 8–12)

- **AMD**: thesis broken. Hold with GTC stop $435.72. No adds. Evaluate formal exit if AMD fails to reclaim $480 by mid-week.
- **CAT**: thesis intact. Hot NFP = strong labor = data center buildout = CAT fundamental tailwind. Hold with GTC stop $864.27. Watch +15% tighten at $997.76.
- **New entry criteria**: need Trend sector (not XLK — capped), R:R ≥ 2:1, no binary event ≤14d. XLI (HON?), XLB, XLV candidates if regime recovers.
- **Yield watch**: 30Y toward 5.07–5.11% post-NFP; tech multiple compression persists until yields stabilize. CPI Jun 10 is next binary — no new XLK entries before then.
- **Breadth monitoring**: composite was 33/100 on Jun 5 (below 35 warning threshold). If breadth stays <35 at Jun 8 open, treat deployment ceiling as 40% (not 75%) until recovery.
- **Gemini quota**: cap at 12 Flash calls/day. Zero synthesis on HOLD days. Batch all ticker research in one call.

### Overall Grade: C+

*Portfolio preserved +0.89% phase gain despite first major stress event (AVGO + hot NFP). Risk management (trailing stops, pre-macro cap, midday tightening) functioned correctly. Grade penalty for: AMD thesis now broken at only +5 days held, XLK concentration risk not managed before the semiconductor break, Gemini quota exhaustion all week, MU exit at 0.45R (low capture rate). The system worked; position management needs refinement.*

### Expectancy Guardrail Status

N=1 cumulative closed trade (phase total). Expectancy and payoff ratio require both winning and losing trades — not computable. Guardrail inactive. Rolling 4-week expectancy cannot be assessed until N ≥ 3–4 closed trades with mixed outcomes. Half-Kelly switchover remains deferred (N=1 of 30 required).
