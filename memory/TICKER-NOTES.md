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
- Thesis (2026-07-21): OPEN POSITION — 25 shares @ $514.61 avg entry (Jul 16). Current $522.45 (+1.52%). GTC trail 15%, HWM $522.44, stop $444.07. AI Summit Advancing AI 2026 TOMORROW Jul 22-23 (San Francisco). Expected: Zen 6 Venice CPU launch, MI455X GPU roadmap, Helios rack-scale (12GW). Potential customer announcements: Microsoft, Anthropic. Cross-risk: Alphabet earnings tonight (AC) — beat would confirm AI capex thesis; miss would dampen Summit narrative. Q2 earnings Aug 4. [Barchart/TradingKey Jul 2026 — Gemini grounded — unverified]
- Recent catalysts:
  - 2026-07-21: AMD +3.75% to $522.45 (Summit pre-event pricing-in; Nasdaq-100 +1.3% premarket on chip names)
  - 2026-07-20: Meta confirmed MI450 GPU + 6th-gen EPYC CPU purchase for H2 2026 [TradingKey Jul 20 — Gemini grounded — unverified]
  - 2026-07-20: Oracle first hyperscaler to launch AI supercluster with 50,000 AMD MI450 GPUs, Q3 2026 [TradingKey Jul 20 — Gemini grounded — unverified]
  - 2026-07-16: UBS raised AMD PT $670→$700 (Buy; maintained amid TSMC-driven selloff) [Stocktwits, Jul 16 — Gemini grounded — unverified]
  - 2026-07-15: KeyBanc raised PT $530→$725 (new street high) [Blockonomi, Jul 15 2026]
  <!-- archive: 2026-07-16: TSMC Q2 2026 record: +77% net profit → confirms AMD chip demand robust [Finnhub, Jul 16] -->
  <!-- archive: 2026-07-15: BofA raised PT $550→$620 (Buy) [TradingKey, Jul 15 2026] -->
  <!-- archive: 2026-07-15: ASML raised AI demand forecast + 30% capacity expansion [Yahoo Finance, Jul 15] -->
  <!-- archive: 2026-07-13: Citigroup upgraded Neutral→Buy, PT $460→$575 [WebSearch, Jul 13] -->
  <!-- archive: 2026-07-08: Goldman Sachs raised AMD PT $450→$640 [prior session] -->
- Trade history:
  - Position exited 06-09/06-10 (TRADE-LOG gap; thesis-break per 06-08 notes)
  - 2026-07-16: OPEN — 25 shares @ $514.61 avg entry (filled ~$514-515 premarket pullback). GTC trail 15% armed.
- Open thesis questions:
  - **Summit binary risk (Jul 22-23):** Alphabet + Meta + MSFT report same days — if hyperscalers signal AI capex slowdown, Summit rally sold into. Key metric: hyperscaler inference GPU orders for H2 2026.
  - **Stop tighten thresholds:** +15% = $591.80 (tighten to 1.75×ATR); +20% = $617.53 (tighten to 1.25×ATR). Neither triggered at $522.45.
  - **Q2 earnings Aug 4:** next binary event. Thesis: strong AI demand visibility from Summit customer wins should provide upside guide.
  - **Sector_bear XLK override:** XLK Bear for 39+ sessions. Position held on thesis strength (hyperscaler wins, hard Summit catalyst). Monitor XLK for regime improvement signal.
  - **Alphabet cross-risk:** GOOGL reports tonight (Jul 21 AC). If cloud/AI capex signal negative → Summit rally dampened. Key metric: Google Cloud revenue growth rate and AI infrastructure CapEx commentary.

---

## ABBV (XLV)
- Thesis (2026-07-21): BREAKOUT setup monitoring — near 52w high $261.64 (3.25% above current $253.38). Skyrizi+Rinvoq revenue ramp driving 12%+ top-line growth; analyst PTs $261-$300 (BMO $300 Jul 13, BofA $276 Jul 10). Entry deferred past Alphabet earnings tonight; window to enter Jul 22-25 before Jul 26 earnings blackout (ABBV reports Jul 31). Buy-stop $262 (BREAKOUT) or limit $248 (PULLBACK support) depending on market reaction.
- Recent catalysts:
  - 2026-07-21: Demoted/deferred — awaiting Alphabet earnings (tonight AC) before entry. Trade slot preserved.
  - 2026-07-13: BMO Capital raised PT to $300 (from prior lower target) [WebSearch Jul 2026 — Gemini grounded — unverified]
  - 2026-07-10: RBC Capital raised PT to $280; BofA raised PT to $276 [WebSearch Jul 2026 — Gemini grounded — unverified]
  - 2026-07-09: Guggenheim raised PT to $261 [WebSearch Jul 2026 — Gemini grounded — unverified]
  - 2026-06-30: Insider BUY — Director Quaggin (62 sh) + Director RAPP (134 sh) at $251.64 [Finnhub Form 4 Jun 30, 2026]
  <!-- archive: 2026-04-29: Q1 2026 beat: revenue $15.0B (+12.4%), Skyrizi +30.9%, Rinvoq +23.3%; FY guidance raised [AbbVie PR Apr 29, 2026] -->
- Open thesis questions:
  - **52w high resistance at $261.64:** must break cleanly on volume to confirm breakout toward $276-$300. Volume surge factor currently -1.614 (below average).
  - **ABBV earnings Jul 31 (10 days):** binary event. Any Skyrizi/Rinvoq miss vs elevated expectations → gap-down. Window to enter = Jul 22-25 only.
  - **FOMC Jul 29 (8 days):** hawkish-hold compresses pharma multiples (30Y 5.06%).
  - **Catalyst factor 0.0:** no near-term events in 14-day window per screener; purely technical/fundamental setup.
- Trade history: (none — first deep-dive Jul 21 2026)

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
- Thesis (2026-07-14): At 52w high ($289.13 vs year-high $290.41); NSC merger STB application accepted May 28, 2026 — transcontinental rail catalyst; consensus PT $291.73 (23 analysts, essentially inline with price); street-high $330 (Morgan Stanley + Jefferies) gives R:R 2.02:1 — barely passes but thin; XLI Choppy regime; earnings Jul 23. DEMOTED — too thin on street-high only; re-entry viable if pulls back below $285 (R:R improves to 2.25:1 at $330).
- Recent catalysts:
  - 2026-Q1: EPS $2.87 (+5.9% YoY), revenue $6.22B (+3.2%)
  - 2026-05-28: STB accepted amended UNP-NSC merger application [Wikipedia/SEC]
  - 2026-07-09: Citigroup raises PT to $326 [Benzinga]
  - 2026-07-14: CPI cool (3.5% vs 3.8%) — macro tailwind for long-duration infrastructure
  - <!-- archive: 2026-04-24: Barclays raises PT to $315 [MarketBeat] -->
- Open thesis questions:
  - STB hearing timeline: will any concession language emerge Q3 2026?
  - Q2 earnings Jul 23: EPS trend continuation or freight volume softening?
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
