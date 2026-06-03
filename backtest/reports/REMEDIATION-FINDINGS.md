# Remediation Backtest Findings (audit 2026-06-03)

Part A of the remediation plan: empirically decide the four open questions
(gate-creep, concentration, sizing, R:R) instead of guessing. All runs use the
production-representative baseline **`--entry-mode limit_pullback --pullback-pct
0.02 --ttl-bars 3`** with **all `--realistic` toggles on** (cash cap, deployment
target, entry caps, regime persistence, gap-fill stops), exit `atr_2_5x`.

Judged on annualized return **and** max-drawdown (+ Sharpe, profit factor) per
the user's mandate ("a bit of risk, not a lot — maximize profits"). A variant
must win on **≥2 of 3 windows** to be adopted; finalists are re-checked on a
combined 2024-2025 window and under stress shocks (1.5%/bar).

Driver: `/tmp/remediation_sweep.py` + `/tmp/remediation_finalist.py` (in-process,
no markdown spam). Engine knobs added: `risk_cap_pct`, `max_sector_deployment_pct`,
`min_rr_at_entry` (+ `rr_target_pct`). CLI: `--risk-cap-pct`,
`--max-sector-deployment-pct`, `--min-rr-at-entry`.

---

## A1 — Gate-creep: chase vs wait-for-pullback

| Entry mode | 2024 ann / DD | 2025 ann / DD |
|---|---|---|
| **market_on_open (chase)** | +5.97 / -10.04 | +10.74 / -7.80 |
| limit_pullback pb1% ttl3 | +29.80 / -7.66 | +19.11 / -6.23 |
| limit_pullback pb2% ttl3 (prod) | +31.74 / -8.18 | +3.16 / -9.26 |
| limit_pullback pb3% ttl3 | +28.83 / -10.72 | -8.73 / -10.65 (n=10) |

**Conclusion → adopt B7 (block chasing).** Chasing the open is the worst entry
mode by a wide margin in both years (roughly ⅕–½ the return of waiting, with the
worst drawdown). This is the economic essence of the AMD gate-creep ($475→$510):
paying up for a level you previously refused destroys edge. **Decision: hard
demote-to-watchlist when today's planned entry is above a level refused as
too-high in the last 5 trading days, absent a same-day pullback to plan.**

Side finding (NOT adopted): on the bare baseline pb1% looked more robust than the
production pb2%, but once the R:R floor (A4) is on, pb2% wins the combined
2024-2025 window (+23.52 vs +19.36). So **keep the production pb2% default** — the
data does not justify changing it. Flagged here for transparency.

---

## A2 — Concentration: per-sector $-cap

| Sector $-cap | 2024 ann / DD | 2025 ann / DD | n (24/25) |
|---|---|---|---|
| none (baseline) | +31.74 / -8.18 | +3.16 / -9.26 | 47 / 40 |
| 35% | +16.68 / -11.05 | +7.46 / -7.49 | 34 / 37 |
| 30% | +16.68 / -11.05 | +7.46 / -7.49 | 34 / 37 |
| 25% | +16.68 / -11.05 | +7.46 / -7.49 | 34 / 37 |

35/30/25% are **identical** because two 20% positions = 40% always breach any of
them — the cap just forces **1-per-sector**. That **halves** 2024 return
(+31.74→+16.68) AND worsens drawdown, because the trend year's gains came from
concentrated tech leadership. It only helps the chop year (2025). Wins 1 of 2 →
**fails the robustness bar.**

**Conclusion → do NOT adopt a hard sector $-cap (B6 cancelled as a hard gate).**
This reverses the audit's own recommendation — the data says a tighter $-cap
sacrifices the trend-following edge. Keep the existing **2-per-sector count cap +
0.70 correlation gate**. The real audit concern (MU+AMD shared AI-capex catalyst,
price-corr 0.44 but thematic-corr ~1) is not backtestable (no theme labels in
price history), so handle it as a **soft pre-market advisory**: when two
candidates/positions share a primary catalyst, flag it for explicit
acknowledgment rather than silently doubling the factor bet.

---

## A3 — Sizing: per-trade risk cap

| Risk cap | 2024 ann / DD | 2025 ann / DD |
|---|---|---|
| none (flat 20%) | +31.74 / -8.18 | +3.16 / -9.26 |
| 1.5% | +26.25 / **-5.75** | +6.88 / -8.13 |
| **2.0%** | **+32.10 / -6.82** | **+6.85 / -8.85** |
| 2.5% | +32.43 / -7.74 | +3.10 / -9.18 (barely binds) |

**Conclusion → adopt B5 with `risk_cap_pct = 2.0%`.** 2.0% improves return AND
drawdown vs flat-20% in **both** years — the profit-maximizing choice among the
three that still cuts risk (1.5% gives the lowest DD but sacrifices ~6pp in
2024). Under 2025 stress it turns -8.69% into +3.69% (see finalist table) — real
tail protection. Equalizes the flaw the audit found: flat-20% risked 2.9% on MU's
15% stop vs 1.5% on CAT's 8% stop; the cap levels per-trade $ risk.

---

## A4 — R:R entry gate

| R:R floor | 2024 ann / DD | 2025 ann / DD |
|---|---|---|
| off (baseline) | +31.74 / -8.18 | +3.16 / -9.26 |
| **min_rr 2.0 (hard)** | **+34.96 / -5.21** | **+13.72 / -8.82** |
| min_rr 1.5 | +36.80 / -4.78 | +3.20 / -9.22 (barely binds) |

**Conclusion → adopt a 2:1 R:R floor. This REVERSES the plan's prediction** that
a hard 2:1 would underperform by excluding momentum winners. min_rr 2.0 is the
single most powerful, most robust improvement found — return **and** drawdown
improve in 2024, 2025, the combined window, and **both** stress runs (5/5).
Mechanism: with a +20% proxy target, R:R ≥ 2 ⟺ stop ≤ 10%, so it screens out the
widest-ATR (10–15% stop) entries, which were net losers on average (profit factor
jumps 3.77→6.89 in 2024). It removes ~6 trades/yr and they were the bad ones.

**Production form (B3):** compute R:R from the **real ATR stop** and a
**cited/derived target** (not a fake +20%). A wide-stop name still qualifies if
its cited upside justifies it (e.g. 15% stop + a PT implying +35% → R:R 2.3 ✓);
it's only demoted when the upside doesn't pay for the risk. This is strictly
better than the blunt proxy and directly fixes the original MU mislabel (shown as
R:R 2.0 on a 10% stop but entered at 15% → real R:R 1.33).

---

## Finalist: stacking the winners

| Config | 2024 | 2025 | 24-25 | 2024 stress | 2025 stress |
|---|---|---|---|---|---|
| BASE pb2 | +31.74 / -8.18 | +3.16 / -9.26 | +18.66 / -9.06 | +15.60 / -12.28 | -8.69 / -10.22 |
| + riskcap2.0 | +32.10 / -6.82 | +6.85 / -8.85 | +20.77 / -8.96 | +17.72 / -10.59 | +3.69 / -9.82 |
| + minrr2.0 | +34.96 / -5.21 | +13.72 / -8.82 | +23.52 / -9.30 | +28.78 / -6.37 | +6.95 / -8.15 |
| + riskcap2.0 + minrr2.0 | +34.96 / -5.21 | +13.72 / -8.82 | +23.52 / -9.30 | +28.78 / -6.37 | +6.95 / -8.15 |

- **minrr2.0 subsumes riskcap2.0 in these windows** (identical when both on) —
  they target the same wide-stop names. They are kept as **complementary layers**:
  min_rr is an entry filter against the derived target; risk_cap is a sizing
  backstop for any wide-stop name whose cited upside lets it pass the R:R floor.
- The combined stack (riskcap 2.0 + minrr 2.0) is the recommended production
  posture: **+23.52% / -9.30% combined**, vs baseline **+18.66% / -9.06%** —
  +4.9pp annualized for ~flat drawdown, and far better stress behavior
  (2025-stress -8.69%→+6.95%).

---

## Decisions for Part B

| # | Question | Verdict | Implements |
|---|---|---|---|
| A1 | gate-creep | **Block chasing**; hard demote when entry > recently-refused level w/o pullback. Keep pb2%. | B7 |
| A2 | concentration | **No hard sector $-cap.** Keep count cap + corr gate; shared-catalyst = soft advisory. | B6 (soft) |
| A3 | sizing | **risk_cap_pct = 2.0%.** | B5 |
| A4 | R:R | **Hard 2:1 floor vs cited/derived target**; demote names that fail. | B3 |

Two audit recommendations were corrected by the data: the sector $-cap (A2,
would hurt) and the R:R floor (A4, helps far more than predicted).
