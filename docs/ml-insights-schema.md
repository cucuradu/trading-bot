# `ml-insights.json` — schema contract

This file is the **only** interface between the local ML pipeline (Ubuntu PC,
RTX 5060 Ti) and the cloud trading loop (this repo). The cloud loop is a
consumer-only — it never writes this file.

**File location**: `docs/ml-insights.json` in this repo

**Producer**: separate local repo (HMM/GMM regime classifier + GARCH vol forecaster).
The local pipeline runs nightly and commits + pushes to this repo's `main` branch
using a distinct git author identity (so it's distinguishable from cloud-routine
commits in `git log`).

**Consumer**: [scripts/ml_insights.py](../scripts/ml_insights.py) — reader with
freshness + schema validation. Falls back to [scripts/regime.py](../scripts/regime.py)
on any failure.

---

## Freshness rule

Cloud loop uses the file only if `generated_at` is **less than 24 hours old**
(UTC). Older → treat as missing → fallback to rule-based regime. The pre-market
routine logs the fallback reason to `RESEARCH-LOG.md` so the user notices when
the local PC has drifted offline.

---

## Schema

```json
{
  "generated_at": "2026-05-26T05:30:00Z",
  "model_version": "hmm-garch-v1.0",

  "market": {
    "regime": "Bull",
    "confidence": 0.87,
    "persistence_bars": 5,
    "breadth_divergence": false,
    "systemic_fragility": 0.21,
    "deployment_target": 0.85,
    "trade_slots": 3
  },

  "volatility": {
    "garch_1d_forecast_pct": 12.18,
    "garch_5d_forecast_pct": 13.40,
    "vix_implied_term_structure": "contango"
  },

  "sectors": {
    "XLK": {"regime": "Trend",  "score": 0.0029},
    "XLF": {"regime": "Choppy", "score": 0.0011},
    "XLV": {"regime": "Trend",  "score": 0.0017},
    "XLE": {"regime": "Bear",   "score": -0.0008},
    "XLY": {"regime": "Choppy", "score": 0.0005},
    "XLP": {"regime": "Choppy", "score": 0.0002},
    "XLI": {"regime": "Trend",  "score": 0.0024},
    "XLU": {"regime": "Choppy", "score": -0.0003},
    "XLB": {"regime": "Bear",   "score": -0.0011},
    "XLRE": {"regime": "Choppy", "score": -0.0004},
    "XLC": {"regime": "Trend",  "score": 0.0021}
  },

  "universe_ranking": [
    {"symbol": "XLK", "ml_score": 0.0029},
    {"symbol": "XLI", "ml_score": 0.0024},
    {"symbol": "XLC", "ml_score": 0.0021}
  ],

  "universe_weights": {
    "XLK": 0.42,
    "XLI": 0.33,
    "XLC": 0.25
  }
}
```

---

## Field semantics

### `generated_at` (required)
ISO 8601 UTC timestamp (`Z` suffix). Used for the 24h freshness check.

### `model_version` (required, informational)
Free-form string. Logged in `RESEARCH-LOG.md` for traceability. Bump on every
local model retrain.

### `market` (required)
| Field | Type | Notes |
|---|---|---|
| `regime` | enum | `"Bull"` \| `"Neutral"` \| `"Caution"` \| `"Defensive"` |
| `confidence` | float [0,1] | HMM posterior on dominant state |
| `persistence_bars` | int ≥ 0 | How many consecutive bars in this regime. Cloud uses this for sanity (must be ≥ 3 to act). |
| `deployment_target` | float [0,1] | Fraction of equity to deploy. Cloud caps at 0.85 regardless. |
| `trade_slots` | int [0,3] | Max new entries today. Cloud caps at 3 regardless. |
| `breadth_divergence` | bool, optional | `true` when SPY/RSP 20d divergence triggers. Producer downgrades `Bull` → `Caution` upstream; cloud surfaces the flag but does not yet act on it. If not a bool, silently dropped (does not fail the payload). |
| `systemic_fragility` | float [0,1], optional | PCA Absorption Ratio across 11 sectors. Higher = sectors more correlated = more fragile market. Reserved for sizing logic. Outside `[0,1]` rejects the whole payload. |

### `volatility` (optional, reserved)
Not consumed by cloud loop in initial implementation. Local PC may populate;
cloud ignores unknown fields gracefully. Forecast percentages are **annualized**
realized vol (e.g. `12.18` = ~12% annualized). Will be wired into sizing logic later.

### `sectors` (optional, recommended)
Object keyed by sector ETF symbol. Each entry:
| Field | Type | Notes |
|---|---|---|
| `regime` | enum | `"Trend"` \| `"Choppy"` \| `"Bear"` |
| `score` | float | Signed momentum/score. Sign is the regime hint; magnitude is conviction. |

If present, cloud uses sector regimes to gate per-sector entries (Bear → blocked).
If missing, cloud falls back to [scripts/regime.py](../scripts/regime.py) sectors.

### `universe_ranking` (optional, surfaced)
Sorted list of `{symbol, ml_score}` (descending by score). `ml_score` is the
raw XGBoost forward-return prediction (e.g. `0.0029` = +0.29% expected 5d
return), **not** a normalized momentum score. Cloud surfaces the list via
`resolve()` but does not yet act on it. Reserved for biasing research focus.

### `universe_weights` (optional, surfaced)
`{symbol: weight}` produced by inverse-volatility weighting on the top
`trade_slots` sectors. Weights are in `[0,1]` and sum ≈ 1.0. Empty `{}` when
`trade_slots = 0`. Cloud surfaces this for downstream sizing; entries with
weights outside `[0,1]` are silently dropped.

---

## Validation contract

The cloud reader ([scripts/ml_insights.py](../scripts/ml_insights.py)) MUST:

1. Reject if JSON is malformed → fallback.
2. Reject if `generated_at` is missing or > 24h old → fallback.
3. Reject if `market.regime` is not one of the 4 valid values → fallback.
4. Reject if `market.deployment_target` is outside [0, 1] → fallback.
5. Reject if `market.trade_slots` is outside [0, 3] (cap, not error) — clamp instead.
6. Reject if `market.systemic_fragility` is present and outside [0, 1] → fallback.
7. Silently drop `market.breadth_divergence` if not a bool (do not fail the whole payload over a metadata flag).
8. Silently drop malformed `universe_ranking` entries (require `symbol: str` + `ml_score: number`); silently drop `universe_weights` entries with weight outside `[0, 1]`.
9. Accept unknown fields silently (forward-compatibility for future local fields).
10. Log the fallback reason to `RESEARCH-LOG.md` whenever fallback is used.

---

## Why this contract is frozen

The local PC and the cloud loop are developed independently. Breaking changes
to this schema require:
1. A versioned migration plan (both repos updated in the same week)
2. A backwards-compatible window (cloud accepts both shapes for one rotation)

Treat this file like a public API contract.

---

## Cloud-side fallback ranking (informational, not part of the producer contract)

When this file is stale (> 24h) or missing, `scripts/ml_insights.py:resolve()`
populates `universe_ranking` from a **local 7-factor screener**
(`scripts/screener.py`, Phase F, 2026-05-27) so the cloud trading loop is not
starved of signal during publisher outages.

The screener is deterministic, network-cheap (one batched `yf.download`), and
emits the same `[{symbol, ml_score}, ...]` shape this contract specifies.
`ml_score` from the screener is a z-scored composite of momentum, relative
strength, technical setup, and volatility-stability factors — **not directly
comparable** to the producer's XGBoost forward-return predictions, but
correctly ordered for ranking purposes.

**Producers should ignore this section.** Your contract is unchanged. When
the publisher delivers a fresh payload, `resolve()` uses it and the local
screener output is discarded.
