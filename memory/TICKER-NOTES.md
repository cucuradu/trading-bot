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

---

## MU (XLK)
- Thesis (2026-06-05): HBM structural demand thesis intact (sold out through 2027, HBM4 shipping for NVDA Vera Rubin) but unentreable at current ~$963 premarket. 15%-clamped ATR stop requires ~30% upside for 2:1 R:R; year-high $1,089 only gives 0.87:1. Viable re-entry zone ~$750–870. June 24 earnings (Q4 FY2026) is the next major catalyst — consider re-entry setup post-NFP stabilization if price pulls to entry-eligible level. Hot NFP +251K adds yield-spike pressure on XLK; demoted Jun 5. [Demoted: R:R fails 2.0 floor. WebSearch Jun 5; MarketBeat Jun 4]
- Recent catalysts:
  - 2026-06-05: Screener #1 (ml 1.36) but demoted — R:R 0.87:1 at year-high target fails 2.0 floor; hot NFP +251K adds yield pressure. Pre-market $963 (−3.4% from $996 Jun 4 close). [Alpaca; WebSearch Jun 5]
  - 2026-06-04 13:59 ET: AVGO infrastructure software miss contagion → MU trailing stop filled $986.00 (0.45R, pnl=$1,324.89)
  - 2026-06-03: Morgan Stanley raises MU + SNDK targets; 2–3 years tight memory supply thesis [MS, Jun 2026]
  - 2026-05-27: Q3 FY2026 earnings +19% (HBM sold out through 2027, HBM4 shipping for NVDA Vera Rubin)
  - 2026-06-24: Q4 FY2026 earnings report (next — 19d; key re-entry catalyst)
  <!-- archive: 2026-06-04: AVGO AH infra-software miss; MU trailing stop hit $986.18 at 13:59 ET -->
  <!-- archive: 2026-06-02/05: COMPUTEX 2026 Taipei (Jensen Huang keynote HBM4 + Vera Rubin) -->
- Open thesis questions:
  - At what price does MU become enterable (R:R 2:1)? Need ~$750–870 for year-high target, or a post-June-24 earnings re-pricing lifting analyst consensus above $1,250.
  - Does hot NFP yield spike (30Y → 5.07–5.11%) break XLK momentum for 1–3 weeks or get absorbed?
  - Analyst consensus PT $751–860 is below current price — when does the Street re-rate?
- Closed trade: entry $922.91, exit $986.00, 21sh, initial_stop $784.47, realized_r=0.45R, pnl=$1,324.89, reason=trailing_stop (AVGO software_miss), date=2026-06-04

## AMD (XLK)
- Thesis (2026-06-05): **HOLD, STOP ACTIVE** — Hot NFP +251K adds second pressure layer after AVGO Jun 4 contagion. AMD −3.4% to $505.33 premarket. Structural thesis (MI450/GPU roadmap; Mizuho $615 PT; COMPUTEX AI ecosystem) intact but sentiment headwind continues. Trail 12.6% HWM=$546.37 stop=$477.53. Buffer only 5.5% from $505 — watching closely. GTC trail active; if AMD drops to $477.53, auto-exit. Do NOT lower stop manually. Key risk: further yield spike from hot NFP compresses XLK multiples this session.
- Recent catalysts:
  - 2026-06-04: AVGO sell-the-news contagion (infrastructure software miss); AMD −3.97% sympathetic (sector-wide semiconductor pullback, not AMD-specific) [WebSearch, Jun 4]
  - 2026-06-03: Analyst upgraded to Strong Buy; stock hits all-time high $540.94 [Tradingkey, Jun 2026]
  - 2026-06-03: Director sold $5.4M near all-time highs [CoinCentral, Jun 2026]
  - 2026-06-01: Mizuho PT raised $515→$615, "Outperform" maintained
  - 2026-06-02: Radeon RX 9070 GRE global launch + BofA Tech Conference (CFO Jean Hu) + Microsoft Build
  <!-- archive: 2026-06-02/05: COMPUTEX Taipei 2026 (AI ecosystem; AMD participating) -->
  <!-- archive: 2026-05-05: Q1 2026 earnings (+38% YoY, DC +57% YoY, record FCF $2.6B) -->
  <!-- archive: 2026-05: U.S. Commerce cleared AMD to resume MI308 export reviews → $800M recovery -->
- Open thesis questions:
  - AVGO infrastructure software miss — does hyperscaler capex rhythm shift away from discrete GPUs toward AI accelerators in-house?
  - TSMC CoWoS packaging — can AMD secure enough capacity vs NVIDIA preferential access?
  - Director $5.4M sale near ATH — distribution at top signal or tax/rebalancing?
  - Single most-likely invalidator: AVGO weakness compounds; AMD trailing stop breaches; thesis break confirmed

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
- Thesis (2026-06-05): **HOLD, INTACT** — Data center power re-rating thesis fully insulated from NFP + semiconductor pressure. CAT −0.8% to $933 premarket (XLI/industrials resilience vs XLK −3.4%). Trail 7.97% HWM=$946.83 stop=$871.37 (6.6% buffer). Hot NFP +251K is CAT-supportive (strong labor = strong capex spending = data center buildout continues). Stop locks in +$3.66/sh gain (stop $871.37 > entry $867.71). No change to position; thesis intact.
- Recent catalysts:
  - 2026-06-04: Sector-wide pullback (AVGO contagion) did NOT impact CAT; +1.52% Jun 4 shows thesis isolation; consolidation into NFP [Jun 4]
  - 2026-Q1: Record backlog $63B (+79% YoY); EPS +30% YoY; raised guidance
  - 2026-05: Analyst upgrades — JPM $1,125, Argus $990, Morgan Stanley $915, DA Davidson $845
  - 2026-06: Annual dividend increase expected (32nd consecutive)
- Open thesis questions:
  - Q1 tariff costs $710M — will US-China escalation compound in Q2?
  - Resource Industries profit −39% YoY; can data center power fully offset?
  - XLI sector Choppy (regime score 0.054); sector tailwind absent — thesis is CAT-specific not sector
  - Single most-likely invalidator: US-China tariff escalation targeting industrial machinery category

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
- Thesis (uninitialized): seed entry; pre-market will rewrite on first run.
- Recent catalysts: (none yet)
- Open thesis questions: (none yet)
- Trade history: (none yet)
- Position-aware notes: (none yet)

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
- Thesis (2026-05-27): GLP-1 franchise + retatrutide TRIUMPH-1 data (28.3% weight loss) positions LLY as long-term obesity market leader; ASCO May 29–June 2 + ADA June = near-term data catalysts. Key risk upgraded: 56.5x fwd P/E (revised from 26.3x) + 13% realized-price erosion in Q1 + compounding GLP-1 legal uncertainty. Endowment selling confirmed routine. Conviction: moderate.
- Recent catalysts:
  - 2026-05-27 [ASCO/ADA confirmed]: LLY presenting oncology data (Retevmo + Verzenio) at ASCO May 29–Jun 2; TRIUMPH-1 additional data + cardiometabolic pipeline at ADA Scientific Sessions June
  - 2026-05-26 [BofA Securities]: PT raised to $1,251 from $1,133 (Buy); Truist $1,281 Buy (May 21)
  - 2026-05-22 [Analyst note]: Retatrutide 12mg cohort higher discontinuation rate — tolerability risk at max dose
  - 2026-05-21 [LLY press release]: Phase 3 retatrutide TRIUMPH-1 positive (28.3% weight loss, 80w, primary+key secondary endpoints met)
  - 2026-05-19 [Barclays]: NVO oral Wegovy outselling Foundayo; 13% Q1 realized-price decline noted
  <!-- archive: 2026-05-26 Endowment $577M confirmed routine; 2026-05-25 Q1 rev confirmation -->
- Open thesis questions:
  - FDA/court ruling on compounded GLP-1 availability — could materially impair pricing and revenue
  - NVO oral Wegovy market share vs Zepbound: quantify % shift in new patient starts
  - Retatrutide commercial timeline and FDA submission date?
  - What did ASCO oncology data show — does LLY oncology pipeline add value?
- Trade history: (none yet)
- Position-aware notes: XLV cap 2 → LLY + 1 other healthcare max (UNH/JNJ). Correlation with NVDA = −0.42. Enter after NVDA fills cleanly; LLY > $1,060 gate.

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

## MS (XLF)
- Thesis (2026-06-02): At year-high $212; consensus PT $205.95 < current price → no upside per Street; wealth management growth + AI/crypto exposure priced in; June 9 U.S. Financials Conference (CEO Ted Pick) is next potential catalyst; DROPPED today — sector Choppy, PT below price.
- Recent catalysts:
  - 2026-06-02: $33M Subtle Medical (AI medical imaging) investment led by MS Investment Mgmt
  - 2026-06-09: Annual U.S. Financials Conference (CEO Ted Pick speaks)
- Open thesis questions:
  - Consensus PT $205.95 < current $211 — needs analyst upgrade above $215 for bullish entry thesis
  - XLF sector Choppy (score 0.07); sector not providing directional tailwind

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
- Thesis (2026-06-02): Q1 2026 beat + FY guidance raised >$18.25 adj EPS + AI investment $1.6B + margin recovery; but DOJ criminal+civil investigation is unquantifiable binary gap-down risk; analyst median PT $400.50 (+5.3%); no catalyst next 14d; DROPPED — binary risk not manageable with a stop.
- Recent catalysts:
  - 2026-Q1: Adj EPS $7.23 beat; FY2026 guidance raised >$18.25; prior authorization cuts for 30% of services
  - 2026-05: Truist PT raised to $440; median consensus PT $400.50
  - Ongoing: DOJ criminal + civil investigation into Medicare Advantage practices (no timeline)
- Open thesis questions:
  - DOJ criminal investigation: indictment risk → gap-down 15-30%; unmanageable with trailing stop
  - MLR still elevated; membership down 2.8M in 2026 (exiting unprofitable MA/Medicaid) — revenue headwind
  - Earnings Jul 28; next specific catalyst unclear before then

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

