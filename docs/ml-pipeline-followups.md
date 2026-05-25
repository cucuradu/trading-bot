# ML pipeline — suspect numbers + improvements

Captured 2026-05-26 during the audit + re-wiring of the cloud consumer.
None are blocking; cloud loop is now consuming Ubuntu's data correctly.
Triage on the Ubuntu / ml-pipeline side. Update / strike items as resolved.

---

## 1. Suspect numbers in the current producer output

Reference payload: [ml-insights.json](ml-insights.json) at `generated_at = 2026-05-25T09:43:35Z`.

| # | Field | Value | Why suspect |
|---|---|---|---|
| S1 | `market.confidence` | `1.0` | GMM posteriors pinned at exactly 1.0 are unrealistic. Either truncation in JSON serialization, or a degenerate cluster assignment where one component dominates. Real GMM posteriors should land in ~0.6–0.95. |
| S2 | `market.persistence_bars` | `32` | Schema example uses 5. 32 consecutive bars = ~6 weeks in one regime. Plausible if the market has been quiet, but worth confirming the persistence filter counts bars correctly (not e.g. counting hours or accumulating without reset on regime change). |
| S3 | `market.systemic_fragility` | `0.0182` | PCA Absorption Ratio of 1.8% means the top principal component explains only 1.8% of cross-sector variance. In normal markets this is 50–70%. 0.018 implies near-perfect sector decorrelation — implausible. Likely a calculation bug: rolling window too short, eigenvalues normalized wrong, or correlation matrix actually returned an identity-ish matrix. **Highest-priority data anomaly.** |
| S4 | `volatility.garch_1d_forecast_pct` vs `garch_5d_forecast_pct` | `12.01` vs `12.28` | 1d and 5d annualized vol forecasts are nearly identical. GARCH(1,1) should produce diverging 1d vs 5d unless the model is at its long-run mean. Could just mean low-vol regime, but worth a quick check of the forecast-horizon arithmetic. |
| S5 | `universe_weights` | `{"XLB": 1.0}` | With `trade_slots = 1` the inverse-vol weighting layer is mathematically a no-op (one item gets 1.0). Not a bug, just a reminder that the IV step adds zero signal when `trade_slots ≤ 1`. Could be skipped entirely in that branch. |
| S6 | Sector `score` magnitudes | 0.0005–0.0039 | These are 5d forward-return predictions per the architecture doc. All sub-50bps. Tiny relative to typical 5d sector vol (~100–200bps). Suggests very weak forward signal — measure SNR before sizing into these. |
| S7 | `model_version` string | `"hmm-garch-v1.0"` | Architecture doc describes a **GMM** regime model, not HMM. The version string lagged the rename. Free-form per schema, so not "wrong" — just confusing. Cosmetic. |

---

## 2. Cloud-side improvements (this repo)

In rough priority order. None block trading.

| # | Idea | Rationale |
|---|---|---|
| C1 | WhatsApp alert when `resolve()` returns `source: "rule_fallback"` | Today the only signal is a line in `RESEARCH-LOG.md`. If the Ubuntu PC dies and stays dead, you'd miss it for days. One ping per fallback day is enough. |
| C2 | Surface a `degraded_capabilities` list in resolve output when `source = rule_fallback` | So downstream code can short-circuit features that depend on ML-only fields (e.g. systemic_fragility-gated sizing) instead of guessing. |
| C3 | Weekend-aware freshness window | Producer runs nightly but markets are closed Sat/Sun. The 24h check forces a Monday-morning fallback unless Ubuntu runs over the weekend too. Either bump cloud window to 72h on weekends, or have Ubuntu run 7 days/week (it would just emit the same Friday-close inference). |
| C4 | Schema version field + validator check | Add `schema_version: "1.0"` to payload; validator rejects on mismatch (with a versioned migration path). Catches the next breaking change cleanly. |
| C5 | Warn-log when producer adds an unknown top-level field | Currently silently tolerated for forward-compat. Append "producer added unknown field: X" to RESEARCH-LOG.md once per day so drift is visible. |
| C6 | Confidence sanity warning (not reject) when `confidence ∈ {0.0, 1.0}` | Surfaces S1-style anomalies without breaking the loop. |

---

## 3. Producer-side / contract improvements (ml-pipeline repo)

These are asks for the Ubuntu side. Send to the ml-pipeline maintainer.

| # | Ask | Why |
|---|---|---|
| P1 | Investigate S3 — `systemic_fragility = 0.018` | This is the most likely real bug. Either fix the calculation or document why a 1.8% absorption ratio is plausible. Without this, the field is unusable for cloud sizing logic. |
| P2 | Rename payload field `sectors.*.score` → `forward_return_pct` (or similar) | "score" is overloaded across the codebase (momentum z-score in `scripts/market_data.py`, ranking score elsewhere). The producer's "score" is a 5d forward-return prediction — give it a name that says so. Coordinated rename: bump `model_version`, update schema + validator. |
| P3 | Annotate `volatility.*` fields with explicit units in payload comments or schema | They're annualized %, but the field name doesn't say so. New consumers will guess wrong. |
| P4 | Add `persistence_bars_unit` (e.g. `"trading_day"`) to the `market` block | Schema currently says "consecutive bars" without a unit. |
| P5 | Producer-side pre-push validator | Publisher doc references either a CLI-call against a local trading-bot clone or a mirror validator in ml-pipeline. Pick one and document the actual command. Right now there is no proof the producer validates before pushing. |
| P6 | Skip inverse-vol weighting branch when `trade_slots ≤ 1` | Save the cycles; emit `universe_weights = {chosen_sector: 1.0}` directly. Cosmetic, but reduces failure surface. |
| P7 | Investigate S1 — confidence pinned at 1.0 | Likely a serialization rounding or GMM degeneracy. Quick to diagnose with one inspect-step on the Ubuntu side. |

---

## 4. Strike-through log

Items completed by 2026-05-26 audit/fix:

- ~~File location mismatch (cloud reads root, Ubuntu writes `docs/`)~~ — fixed in commit `f4a9f14`.
- ~~Three extra payload fields invisible to cloud (`breadth_divergence`, `systemic_fragility`, `universe_weights`)~~ — formalized in schema + surfaced via validator + resolve in `f4a9f14`.
- ~~Publisher doc fictional API reference + stale git-diff path~~ — fixed in `f4a9f14`.
- ~~Producer contract test fixture lied about wire format~~ — fixed in `f4a9f14`.
