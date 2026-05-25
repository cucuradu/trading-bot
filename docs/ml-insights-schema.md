# `ml-insights.json` — schema contract

This file is the **only** interface between the local ML pipeline (Ubuntu PC,
RTX 5060 Ti) and the cloud trading loop (this repo). The cloud loop is a
consumer-only — it never writes this file.

**File location**: repo root (`/ml-insights.json`)

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
  "model_version": "hmm-v1.2",

  "market": {
    "regime": "Bull",
    "confidence": 0.87,
    "persistence_bars": 5,
    "deployment_target": 0.85,
    "trade_slots": 3
  },

  "volatility": {
    "garch_1d_forecast_pct": 1.2,
    "garch_5d_forecast_pct": 2.8,
    "vix_implied_term_structure": "contango"
  },

  "sectors": {
    "XLK": {"regime": "Trend",  "score": 0.74},
    "XLF": {"regime": "Choppy", "score": 0.12},
    "XLV": {"regime": "Trend",  "score": 0.55},
    "XLE": {"regime": "Bear",   "score": -0.41},
    "XLY": {"regime": "Choppy", "score": 0.05},
    "XLP": {"regime": "Choppy", "score": 0.02},
    "XLI": {"regime": "Trend",  "score": 0.38},
    "XLU": {"regime": "Choppy", "score": -0.08},
    "XLB": {"regime": "Bear",   "score": -0.29},
    "XLRE": {"regime": "Choppy", "score": -0.11},
    "XLC": {"regime": "Trend",  "score": 0.61}
  },

  "universe_ranking": [
    {"symbol": "NVDA", "ml_score": 0.91},
    {"symbol": "META", "ml_score": 0.84}
  ]
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

### `volatility` (optional, reserved)
Not consumed by cloud loop in initial implementation. Local PC may populate;
cloud ignores unknown fields gracefully. Will be wired into sizing logic later.

### `sectors` (optional, recommended)
Object keyed by sector ETF symbol. Each entry:
| Field | Type | Notes |
|---|---|---|
| `regime` | enum | `"Trend"` \| `"Choppy"` \| `"Bear"` |
| `score` | float | Signed momentum/score. Sign is the regime hint; magnitude is conviction. |

If present, cloud uses sector regimes to gate per-sector entries (Bear → blocked).
If missing, cloud falls back to [scripts/regime.py](../scripts/regime.py) sectors.

### `universe_ranking` (optional, reserved)
Sorted list of universe symbols by ML score. Not consumed yet. Will be used
later to bias Claude's research focus.

---

## Validation contract

The cloud reader ([scripts/ml_insights.py](../scripts/ml_insights.py)) MUST:

1. Reject if JSON is malformed → fallback.
2. Reject if `generated_at` is missing or > 24h old → fallback.
3. Reject if `market.regime` is not one of the 4 valid values → fallback.
4. Reject if `market.deployment_target` is outside [0, 1] → fallback.
5. Reject if `market.trade_slots` is outside [0, 3] (cap, not error) — clamp instead.
6. Accept unknown fields silently (forward-compatibility for future local fields).
7. Log the fallback reason to `RESEARCH-LOG.md` whenever fallback is used.

---

## Why this contract is frozen

The local PC and the cloud loop are developed independently. Breaking changes
to this schema require:
1. A versioned migration plan (both repos updated in the same week)
2. A backwards-compatible window (cloud accepts both shapes for one rotation)

Treat this file like a public API contract.
