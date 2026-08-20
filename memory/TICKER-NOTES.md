# Ticker Notes

Per-ticker running dossier. Each section is bounded to ~15 lines: rewrite
the **Thesis** line when a new catalyst moves it; append catalyst and
trade rows. Sections are read by pre-market.md, trade.md, market-open.md,
and weekly-review.md via scripts/research.py ticker-notes <SYM>.

Conventions:
- Cite sources inline with [outlet] tags.
- Dates in ISO format (YYYY-MM-DD).
- The OPEN catalyst list keeps the last 5 entries; older rows get archived
  to memory/TICKER-NOTES-ARCHIVE.md during the weekly review.
- Trade-outcome rows mirror the canonical CLOSED-line metadata.

<!-- SEED-CURSOR: AAPL -->

---

## MU (XLK)
- Thesis (2026-08-20): OPEN POSITION — 14 shares @ $936.29 avg (filled Aug 19, OTO limit). Current $923.89 (-1.32%). **CRITICAL: Stop $798.05 GTC unarmed (OTO child failed). Market-open MUST arm stop immediately.** New Street PT $1,250 [NewsAPI 2026-08-15 — verified]. R:R 2.24:1. FOMC minutes (Aug 19) resolved; mild tech softness (-1.3% MU). Next: monitor if $923 holds; stop tighten at $1,076 (+15% from $936.29 entry).
- Recent catalysts:
  - 2026-08-19: MU fell $1,011→$926 intraday (−8.4%) on bond rout/yield spike; recovered to $940. Futures rising premarket; NVDA/MU/SNDK in focus [Google News 2026-08-19 — Gemini grounded — unverified]
  - 2026-08-17: New Street (5-star, Ferragu) Buy upgrade, PT $1,250; KOSPI rebound [NewsAPI 2026-08-15; Yahoo Finance Google News 2026-08-17]
  - 2026-08-17: Trump Administration $200B US fab expansion (Idaho/NY/VA) + $50B R&D [WebSearch — unverified]
  - 2026-08-14: SNDK Investor Day reset NAND 2028-2030 economics; memory sector re-rating [Finnhub 2026-08-14]
  - 2026-07-24: CEO Mehrotra Form 4 insider sells ~7,039 sh at $945-$966 (~$6.76M) [EDGAR Form 4 — verified]
  <!-- archive: 2026-08-14: Alphabet + Amazon $420B AI infrastructure spend; AMAT AH Aug 14 benign -->
  <!-- archive: 2026-08-13: Micron Ventures Paradigm Fund $250M launched -->
  <!-- archive: 2026-06-15: Demoted R:R 1.82:1 vs Wolfe $1,250; "Do NOT chase at $981" -->
- Trade history:
  - 2026-06-04: r=0.45, regime=Neutral, reason="trailing stop hit on AVGO software miss contagion; HBM thesis intact"
- Open thesis questions:
  - FOMC minutes today (Aug 19) — hawkish lean → yield spike → MU revisits $900-926 range
  - Michael Burry expanding short (34 drawdowns >30%, median ROIC 4%): distribution phase?
  - Stop tighten at +15% ($940 entry → $1,081) and +20% ($940 → $1,128) once filled
  - Watch: if MU closes below $900 post-FOMC minutes → stop review needed

## AMD (XLK)
- Thesis (2026-07-22): OPEN POSITION — 25 shares @ $514.61 avg entry (Jul 16). Current ~$528.23 (−2.97% today, +2.6% vs entry). GTC trail 15%, HWM ~$548.14, stop ~$465.92. Advancing AI Summit DELIVERED: Zen 6 Venice (2nm TSMC, 256 cores, 1.7x perf gen-on-gen), MI455X GPU, Helios rack (31TB HBM4); Azure (Helios deployment), Meta (H2 2026), OpenAI (multi-gen Instinct contract) committed. Sell-the-news −3% on day of event. Alphabet + Tesla report tonight (Jul 22 AC) — next binary. Q2 earnings Aug 4. [TechTimes Jul 22 2026; SeekingAlpha/Jefferies Jul 2026]
- Recent catalysts:
  - 2026-07-22: AMD Advancing AI Summit — Zen 6 Venice (2nm, 1.7x perf), MI455X, Helios; Azure+Meta+OpenAI all committed. AMD −2.97% sell-the-news. [TechTimes Jul 22 — WebSearch]
  - 2026-07-21: AMD +3.75% to $522.45 (Summit pre-event pricing-in; Nasdaq-100 +1.3% premarket)
  - 2026-07-20: Meta MI450 GPU + 6th-gen EPYC H2 2026; Oracle 50k MI450 supercluster Q3 2026 [TradingKey Jul 20 — Gemini grounded — unverified]
  - 2026-07-16: UBS raised AMD PT $670→$700; KeyBanc $530→$725 (street high) [Jul 15-16 — various]
  <!-- archive: 2026-07-21: Nasdaq-100 +1.3% pre-event; AMD +3.75% pricing-in Summit -->
  <!-- archive: 2026-07-16: TSMC Q2 2026 record: +77% net profit → confirms AMD chip demand -->
  <!-- archive: 2026-07-15: BofA raised PT $550→$620; ASML raised AI demand forecast -->
  <!-- archive: 2026-07-13: Citigroup upgraded Neutral→Buy, PT $460→$575 -->
- Trade history:
  - Position exited 06-09/06-10 (TRADE-LOG gap; thesis-break per 06-08 notes)
  - 2026-07-16: OPEN — 25 shares @ $514.61 avg entry (filled ~$514-515 premarket pullback). GTC trail 15% armed.
- Open thesis questions:
  - **Alphabet + Tesla tonight (Jul 22 AC):** If Alphabet cloud misses, AI capex narrative weakens; AMD Summit narrative dampened. Key metric: Google Cloud YoY growth and AI CapEx guidance.
  - **Stop tighten thresholds:** +15% = $591.80 (tighten to 1.75×ATR); +20% = $617.53 (tighten to 1.25×ATR). Not reached (today's high ~$548).
  - **Q2 earnings Aug 4:** next binary. Summit customer wins (Azure/Meta/OpenAI) should provide upside guide if AI capex remains robust.
  - **Sell-the-news resolved?** Summit delivered everything expected; question is whether Alphabet beat tonight + Day 2 tomorrow reverts AMD upward or sell-off continues into FOMC (Jul 29).

---

## ABBV (XLV)
- Thesis (2026-07-24): BREAKOUT carry-forward — Jul 23 buy-stop $262 (day TIF) expired unfilled. ABBV failed to reach $262 for 2nd consecutive session (Jul 23, Jul 24). Re-queuing $262 buy-stop today (Jul 24) and Jul 25 = FINAL entry day before Jul 26 blackout (earnings Jul 31). BofA $276 newly confirmed [GuruFocus Jul 24]. R:R 2.07:1 using BMO $300 (confirmed); entire 2:1 case depends on BMO outlier (consensus PT $256.89 is below entry). Volume surge factor negative (−1.166); low-volume breakout risk.
- Recent catalysts:
  - 2026-07-24: BofA $276 Buy confirmed [GuruFocus Jul 24]. Buy-stop $262 day TIF re-queued. Final 2 entry days.
  - 2026-07-23: Alphabet cloud $24.8B (+82%) beat; buy-stop $262 placed day TIF, expired unfilled. Carry to Jul 24-25.
  - 2026-07-22: EU Commission approved Boey (Allergan, serotype E neurotoxin, aesthetics) [Finnhub]; Canaccord raised PT $273→$282 [Finnhub/Investing.com]
  - 2026-07-13: BMO Capital raised PT $258→$300, Outperform — Skyrizi durability + EPCORE DLBCL-4 PFS improvement [Investing.com/GuruFocus — CONFIRMED]
  - 2026-06-30: Insider BUY — Director Quaggin (62 sh) + Director RAPP (134 sh) at $251.64 [Finnhub Form 4]
  <!-- archive: 2026-07-10: BofA raised PT $234→$276 [GuruFocus]; 2026-07-09: Guggenheim $261; 2026-04-29: Q1 2026 beat revenue $15.0B (+12.4%) -->
- Open thesis questions:
  - **Final entry window Jul 24-25:** If $262 not filled by Jul 25 EOD, window closes; reassess post-earnings.
  - **R:R single-outlier risk:** BMO $300 alone gives 2.07:1; BofA $276 gives 0.76:1; Guggenheim $261 is below entry. If BMO cuts PT pre-earnings, thesis collapses.
  - **Volume confirmation needed:** volume surge factor −1.166 (below avg). A breakout at $262 on low volume is lower conviction.
  - **FOMC Jul 28-29 (5 days):** hawkish-hold; 30Y 5.17%. Rate headwind for pharma PE.
- Trade history: (no fill yet — buy-stop $262 day TIF placed Jul 23, expired; re-queued Jul 24)

---

## AAPL (XLK)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## AMGN (XLV)
- Thesis (2026-08-13): Q2 beat (EPS $6.29, rev $10.05B +10% YoY); MariTide (AMG 133) sole remaining metabolic pipeline asset. Current price $416.18 [yfinance Aug 13]; ABOVE watchlist entry $394 — limit won't fill today. Scotiabank $450 PT (raised from $385 post-Q2 [WebSearch — unverified]) is sole source of 2:1 R:R at planned $394 entry. Wells Fargo $400 / RBC $400 / consensus $357 all below current price — significant analyst disagreement. Watchlist hold at $394.
- Recent catalysts:
  - 2026-08-13: Price $416.18, above $394 planned limit; not actionable today. Wells Fargo PT $400, RBC PT $400 [WebSearch — unverified]; FactSet consensus $357 [WebSearch — unverified]
  - 2026-08-12: AMG 513 Phase 1 discontinued; MariTide sole metabolic pipeline [WebSearch — unverified]; Scotiabank PT $385→$450 Outperform; UBS $420→$440 Buy [WebSearch — unverified]
  - 2026-08-05: Q2 beat: EPS $6.29 vs $5.60 est, rev $10.1B vs $9.43B; 22 products double-digit growth; FY2026 guidance maintained [WebSearch — unverified]
  - 2026-08-04: Screener rank #1 (0.6208 Aug 13); XLV Choppy (ML) vs +4.36% 1mo momentum
  <!-- archive: 15-year CAGR 14.88%; Wells Fargo Equal Weight $400; pre-Q2 prices ~$365 -->
- Open thesis questions:
  - Price $416 vs consensus $357: stock already pricing in Scotiabank optimism; downside to consensus is −14%.
  - Scotiabank $450 PT still unverified in any primary source — Finnhub or EDGAR records needed.
  - MariTide Phase 3 timeline: no near-term readout expected; any pipeline slip = thesis breaks.
  - KO/AMGN 30d correlation 0.60 (near 0.70 cap; elevated sector-correlation risk if XLV Choppy).
- Trade history: Not entered (watchlist hold; price above limit entry)
- Position-aware: 30d corr KO=0.6011 (near cap); XLV sector cap 0/2 ✓; plan limit $394

## AMZN (XLY)
- Thesis (2026-08-04): Post-Q2 AWS re-acceleration (37%, 18-quarter high); consensus PT 22; enter only on pullback to 65-270 for 2:1 R:R with 8.72% ATR stop (current 84 at 52w-high fails R:R floor).
- Recent catalysts: Q2 2026 AWS +37% YoY (fastest 18 quarters); Jefferies Buy 20 (raised post-Q2); consensus 22.64 (62 analysts, Strong Buy); Needham Buy 00
- Open thesis questions: Will AMZN consolidate below 87 52w-high and offer pullback entry? Does JOLTS/NFP compress growth PEs?
- Trade history: Not entered (demoted 2026-08-04 — R:R 1.45:1 at 84 fails 2:1 floor with 8.72% ATR stop)
- Position-aware notes: 30d correlation with KO=-0.11, UNP=+0.10 (low); XLY sector cap 0/2
## AVGO (XLK)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## BA (XLI)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## CAT (XLI)
- Thesis (2026-07-02): Dropped — R:R 1.52:1 at $991.41 (fails 2:1 hard floor) + Michael Burry opened SHORT (Jul 1-2; first-ever short on CAT, reversing longtime bull stance; cites "extreme valuation + overexposure to AI/infra theme"). Meta cloud selloff pulled CAT from $1,073.46 (Jul 1 high) to $991.41 (Jul 2; −7.5%). Stop 10.83% unclamped = $884.04. Target $1,155 [WF, Jun 23]. For 2:1: need entry ≤$949.43. NOT watchlist-eligible at current price. Re-evaluate only below $949. [Dropped. Finnhub + yfinance, Jul 2]
- Recent catalysts:
  - 2026-07-02: Michael Burry opened short on CAT — first-ever short, reversing longstanding bull stance; cites extreme valuation + AI-infra overexposure [Finnhub, 2026-07-01/07-02].
  - 2026-07-02: CAT added to Russell Top 50 Index (forced institutional buying from rebalancing) [Finnhub, 2026-07-02].
  - 2026-07-01: CAT 52w high $1,073.46; then sold off to $991.41 by Jul 2 on Meta cloud rotation [yfinance, Jul 1-2].
  <!-- archive: 2026-06-29: Two EDGAR Form 4 insider filings -->
  <!-- archive: 2026-06-25: Wells Fargo raised CAT PT to $1,155 [Finnhub, Jun 25] -->
  <!-- archive: 2026-06-23: Chevron/Microsoft "Project Kilby" names CAT as turbine supplier; CAT +3.05% -->
  <!-- archive: 2026-06-20: "309.4% overvalued" critique -->
  <!-- archive: 2026-05-09: Evercore ISI PT $878→$1,103 -->
- Open thesis questions:
  - 2:1 R:R threshold: entry ≤$949.43 needed (CAT at $991.41; must fall $42 more).
  - Does Burry's short indicate institutional sentiment flip? Burry is typically right long-horizon. Monitor for price approaching $949 with Burry thesis vs WF $1,155 thesis.
  - Form 4 filings Jun 29 unreviewed — still outstanding.
  - Process note: JPMorgan $1,125/$1,165 PT date discrepancy unresolved — carry forward.
- Trade history: (none yet)
- Position-aware notes: 0/2 XLI sector cap (no open positions).

## COST (XLP)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## CVX (XLE)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## DIA (BROAD)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## DIS (XLC)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## GOOGL (XLC)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## HD (XLY)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## IWM (BROAD)
- Thesis (2026-06-16): At all-time highs ($294.64, −1.1% from 52wH $297.91); BREAKOUT setup thesis fails on R:R 1.37:1 (need $340 target for 2:1 vs 7% ATR-clamped stop; best AI forecast $326.80 [Tradestie]). Zombie-firm debt wall ($368B at 6.5% refinancing) and FOMC/Warsh hawkish risk are the structural bears. Screener top pick on momentum (YTD +12%) but not enterable pre-FOMC at ATH. [Demoted: R:R 1.37:1. WebSearch Jun 16]
- Recent catalysts:
  - 2026-06-16: Iran-US peace deal (signing in Switzerland Jun 19) — SPX +1.65%, oil at 2026 lows (WTI $80.47), IWM near ATH on risk-on
  - 2026-06-17: FOMC decision (Warsh's first meeting as Chair) — rate hold expected; dot-plot/tone is the wildcard
- Open thesis questions:
  - Will Warsh's first dot plot shift bias from easing to neutral? (direct hit to small-cap floating-rate debt thesis)
  - At what IWM pullback level does R:R clear 2:1 vs $326 target? (≈ $294 entry gives 7% stop to $273 → R:R = ($326−$294)/$21 = 1.52:1; still fails)
  - Is there a cited sell-side level for IWM/Russell 2000 above $340 that would clear the floor?
- Trade history: (none)
- Position-aware notes: BROAD ETF — sector cap exempt; no correlation gate with other names

## JNJ (XLV)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## JPM (XLF)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## KO (XLP)
- Thesis (2026-08-11): OPEN — 224sh avg $87.42, stop GTC $81.30. Q2 beat (6% volume-led organic growth, FIFA tailwind), analyst PT cluster ($93-$104). Valuation at 26× trailing = near fair value (DCF ≈ current price) — upside requires $104 UBS/Jefferies realization. −0.81% unrealized at $86.71. Thesis intact; defensive bid expected if CPI hot or recession fears materialize.
- Recent catalysts:
  1. 2026-08-11: Ultra-processed food regulation delayed by White House [Bloomberg/Finnhub Aug 10] — regulatory overhang reduced (mildly positive)
  2. 2026-08-10: "26× trailing near fair value; DCF near current price" [Finnhub Aug 10] — valuation flag; not thesis-breaking
  3. 2026-08-07: Monster Beverage Q2 record $2.54B +20.2% YoY — strong beverage sector peer [Finnhub Aug 7]
  4. 2026-08-06: UBS $98→$104, JPM $90→$96, RBC $87→$96; consensus JPM raised to $96 per Q2 upgrade cycle [WebSearch — unverified]
  5. 2026-07-28: Q2 EPS 97¢ beat 93¢; revenue $13.38B (+7% YoY), volume-led (5% vol, 1% price/mix); FIFA tailwind; FY guidance raised [CNBC Jul 28]
  <!-- archive: Barclays $91→$93 (Jul 30); Berkshire Q2 strong; KO ATH $90.92 (Jul 29); Fairlife ransomware resolved -->
  <!-- archive: Core PCE +3.3% YoY benign (Jul 31); Monster Beverage Q2 record; 7-Eleven competitor note -->
- Open thesis questions:
  - Valuation concern: 26× trailing near the high end of KO's historical range; sub-2:1 R:R at consensus $94.70
  - India market share loss Q2 — one-quarter anomaly or structural?
  - Fairlife breach litigation risk (1TB data; KO refused ransom) — ongoing
  - CPI Aug 12: hot print may drag defensives (oil costs); benign = rate-relief supports multiple
- Trade history: PULLBACK fill Jul 31 @ avg $87.42 (224sh, $19,582 cost basis). GTC stop $81.30. Target $104.
- Position-aware notes: Stop active (order 80097d5a, GTC, expires Oct 30). Tighten at +15% ($100.53) to 1.75×ATR; +20% ($104.90) to 1.25×ATR.

## LLY (XLV)
- Thesis (2026-06-11): At 1.85% off the 52w high ($1,182.73) and 41.2x trailing/26.1x fwd P/E, GLP-1 leadership is fully priced in. Consensus PT median $1,251 (BofA 05-26) implies only +7.7%, vs a real 7.95% ATR stop → R:R 0.98:1, fails 2:1 floor (even Truist's $1,281 only reaches 1.30:1). Continued bullish flow (Citi "compelling" note, oral GLP-1 diabetes data beating Novo/AZ, fresh 52w high) but no valuation cushion. Demoted on math, not thesis. [Demoted: R:R 0.98:1. analyst_data.py + WebSearch Jun 11]
- Recent catalysts:
  - 2026-06-11 [Seeking Alpha]: 1-in-10 employers may drop GLP-1 coverage in 2027 — multi-year pricing tail risk
  - 2026-06-09 [Yahoo Finance]: LLY hit fresh 52-week high alongside AAPL/OSCR
  - 2026-06-08 [Yahoo Finance]: Oral GLP-1 pill data beat Novo Nordisk/AstraZeneca diabetes trial readouts
  - 2026-06-08 [TipRanks/Citi]: Citi reiterates bullish "This Is Compelling" note
  - 2026-05-26 [BofA Securities]: PT raised to $1,251 from $1,133 (Buy); Truist $1,281 Buy (May 21)
  <!-- archive: 2026-05-27 ASCO/ADA catalyst confirmed; 2026-05-22 retatrutide 12mg tolerability risk; 2026-05-21 TRIUMPH-1 positive; 2026-05-19 Barclays NVO oral Wegovy note; 2026-05-26 Endowment $577M routine -->
- Open thesis questions:
  - FDA/court ruling on compounded GLP-1 availability — could materially impair pricing and revenue
  - Employer GLP-1 coverage pullback for 2027 — how material to revenue if it spreads beyond early adopters?
  - Would need a fresh PT raise above ~$1,260 (vs current $1,251 median) to clear 2:1 against the 7.95% stop — watch for post-ADA analyst updates
- Trade history: (none yet)
- Position-aware notes: 0% XLV exposure (no open positions as of 06-11). LLY > $1,060 gate cleared (now $1,160.80) — gate is no longer the blocker, R:R math is.

## MA (XLF)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## META (XLC)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## MRK (XLV)
- Thesis (2026-06-08): Within 3.5% of 52w high ($125.14); 29-analyst Buy consensus (avg PT $129.74-136.50, ~7-13% upside) clears the credible-target bar at only R:R 1.86:1 — fails the 2.0 floor. Only the outlier-high $150 estimate (top of a $100-150 range) produces ≥2:1, which the B3 audit specifically flags as a cherry-picking error. Pipeline catalysts (Cidara/CD388, Winrevair Phase 2, ASCO intismeran autogene data) are real but already-priced; Keytruda patent-cliff overhang capped the stock at -3.19% as recently as 6/1. Best non-XLK/XLI diversification (corr -0.02 vs CAT) but math doesn't clear. Demoted. [Demoted: R:R 1.86:1 on consensus target. WebSearch/S&P Global Jun 8]
- Recent catalysts:
  - 2026-06-08: 29-analyst Buy consensus avg PT $129.74 (S&P Global); pipeline: Cidara/CD388 acquisition, Winrevair Phase 2 CADENCE positive topline, ASCO 5-yr intismeran autogene + Keytruda melanoma data [WebSearch Jun 8]
  - 2026-06-01: -3.19% single-session move — Keytruda biosimilar/patent-cliff overhang remains live even in a "Trend"-tagged sector [TradingKey Jun 1]
- Open thesis questions:
  - Can MRK clear its own $125.14 52w high on the dated pipeline catalyst flow, or does the Keytruda-cliff overhang keep capping it below the consensus PT range?
  - Is the $150 high-end analyst estimate ever a defensible 2:1 target, or does it stay an outlier vs. the $129-136 consensus the Street actually believes?
- Trade history: (none yet)
- Position-aware notes: XLV currently 0% exposure (fresh sector if entered); near-zero correlation with AMD/CAT (-0.02) — best factor diversification of any candidate screened to date.

## MS (XLF)
- Thesis (2026-06-25): Demoted again (8th consecutive session) — R:R 0.56:1: entry/stop/target math now decisively failing, spot has run further past the static $230 ceiling that's anchored the (already weak) bull case for weeks. Only fresh catalyst is non-PT-moving: dividend raise + buyback reauthorization. No dated analyst PT raise above spot has surfaced. Recommend continuing to treat as de-prioritized in active rotation (carried weekly-review item, still unresolved). [Demoted: R:R 0.56:1, decisive fail (8th consecutive). market_data.py/analyst_data.py (yfinance, post TLS-proxy fix) + Finnhub, Jun 25]
- Recent catalysts:
  - 2026-06-25: MS announces dividend raise + buyback reauthorization — capital-return signal, not PT-moving; no dated analyst target reaction yet [Finnhub]
  - 2026-06-25: No dated analyst PT raise above spot found; Barclays $230 (dated 2026-04-16) remains stale high-water mark [market_data.py/analyst_data.py]
  <!-- archive: 2026-06-23: No new MS-specific dated catalyst found; Barclays $230 confirmed still the highest dated individual target (dated 2026-04-16) -->
  <!-- archive: 2026-06-22: "Soaring Profits in Emerging Markets Build Case for a Raging Bull Market" — MS-desk commentary, broader market thesis not MS-specific -->
  <!-- archive: 2026-06-19: MS quietly added Bitcoin exposure, cut crypto-ETF fee to 0.14% -->
  <!-- archive: 2026-06-18: "The Quiet Revolution at the Fed: U.S. Banking Sector Received a Catalyst More Potent than Rate Cuts" -->
  <!-- archive: 2026-06-12: JPMorgan PT raised to $187 from $179 — still below spot -->
  <!-- archive: 2026-06-19: "MS Stock After 72% One-Year Jump — What Do Valuation Models Suggest Now" -->
  <!-- archive: 2026-06-17: MS rose while the broader market fell on the hawkish FOMC dot-plot — relative-strength data point -->
  <!-- archive: 2026-06-17: "$10 Trillion Wealth + SpaceX Boost" headline — narrative story, no quantified guidance -->
  <!-- archive: 2026-06-09: Annual U.S. Financials Conference (CEO Ted Pick spoke) — no PT-moving guidance -->
  <!-- archive: 2026-06-08: KBW (Konrad) sole bull at $230/+8.6% -->
  <!-- archive: 2026-06-02: $33M Subtle Medical (AI medical imaging) investment led by MS Investment Mgmt -->
- Open thesis questions:
  - Dividend/buyback announcement is capital-return strength, not undervaluation — does it ever translate into a dated PT raise above spot, or does the bull case stay capped at $230 indefinitely?
  - Is the rate-sensitive financials/NIM-expansion tailwind durable, or does it unwind if yields retrace — removing the only thing supporting MS's relative strength?
  - Given 8 consecutive demotions and R:R now at 0.56:1, should MS be formally dropped from active candidate rotation until a fresh dated catalyst resets the math? (weekly-review item, carried 2nd week)
- Trade history: (none yet)
- Position-aware notes: 0/2 XLF sector cap (no open XLF positions); no other XLF candidate in today's shortlist to correlation-check against.

## MSFT (XLK)
- Thesis (2026-08-10): Post Q2-earnings breakout — EPS $4.74 beat $4.24 (+11.8%), revenue $90.01B vs $87.62B; stock surged ~28% over 7 sessions from $349→$500. At $500, R:R FAILS 2:1 floor (7% stop = $465; consensus $563 → R:R 1.80:1). Pre-warm watchlist: wait for pullback to $480 (R:R 2.44:1) OR confirmed PT ≥ $570 from tier-1 bank. Do NOT enter at $500+.
- Recent catalysts:
  - 2026-08-10: 56 analysts "Strong Buy"; avg PT $563.16 (+12.6% from $500); 52w range $349-$553 [WebSearch — unverified Aug 10]
  - 2026-07-29: Q4 FY2026 earnings: EPS $4.74 beat $4.24 (+11.8%); revenue $90.01B vs $87.62B; +28% over 7 sessions; Azure AI + Copilot growth cited [Yahoo Finance/Blockonomi Aug 10 — unverified]
  - <!-- archive: seed: uninitialized prior to 2026-08-10 -->
- Open thesis questions:
  - Does MSFT pull back to $480 pre-CPI or post-CPI (entry threshold for R:R ≥ 2:1)?
  - Will a tier-1 bank (GS/MS/BofA/Barclays) issue PT ≥ $570 to unlock R:R at $500 entry?
  - CPI Aug 12: hot print → 30Y spike → MSFT P/E compression risk. How does MSFT trade if CPI ≥ 3.7%?
- Trade history: (no trades — pre-warm only as of 2026-08-10)
- Position-aware notes: Correlation 0.116 vs KO (excellent). XLK sector 0/2 cap. No shared catalyst with KO/UNP.

## NFLX (XLC)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## NVDA (XLK)
- Thesis (2026-05-27): MU +19% premarket (HBM sold out 2027, HBM4 shipping for Vera Rubin) re-validates AI infrastructure demand chain; NVDA Q1 FY27 beat ($81.6B +85% YoY) + Q2 guide $91B intact; institutional sell-the-news pressure from ER now counterbalanced by supply chain confirmation. COMPUTEX June 1 (Jensen Huang keynote) = next major catalyst. 30y yield 5.01% (gate passed). Conviction: high.
- Recent catalysts:
  - 2026-05-27 [Micron IR / Gemini grounded]: MU Q3 FY26 guidance $33.5B rev (+250% YoY), 81% GM; HBM sold out 2027; HBM4 volume shipments for NVDA Vera Rubin confirmed
  - 2026-05-27 [TD Cowen / BofA confirmed]: NVDA presenting TMT Conference May 28; COMPUTEX GTC Taipei June 1 (Jensen Huang keynote); BofA Global Tech Conference June 4
  - 2026-05-26 [Gemini grounded]: PT wave: Goldman $285, HSBC $325, Truist $307, Craig Hallum $275, Citic $315
  - 2026-05-20 [NVDA IR]: Q1 FY27 beat: rev $81.6B, DC $75.2B (+92%), EPS $1.87; Q2 guide $91B; $80B buyback + 25× dividend
  <!-- archive: 2026-05-22 sell-the-news −3.6%; 2026-05-21 PT wave; 2026-05-25 export risk flagged -->
- Open thesis questions:
  - COMPUTEX June 1: does Jensen Huang announce Vera Rubin timing acceleration or new AI factory deals?
  - AVGO June 3 ER: confirms AI capex 2H ramp?
  - Post-PCE (May 28): does benign PCE resolve institutional sell pressure?
  - Kill-switch: 30y yield > 5.15% → skip entry
- Trade history: (none yet)
- Position-aware notes: sector cap=2 → NVDA + 1 other XLK max. Correlation with LLY = −0.42. Entry gate today: 30y 5.01% ✓ + NVDA > $213 ✓.

## PG (XLP)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## QQQ (BROAD)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## SPY (BROAD)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## TSLA (XLY)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## UNH (XLV)
- Thesis (2026-07-20): DOJ EXPANDED — Claritev antitrust probe now includes new civil investigative demands + collusion allegations with major insurers (broader than prior disclosures). Multiple simultaneous active probes: (1) Medicare billing criminal, (2) Optum Rx + physician reimbursement, (3) Claritev antitrust. Failed earnings breakout intact ($461 high → $423 close on Q2 beat). R:R 2.07:1 at $426 entry (Goldman $490 target, 7.27% stop) passes math BUT binary DOJ gap risk (20-30% gap-down on indictment) makes stop theoretical. DEMOTED — 3rd consecutive week. Do NOT add to watchlist; requires DOJ resolution. [Yahoo Finance, SimplyWallSt Jul 2026 — Gemini grounded — unverified]
- Recent catalysts:
  - 2026-07-20: DOJ probe EXPANDED to Claritev antitrust — new civil investigative demands, collusion allegations with major insurers [Yahoo Finance Jul 2026, SimplyWallSt Jul 2026 — Gemini grounded — unverified]
  - 2026-07-20: Post-earnings analyst raises: MS $529, BofA $512, Goldman $490, Truist $500, WF $485 [WebSearch Jul 20 — Gemini grounded — unverified]
  - 2026-07-16: Q2 2026 massive beat — adj EPS $6.38 vs $4.85 (+31.5%); FY2026 guide $19.50-$20.00 [SEC 8-K Jul 15; CNBC Jul 16]. Failed breakout: $461 high → $423 close.
  - 2026-07-17: Monitor at $426.72. DOJ not resolved. DEMOTED (risk-off Friday + price action).
  - 2026-07-08: DOJ probe confirmed expanded to Optum Rx + physician reimbursement [fiercehealthcare.com Jul 2026]
  <!-- archive: 2026-06-23: Bernstein $492 PT confirmed; DOJ still blocking entry despite R:R 3.00:1 math at $406 -->
  <!-- archive: 2026-06-08: BofA "Buy" upgrade + 5% dividend raise; stock +40% from lows -->
  <!-- archive: 2026-Q1: Adj EPS $7.23 beat; FY2026 guidance raised >$18.25; DOJ criminal + civil opened -->
- Open thesis questions:
  - **DOJ escalation scope:** Claritev antitrust now added to criminal Medicare billing + Optum Rx criminal probes. 3 simultaneous active probes. Executives to address on Jul 29 call — this is a near-term binary event, not a background risk.
  - **Binary gap risk:** indictment or probe expansion → gap-down 20-30%; no trailing stop captures this. Until resolution, entry requires a position size so small that it's not worth the slot.
  - **Failed breakout confirmation:** stock at $426 (Jul 20) vs $423 close Jul 16 = essentially no recovery despite massive Q2 beat. Institutional distribution signal = real.
  - **Re-entry trigger (deferred):** DOJ resolution (favorable settlement or dropped charges) OR price breaks above $461 (reclaims all post-earnings losses) on high volume. Neither expected in near term.
- Trade history: (none yet)
- Position-aware notes: 0% XLV exposure. DOJ disqualifier escalated Jul 20. Entry blocked until DOJ resolution.

## UNP (XLI)
- Thesis (2026-08-11): OPEN — 68sh avg $291.45, stop GTC $271.56. Q2 beat ($3.41 EPS, +7% YoY). UNP-NS merger strongly de-risked: 152 shipper letters of support filed (Nissan, Hub Group, Knight-Swift). UNP+CN MOU signed Aug 11 (strategic North American rail service deal). Consensus PT $321.11 (18 analysts, MarketBeat Aug 4; up from pre-Q2 $299). BofA $334, Citi $349. Dividend ex-date Aug 31 ($1.42/sh, $96.56 income on 68sh). +0.22% unrealized.
- Recent catalysts:
  - 2026-08-11: UNP + CN (Canadian National) signed binding MOU to strengthen North American rail service [WebSearch Aug 11 — unverified] — strategic expansion, incremental positive
  - 2026-08-10: Rail sector bullish tone: "3 Railroad Stocks to Buy" [Zacks/Finnhub Aug 10]; NSC $85B merger arb = event-driven capital active in rail sector [Finnhub Aug 10]
  - 2026-08-07: 152 shipper support letters filed Aug 5 with STB [Finnhub Aug 6 — VERIFIED]
  - 2026-08-04: Analyst PT $331.30 (+11.7%) [Finnhub Aug 4]; 4th record domestic intermodal quarter (Q2) [Yahoo Finance]
  <!-- archive: BofA PT $301→$334 (Aug 6); CSX Q2 record $3.94B (Aug 4); Iran ceasefire rail fuel tailwind (Aug 5) -->
  <!-- archive: PULLBACK entry $291.45 filled Aug 3; GTC stop $271.56 placed Aug 5 (was naked) -->
- Open thesis questions:
  - Consensus PT upgraded to $321.11 (from ~$299 pre-Q2); confirm R:R 2.77:1 on Citi $349; sub-2:1 at $321 consensus
  - STB DOJ antitrust risk remains; timeline mid-2027; shipper support very strong
  - Brent >$92 = fuel cost thesis reversal trigger (Brent $87.90 Aug 11, rising)
  - Recession risk: NFP −23k could signal freight volume contraction within 2-3 quarters
- Trade history: PULLBACK limit $292.00 placed Aug 3; filled $291.45 avg (68sh, $19,818 cost basis). GTC stop $271.56 (placed Aug 5). Target $349.
- Position-aware notes: Stop active (order 650b19c2, GTC, expires Nov 3). Tighten at +15% ($335.17) to 1.75×ATR; +20% ($349.74) to 1.25×ATR.

## RTX (XLI)
- Thesis (2026-08-20): WATCHLIST — buy-stop $227.50 (8th+ attempt; primary slot today). $22.9B Tomahawk + Pentagon multiyear push + new institutional buyers. Aug 19: hit $226.41 (near 52w high $226.88) then closed $220.35 — "sell-the-news" on Tomahawk contract. Breakout pending. BNP $265 PT → R:R 2.36:1. XLI fills 2/2 with UNP.
- Recent catalysts:
  - 2026-08-20: Aug 19 RTX hit $226.41 (near 52w high), closed $220.35 — "sell-the-news" reversal risk noted [yfinance — verified]
  - 2026-08-19: Pentagon Under Sec. Duffey endorses multiyear missile production expansion [Finnhub 2026-08-19 — verified]
  - 2026-08-19: Two new institutional buyers: Meeder Advisory + Great Lakes Advisors [MarketBeat Google News 2026-08-19 — verified]
  - 2026-08-17: US Navy awards $22.9B, 7-year Tomahawk contract; output 60→1,000/yr [Yahoo Finance, StockTitan 2026-08-17 — verified]
  <!-- archive: Aug 14: Pentagon SM-3 7-yr framework; Blue Canyon $620M; Aug 11-13 CH-47 contracts -->
- Open thesis questions:
  - Aug 19 reversal from $226.41 → $220.35 — "sell-the-news"? Or consolidation before breakout?
  - Pratt & Whitney GTF remediation + F135 "undefinitized" = Q3 margin risk
  - XLI fills to 2/2 with UNP — no further industrials entries
  - Warren legislative risk to defense buyback programs
- Watchlist: buy-stop $227.50 (BREAKOUT above 52w high $226.88), stop $211.58 (−7%), target $265 (BNP [MarketScreener Jul 24 — verified]), R:R 2.36:1. Days remaining: 2 (Aug 14 add).

## V (XLF)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## WMT (XLP)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## XLB (XLB)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## XLC (XLC)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## XLE (XLE)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## XLF (XLF)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## XLI (XLI)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## XLK (XLK)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## XLP (XLP)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## XLRE (XLRE)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## XLU (XLU)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## XLV (XLV)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## XLY (XLY)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## XOM (XLE)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)


---

## XBI — SPDR S&P Biotech ETF

- Sector: XLV (Healthcare)
- Thesis (2026-07-13): Screener #2 (ml_score 0.76) XLV Trend; pulled back from 52w high $165.71 to $159.03 (−4.0%). R:R with $174 2021 ATH target = 1.34:1 → fails. Base case $180 = 1.88:1 → fails. TipRanks $214.59 (12-mo aggregate) not usable for swing timeframe. Fourth consecutive demotion; R:R structurally broken. Key: post-CPI (Jul 14), if benign AND XBI reclaims $165.71, fresh BREAKOUT setup warrants re-evaluation with higher cited target. [WebSearch, Jul 13 2026]
- Recent catalysts:
  - 2026-07-13: XBI $159.03 (pulled back 4.0% from 52w high $165.71); failed breakout context
  - 2026-07-13: 2026 YTD biotech M&A: $106B / 201 transactions; full-year $140-160B forecast [WebSearch, Jul 13]
  - 2026-07-10: New 52w high $165.71 (intraday); closed near $164.28; XLV Trend; Biotech M&A wave [Blockonomi, Jul 10]
  - 2026-07-10: TipRanks aggregate analyst consensus $214.59 (12-mo, 146 analysts on components) [tipranks.com/etf/xbi, Jul 10]
  - 2026-07-08: New 52w high $164.35; XLV Trend regime confirmed
  <!-- archive: 2026-07-07: Broke above 52w-high ($161.56→$163.93) on broad risk-on (ISM Services 54.0, benign) -->
- Open thesis questions:
  - **Target resolution (B3 contradiction — ONGOING):** $174 (2021 ATH) gives 1.34:1; $214.59 (TipRanks, 12-mo aggregate) gives 4.99:1 but unusable. Minimum cited near-term target ≥ $178.30 needed for 2:1 from $159.03 + 7% stop. CPI watch: if benign → XBI may re-approach $165 → recheck breakout thesis. If hot → XBI drops further; wait for reset.
  - **Post-CPI re-entry criteria (Jul 15):** XBI closes above $165.71 Jul 14 + benign CPI + institutional analyst PT ≥ $189 found → re-evaluate as BREAKOUT setup.
  - **Note on base case:** rockflow.ai $160-180 base case target is a low-confidence source; not usable for R:R.
- Trade history: (none — demoted pre-synthesis on R:R; not entered)
