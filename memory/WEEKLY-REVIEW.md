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
