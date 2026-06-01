# Macro Framework

One paragraph per trading day. Pre-market writes the new paragraph after
reading the prior day's, so the file is a running macro thesis with explicit
day-over-day diffs. Each entry begins with a `## YYYY-MM-DD` heading so
`scripts/research.py macro` can return the most recent block.

Captures: regime + key yield level + USD trend + oil/commodities + breadth +
VIX term structure + the dominant theme of the day. Older paragraphs auto-archive
to memory/MACRO-FRAMEWORK-ARCHIVE.md during the weekly review (>30 days old).

---

## 2026-05-25

Regime: **Neutral** (rule_fallback; ml-insights.json not yet wired to this repo).
Slots 2, deployment target 75%. **SPY 7,473.47** (eighth consecutive weekly gain).
**VIX 16.70** — low/complacent. **30y yield 5.07%** (−4.6bp WoW), off the
mid-week peak of 5.19% (19y high); the yield-driven multiple-compression risk
is easing for now. **WTI $90.83 (−5.77%), Brent ~$94.7 (−5.4%)** — sharp
decline on Iran/Hormuz peace-deal optimism; ESM26 futures +0.51% to 7,504
(market reading lower oil as disinflationary). Binary risk: deal closes → oil
keeps fading + equity tailwind; deal breaks → XLE gaps, cross-asset spillover.
Sector picture: 3 Trend (XLK +1.01σ, XLE +0.43σ, XLV +0.34σ), 6 Choppy,
2 Bear (XLU, XLB) — broadening beyond tech. **Dominant theme**: broadening
rally with oil-driven inflation relief; but **Wed May 28 = Core PCE (3.4% YoY
consensus) + GDP Q1 2nd estimate** is the week's linchpin. Markets closed today
(Sun) + Mon May 26 Memorial Day; first open = Tue May 27.

## 2026-05-25 (Holiday refresh — Memorial Day; research for Tue May 27 open)

Regime Neutral (rule_fallback; ml-insights.json absent). Slots 2, deployment 75%. **VIX 16.68** (−0.02 from Fri; complacent). **30y yield 5.06%** (−1bp from 5.07%; −13bp from mid-week peak of 5.19% — yield-driven compression risk easing). **WTI ~$91 / Brent $95.43** — oil extended Friday's decline over the 3-day weekend on Iran/US peace-deal optimism; Brent ~−5.4% since Fri. **S&P 500 ESM26 futures +0.15%** (Tue AM pre-market). Trump: Strait of Hormuz blockade stays until formal Iran deal — binary risk unresolved. SPX 8-week winning streak intact. Sector leadership: XLK +15.75% / XLE +4.41% / XLV +2.50% (1mo, all Trend). Dominant theme: Iran-deal oil relief + yield easing = disinflationary tailwind for equities; but **Wed May 28 = Core PCE (3.4% YoY consensus) + GDP Q1 2nd estimate + durable goods** is the week's binary event. vs May 22: yields −13bp WoW, WTI −5.77%, regime unchanged (Neutral), VIX −0.02. [source: WebSearch fallback; Gemini quota exhausted]

## 2026-05-26

Neutral regime (rule_fallback; ml-insights.json stale 26.8h). VIX 16.85 (+0.17). 30y yield 5.04–5.07% (flat ±1bp vs yesterday's 5.06%). DXY: slight retreat. WTI $91.25–91.33 (+0.4%); Brent ~$97.60 — rebounding from Monday's −6.5%/−7% collapse on Iran peace deal hopes; Tuesday rebound driven by fresh US military strikes in southern Iran raising Strait of Hormuz negotiation doubts. SPX futures +0.53–0.69% premarket (7,513 level); VIX futures below 21. 7/11 sectors positive momentum. Sector leadership: XLK +15.75% (Trend), XLE +4.41% (Trend), XLV +2.50% (Trend). Bear: XLU, XLB. Dominant theme: risk-on post-holiday open; Iran oil binary unresolved; Wed May 28 = Core PCE April (consensus 3.4% YoY) + GDP Q1 2nd estimate is week's linchpin. vs yesterday: yields flat (±1bp from 5.06%); oil +0.4% (Iran military escalation bounce from −6.5% Monday); regime unchanged; VIX +0.17.

## 2026-05-27

Neutral regime (rule_fallback; ml-insights.json stale 51h — local PC drift). VIX 17.44 (+0.59 vs yesterday). 30y yield 5.01% (down 3bp from 5.04%; down 18bp from mid-week peak of 5.19%). DXY 99.11 (down 0.1% — dollar drift continuing). WTI $89.87 (−4.1%); Brent $96.16 (−3.5%) — Iran peace deal optimism accelerated oil below $90; Strait of Hormuz reopening narrative is the dominant disinflationary catalyst. MU +19% premarket (HBM sold out through 2027, HBM4 shipping for NVDA Vera Rubin) adds tech AI tailwind. SPX futures +0.28% (7,540). Breadth 56.77% SPX above 50-SMA; 8/11 sectors positive 1mo. Sector leadership: XLK +15.3% (Trend), XLV +3.52% (Trend); Bear: XLU, XLB. XLE divergence: sector-momentum +1.90% but regime classifier Bear (score 0.0098) — following classifier given oil down −4% today. Dominant theme: Iran-peace oil disinflation + AI memory demand confirmation (MU) = risk-on with a binary ceiling at tomorrow's Core PCE (May 28, 8:30am ET, consensus 3.4% YoY). vs yesterday: yields −3bp (5.01% vs 5.04%); oil −4.1% (Iran optimism resumed); VIX +0.59; regime unchanged; DXY −0.1%.

## 2026-05-28

Neutral regime (rule_fallback; ml-insights.json stale 74.9h — local PC drift). VIX 16.73 (−0.71 vs yesterday). 30y yield 5.03% (+2bp vs 5.01%). DXY steady ~99. WTI $90–92 (+2–4%); Brent $96–98 — Iran re-escalation: US forces struck Iranian military site; IRGC struck US airbase; Strait of Hormuz closure risk back. PCE print BENIGN: Core PCE April +3.2% YoY (consensus +3.3%), MoM +0.2% (vs +0.3%) — inflation gate passed. GDP Q1 2026 2nd estimate +1.6% annualized (consensus +2.0%) — weaker growth, supports Fed easing. SPX futures −0.1–0.3% premarket (7,532) — modest pullback on Iran/GDP despite PCE beat. Sector leadership: XLK +16.84% (Trend), XLY +3.88% (Trend), XLV +3.44% (Trend); Bear: XLE (−1.25%), XLU (−2.40%). AI/semiconductor momentum continues — screener top picks MU (1.68), AMD (1.55). Dominant theme: PCE inflation gate cleared → deployment window opened; Iran binary is the new top risk replacing PCE. vs yesterday: yields +2bp (5.03% vs 5.01%); oil +3% (Iran re-escalation); VIX −0.71; regime unchanged; DXY flat.

## 2026-05-29

Neutral regime (rule_fallback; ml-insights.json stale 98.9h — local PC drift). VIX 15.74 (−0.99 vs yesterday 16.73 — lowest this week). 30y yield 4.97% (−6bp vs 5.03%; −22bp from 5.19% peak). DXY steady ~99. WTI $87.30 (−1.8%); Brent $91.17 (−1.65%) — Iran ceasefire extension; Brent −17% MTD, WTI −12% MTD. SPX futures +0.12–0.16% premarket (mild positive). Dell AI server earnings beat (PM May 28) driving AI hardware rally premarket. Economic calendar light: Trade Balance Advance 8:30 AM ET; Fed speakers (Schmid, Bowman, Paulson). Sector leadership: XLK +17.4% (Trend), XLV +5.6% (Trend), XLY +4.5% (Trend); Bear: XLE (−3.5%), XLU (−2.3%). Screener top: MU (1.68, held), AMD (1.66, gate not met). Dominant theme: Iran ceasefire oil disinflation continuing + Dell AI tailwind → tech rally; Friday weekend risk = Iran binary. vs yesterday: yields −6bp (4.97% vs 5.03%); oil −1.8% (ceasefire extension); VIX −0.99; regime unchanged; Dell AI rally fresh tailwind.

## 2026-06-01

Neutral regime (rule_fallback; ml stale). VIX 15.92 (+0.60 from May 29 close 15.32 — uptick on Iran reversal). 30y yield 4.99% (+2bp from 4.97%). DXY steady ~99. **Oil REVERSED: WTI $90.80 (+3.94%), Brent $93.85 (+3.00%)** — Iran/Strait of Hormuz escalation reversed weekend ceasefire optimism; peace deal dampened by ongoing US-Iran strikes and Israel/Lebanon actions. SPX futures +0.22% to 7,596.74 — mildly positive despite oil spike, supported by COMPUTEX catalyst (Jensen Huang unveiled NVDA N1X PC chip + Microsoft partnership). ISM Manufacturing PMI + Construction Spending at 10:00 AM ET (moderate). FOMC Jun 16-17; Jobs Jun 5; CPI Jun 10. AMD Radeon RX 9070 GRE launches globally Jun 2; AMD at BofA Tech Conference Jun 2 + Microsoft Build Jun 2-3; MU at COMPUTEX Jun 2-5 (HBM showcase). Mizuho raised AMD PT $515→$615 on June 1. Sector leadership: XLK +19.76% (Trend), XLV +2.38% (Choppy), XLY +2.13% (Choppy); Bear: XLP (−1.66%), XLU (−5.19%), XLE (−5.63%). Dominant theme: COMPUTEX AI hardware rally partially offsets Iran oil reversal; start-of-month positioning adds tailwind. vs May 29: yields +2bp; oil +4% REVERSAL (Brent $91→$94; ceasefire collapsed); VIX +0.60; regime unchanged; COMPUTEX = fresh tech catalyst.
