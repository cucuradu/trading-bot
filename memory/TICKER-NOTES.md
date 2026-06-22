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
- Thesis (2026-06-15): Demoted 6th consecutive session — at $981.61, R:R on Wolfe Research's brand-new $1,250 PT (06-11, +127% raise from $550) is 1.82:1 against the 15%-clamped ATR stop ($834.37) — closest MU has come to the 2:1 floor, but still 0.18 short. 40-analyst consensus median $846 (up from $637.50 on 06-12, reconciled — genuine new PT raises) still implies −13.8% from price, independently failing B3. Goldman's "high bar" caution into 06-24 earnings (9d) remains unaddressed. Do NOT chase. [Demoted: R:R 1.82:1. analyst_data.py + WebSearch (Wolfe PT confirmation) Jun 15]
- Recent catalysts:
  - 2026-06-15: Iran-relief oil collapse (WTI −5.6%) lifts memory/chip names premarket; "MU leads memory chip rally, DRAM surges 6%" [Finnhub headline — unverified primary source]
  - 2026-06-11: Wolfe Research raised PT $550→$1,250 (+127%, "Outperform") — DRAM pricing +200% CY26/+17.5% CY27, NAND +216%/+17%, 2027E rev $226.5B/EPS $135, bit-shipment capped by cleanroom space through 2027 [Investing.com/TipRanks/GuruFocus Jun 11]
  - 2026-06-12: Goldman cautious into 06-24 earnings ("high bar"); memory stocks (MU/STX/WDC/SNDK) rallied on Iran peace-deal hopes + DRAM/NAND price-hike thesis [Finnhub Jun 12]
  - 2026-06-09: small insider BUY (Bjorlin, 63sh, immaterial) [Finnhub Jun 12]
  - 2026-06-24: Q4 FY2026 earnings report (next — 9d; key re-entry catalyst, "could go parabolic" per Motley Fool)
  <!-- archive: 2026-06-08: +7.1% premarket on SK Hynix-NVDA HBM deal headline; still fails R:R at both chase and no-chase prices -->
  <!-- archive: 2026-06-07: CEO Mehrotra sold ~40,000 sh (~$38M, pre-planned 10b5-1) -->
  <!-- archive: 2026-06-05: Screener #1 (ml 1.36) but demoted — R:R 0.87:1; hot NFP +251K adds yield pressure -->
  <!-- archive: 2026-06-03: Morgan Stanley raises MU PT to $1,050; Susquehanna to $1,750 (5/29) -->
  <!-- archive: 2026-06-04: AVGO AH infra-software miss; MU trailing stop hit $986.18 at 13:59 ET -->
  <!-- archive: 2026-06-02/05: COMPUTEX 2026 Taipei (Jensen Huang keynote HBM4 + Vera Rubin) -->
- Trade history:
  - 2026-06-04: r=0.45, regime=Neutral, reason="trailing stop hit on AVGO software miss contagion; HBM thesis intact, catalyst-specific break; peak was +1.25R (HWM $1,088) but 9.47% trail left too much gap-down room"
- Open thesis questions:
  - Wolfe's unprecedented $1,250 PT (06-11) got MU to 1.82:1, closest yet to 2:1 — would a further consensus catch-up (median above $846, e.g. other banks following Wolfe) or a pullback toward ~$900 (R:R≈2.6:1 vs $1,250) be the trigger to clear the floor first?
  - Does 06-24 earnings (Goldman "high bar") become the volatility event that either validates a pullback entry or confirms the bear case?
  - Does the DRAM/NAND spot-pricing data (CY26 +200%/+216% per Wolfe) get independently confirmed before 06-24, or does it remain a single-analyst thesis?

## AMD (XLK)
- Thesis (2026-06-22): Demoted — R:R 1.58:1 best case: entry $537.37 / stop $456.76 (−15.0% ATR-clamped) / target $665 (Barclays, street-high, 06-01) (+23.76%); worst case using Citi's more-recent $575 (06-12) is R:R 0.47:1. AI-infra rotation thesis intensifying (OpenAI+Meta committed 6GW of AMD infra, "Helios" deployments H2 2026) but stock has run +10% since the 06-11 BofA upgrade with no fresh idiosyncratic catalyst since 06-12 — same single/dual-bank-call-vs-consensus gap flagged since 06-15, still unresolved 5+ sessions later. [Demoted: R:R 1.58:1. research.py gather + WebSearch, Jun 22]
- Recent catalysts:
  - 2026-06-21: "AMD's H2 2026 Inflection Is Bigger Than AI GPUs" — OpenAI + Meta each committed 6GW of AMD infrastructure, Helios deployments beginning H2 2026 [Finnhub]
  - 2026-06-20: "Cloud Infrastructure Rotation Intensifies as AMD Surges While Microsoft Stumbles" — AMD +20% monthly, capital rotating from cloud platforms into pure-play AI-infra [Finnhub]
  - 2026-06-19: D.A. Davidson (Gil Luria) flagged valuation contradiction on CNBC — semi ETFs +80% YTD, memory +300%+, multiples disconnecting from fundamentals [Finnhub]
  - 2026-06-19: dated bear note — attractive R:R only on a macro pullback to ≤$440 [Finnhub]
  - 2026-06-12: Citi upgraded to Buy, PT $575 — "AMD is no longer just a CPU stock" [Reuters/Benzinga]
  - 2026-06-01: Barclays street-high PT $665 [WebSearch aggregators]
  <!-- archive: 2026-06-11: BofA raised PT $500→$560, "top CPU pick" on $170B 2030 server-CPU TAM -->
  <!-- archive: 2026-06-10: ARK (Cathie Wood) trimmed AMD, added NVDA same week -->
  <!-- archive: 2026-06-04: AVGO sell-the-news contagion; AMD −3.97% sympathetic -->
  <!-- archive: 2026-06-03: Analyst upgraded to Strong Buy; stock hits all-time high $540.94 -->
  <!-- archive: 2026-06-03: Director sold $5.4M near all-time highs -->
  <!-- archive: 2026-06-01: Mizuho PT raised $515→$615, "Outperform" maintained -->
  <!-- archive: 2026-06-02: Radeon RX 9070 GRE global launch + BofA Tech Conference + Microsoft Build -->
- Trade history:
  - Position exited 06-09/06-10 (TRADE-LOG gap, no entry recorded — thesis-break per 06-08 notes: COMPUTEX exhaustion + NFP yield spike + AVGO contagion)
- Open thesis questions:
  - No third major desk has confirmed the $575–665 range with a fresh, dated note since 06-12 — does the re-rating broaden, or does AMD round-trip back toward the $490 consensus median?
  - "6GW Helios" commitment language (06-21) is directional, not quantified guidance — does a follow-up filing/guide turn it into an R:R-moving number?
  - Single most-likely invalidator: same as 06-15, still unresolved — no third-desk confirmation within 5 trading days of the BofA/Citi/Barclays cluster.

---

## AAPL (XLK)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

## AMZN (XLY)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

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
- Thesis (2026-06-22): Demoted again — R:R 1.66:1, CAT's best reading in 4 sessions but only because today's calc finally used JPMorgan's higher $1,125 PT (previously logged under "2026-05" but never substituted into the live calc — see process note below), not because the setup improved. Entry $985.82 / stop $901.71 (−8.53%, unclamped 2.5×ATR) / target $1,125 (+14.12%). Overvaluation critique escalated from "69%" (06-16) to "309.4% overvalued" (06-20) — bear narrative gaining traction, not losing it. No fresh CAT-specific catalyst since the now-stale backlog headline (4th+ consecutive restatement). Do NOT chase above $1,113 (06-18 gate) — today's $985.82 reference is well clear of it. [Demoted: R:R 1.66:1. research.py gather + WebSearch, Jun 22]
- Recent catalysts:
  - 2026-06-20: "Caterpillar (CAT) Stock Could Be 309.4% Overvalued Despite Strong Share Price Momentum" — escalation from the 06-16 "69% overvalued" critique [Finnhub]
  - 2026-06-22: "The One Stock Now Controlling DIA's Next Move" — restates the data-center power-gen backlog thesis (no new info) [Finnhub]
  - 2026-06-19: CAT +3.1% surge noted on continued strength [Finnhub]
  - Process note: JPMorgan $1,125 PT (logged "2026-05", re-surfaced via WebSearch under a "June 2" batch with UBS $900/Oppenheimer $980 — same number, ~1mo date discrepancy, not a magnitude contradiction) was never substituted into the live R:R calc in 06-17/06-18 sessions, which defaulted to the lower/stale Evercore $1,103 figure instead — likely understated CAT's R:R for ≥2 prior sessions. Flagged for weekly review.
  - 2026-06-16: simplywall.st DCF model flags CAT ~69% overvalued post AI-backlog re-rating [Google News]
  <!-- archive: 2026-05-09: Evercore ISI raised PT $878→$1,103 -->
  <!-- archive: 2026-Q1: Record backlog $63B (+79% YoY); EPS +30% YoY; raised guidance -->
  <!-- archive: 2026-05: Analyst upgrades — JPM $1,125, Argus $990, Morgan Stanley $915, DA Davidson $845 -->
  <!-- archive: 2026-06-04/05: HOLD, INTACT — thesis insulated from NFP/AVGO contagion at $933, trail stop locking gains -->
- Open thesis questions:
  - Now that JPM's $1,125 is the active target (replacing the stale Evercore $1,103), does a fresh named-bank PT above ~$1,142 (needed for 2:1 from today's stop) ever surface, or does the bull case stay capped by a target the market already knows?
  - Will the escalating "309% overvalued" critique gain sell-side traction (a dated downgrade) or stay a single-aggregator DCF outlier?
  - Resource Industries profit −39% YoY (carried question); can data center power fully offset?
  - Single most-likely invalidator: same as 06-18, still live — a broad industrials/cyclicals pullback on higher-for-longer before any new CAT-specific catalyst.

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
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

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
- Thesis (2026-06-22): Demoted again (6th consecutive session, identical structural problem) — R:R 0.44:1: entry $223.17 / stop $207.55 (−7.0%, ATR-clamped) / target $230 (highest individual analyst target, undated) (+3.06%). Consensus ($203.29, 25 analysts) still ~9% below spot, same gap flagged for 6 straight sessions. Only dated analyst action on record (JPMorgan $187, 06-12, Neutral) points *below* spot, not above — every bull bullet this run is sector-level (Fed capital-relief narrative) or tangential (crypto/Bitcoin diversification), no MS-specific dated catalyst. [Demoted: R:R 0.44:1. research.py gather + WebSearch, Jun 22]
- Recent catalysts:
  - 2026-06-22: "Soaring Profits in Emerging Markets Build Case for a Raging Bull Market" — MS-desk commentary, broader market thesis not MS-specific [Finnhub]
  - 2026-06-19: MS quietly added Bitcoin exposure, cut crypto-ETF fee to 0.14% (new category floor) — diversification signal, not core-business catalyst [Finnhub]
  - 2026-06-19: "MS Stock After 72% One-Year Jump — What Do Valuation Models Suggest Now" — valuation-check headline echoing the AMD/CAT overvaluation-pushback pattern [Finnhub]
  - 2026-06-18: "The Quiet Revolution at the Fed: U.S. Banking Sector Received a Catalyst More Potent than Rate Cuts" — sector-level regulatory/capital-relief narrative, not MS-specific [Finnhub]
  - 2026-06-12: JPMorgan PT raised to $187 from $179 — still below spot, most recent dated action on record
  <!-- archive: 2026-06-17: MS rose while the broader market fell on the hawkish FOMC dot-plot — relative-strength data point -->
  <!-- archive: 2026-06-17: "$10 Trillion Wealth + SpaceX Boost" headline — narrative story, no quantified guidance -->
  <!-- archive: 2026-06-09: Annual U.S. Financials Conference (CEO Ted Pick spoke) — no PT-moving guidance -->
  <!-- archive: 2026-06-08: KBW (Konrad) sole bull at $230/+8.6% -->
  <!-- archive: 2026-06-02: $33M Subtle Medical (AI medical imaging) investment led by MS Investment Mgmt -->
- Open thesis questions:
  - The only dated analyst action (JPM, 06-12) points below spot — does any desk publish a fresh target above ~$237 (needed for 2:1 against the 7%-floor stop), or does the static $230 figure keep getting left behind by price?
  - Is the rate-sensitive financials/NIM-expansion tailwind (post-FOMC dot-plot) durable, or does it unwind if yields retrace — removing the only thing supporting MS's relative strength?
  - Single most-likely invalidator: same as 06-18, still live — a reversal in the rate-sensitive financials trade if higher-for-longer cools.

## MSFT (XLK)
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

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
- Thesis (2026-06-08): Sentiment has flipped sharply bullish (BofA upgrade to Buy, dividend +5%, Q1 beat+raise, "40% rally" headlines, stock now $399.47 — near its $404 52w high) — but the active DOJ criminal investigation into Medicare billing remains OPEN/UNRESOLVED per fresh confirmation (no charges yet, no announced resolution timeline). Improving fundamentals do not retire a binary federal-indictment gap-risk that no stop protects against. 7th consecutive drop on the same DOJ basis (6/2 through 6/8). [Dropped — DOJ binary risk unchanged. WebSearch Jun 8; healthcaredive/fiercehealthcare]
- Recent catalysts:
  - 2026-06-08: BofA Securities upgrade to "Buy" + 5% dividend raise drove a fresh pop; stock near 52w high $404.15, up ~40% from recent lows [Barchart/TIKR via WebSearch Jun 8]
  - Ongoing (confirmed still active 6/8): DOJ criminal + civil investigation into Medicare Advantage/Optum Rx/physician-reimbursement billing practices — no charges, no resolution timeline [healthcaredive.com, fiercehealthcare.com via WebSearch Jun 8]
  - 2026-Q1: Adj EPS $7.23 beat; FY2026 guidance raised >$18.25; prior authorization cuts for 30% of services
  <!-- archive: 2026-05: Truist PT raised to $440; median consensus PT $400.50 -->
- Open thesis questions:
  - DOJ criminal investigation: indictment risk → gap-down 15-30%; unmanageable with trailing stop. Does the bullish sentiment wave (BofA upgrade, dividend hike) eventually outweigh this in the bot's framework, or does the binary-risk gate hold indefinitely until the investigation formally resolves?
  - At what point does a 7-session string of identical DOJ-based drops warrant a strategy-level rule (e.g., a standing "no entry while active criminal probe" filter) vs. re-litigating it daily?
  - MLR still elevated; membership down 2.8M in 2026 — does the rally reflect real operational improvement or short-covering/legal-resolution optimism getting ahead of facts?

## UNP (XLI)
- Thesis (2026-06-04): XLI Trend regime; Q1 FY2026 EPS $2.87 (+5.9% YoY), revenue $6.22B (+3.2%); Norfolk Southern integration potential PT uplift; consensus PT $273.36 (26 analysts), Barclays outlier $315 (Apr 24, 2026); current $262.13. DEMOTED — R:R 0.96:1 with year-high $279.70 as target fails 2.0 floor; entry only viable if price retraces to ~$245–250.
- Recent catalysts:
  - 2026-Q1: EPS $2.87, revenue $6.22B (+3.2%); analyst PT wave higher
  - 2026-04-24: Barclays raises PT to $315 [MarketBeat via WebSearch]
- Open thesis questions:
  - Norfolk Southern deal progress — updates at Q2 earnings Jul 23?
  - Freight volume sensitivity to US-China tariff regime?

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

