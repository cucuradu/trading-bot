# Backlog — deferred until post-paper-phase (week 13+)

Items below are intentionally NOT in the active roadmap. They wait until the
10–12 week paper-trading validation is complete and we have enough data /
operational maturity to justify the extra surface area.

If the paper-trading phase invalidates the strategy, these items become moot.
Revisit this file every Friday during the weekly review.

---

## 1. Streamlit dashboard

`dashboard/app.py`. Pages:
- Regime gauge (with `ml | rule_fallback` source indicator)
- Open positions + unrealized P&L
- Equity curve (daily EOD)
- Circuit-breaker status (daily/weekly/lock)
- Sector heatmap (vs. 50-day SMA + 10-day momentum)
- Kelly inputs panel (N, W, R, f, half_f, current size %)

Run: `streamlit run dashboard/app.py`.

**Constraint**: local-only or behind auth — never expose to open internet.
Even paper account state is sensitive (strategy signals leak).

---

## 2. Multi-broker abstraction

Today: Alpaca-only. `scripts/alpaca.sh` is the only broker wrapper.

If Alpaca pricing/execution quality degrades, factor into:
- `scripts/broker.py` — abstract interface (account, positions, place_order, cancel, close)
- `scripts/brokers/alpaca.py`, `scripts/brokers/ibkr.py` — concrete adapters
- Migration: rewrite skills to call `broker.py` instead of `alpaca.sh` directly

Not worth doing speculatively.

---

## 3. Options module

Currently FORBIDDEN by strategy (`memory/TRADING-STRATEGY.md` rule 1).

Revisit only if:
- 12-week stock strategy validates (beats SPY benchmark)
- A defined edge case exists (e.g., earnings strangles on confirmed catalysts)
- Failsafe must extend to options-mutating operations as well

This is a major architectural addition and a strategy change — requires fresh
forward-test if pursued.

---

## 4. Breadth indicator (NYSE A/D)

A third regime input beyond VIX + SPY-200SMA. yfinance does not provide
advance/decline data. Options:
- stooq (free, manual scrape)
- A paid feed (Tradier, Polygon)
- **Preferred**: have the local PC fetch + include in `ml-insights.json`
  (since the local pipeline already has more bandwidth for data acquisition)

---

## 5. Local-side training pipeline (separate repo)

The Ubuntu PC with the RTX 5060 Ti produces `ml-insights.json` daily.
Repo: **github.com/cucuradu/ml-pipeline** — kept intentionally separate
from this trading repo, never merged or imported here. Current state
(reviewed 2026-05-24):

- Phase 1: data pipeline (yfinance OHLCV + feature engineering) — done
- Phase 2: GMM regime classifier (4 regimes, 3-bar persistence) — done
- Phase 3: GARCH(1,1) volatility forecaster (1d only) — done
- Phase 4: assembly + cron + auto-shutdown — done

**Activation pending** — see [memory/PROJECT-CONTEXT.md](PROJECT-CONTEXT.md)
"Hybrid ML pipeline" section: producer currently pushes to its own repo
root, not to this repo. Cloud reader looks for `ml-insights.json` at this
repo's root — until the producer's `run_pipeline.sh` pushes the file
HERE with a distinct git author, the cloud always uses `rule_fallback`.
Recommended fix (per schema contract): local pipeline clones + pushes
to this repo with author `ml-pipeline-bot`.

**Future work in the ml-pipeline repo (not here):**
- Switch GMM → HMM (hmmlearn) with BIC-selected state count
- Dynamic regime count (3–7) instead of fixed 4
- GARCH 5d forecast (schema reserves the field; cloud doesn't consume yet)
- Per-symbol scoring → `universe_ranking` field
- Pin cluster→label mapping after first fit (avoid phantom regime flips on retrain)
- Add a producer-side `validate()` step pre-push to catch contract drift early

Contract: `docs/ml-insights-schema.md` (this repo) is the source of truth.
Local pipeline must conform; cloud loop ignores unknown fields.

**Consumer side only** in this repo: `scripts/ml_insights.py` and the
contract test at `tests/test_ml_insights_contract.py`.

---

## Investigated and rejected (do NOT re-litigate without new evidence)

### Trend-confirmation entry filter (price > 200-SMA AND 200-SMA rising 10 sessions)

Tested in Phase C across 2020-2022 and 2024-2025 windows. Backed out.
Evidence (`backtest/reports/PHASE-C-FINDINGS.md`):

| Window | with filter | without filter | delta |
|---|---:|---:|---:|
| 2024-2025 fixed_10 | +13.34% | +24.75% | **−11.4pp** |
| 2020-2022 atr_2_5x | −8.80% | +119.69% | **−128pp** |

The filter locked the bot out of the entire post-COVID recovery (200-SMA
was falling for ~12 months), then only allowed entries right as the 2022
bear began. Momentum-rank entry already captures direction; a strict
200-SMA filter on individual names is both redundant and miscalibrated
through regime changes. **Do not re-add unless a fundamentally different
trend definition (e.g., regime-conditional) is being proposed.**

---

## 6. Telegram channel for richer messages

CallMeBot WhatsApp uses URL-encoded GET requests with a practical
~1500-char body limit. The new pre-market WhatsApp brief (20-25 lines)
fits comfortably, but if we ever want multi-message digests or markdown
formatting, Telegram bots are the natural next channel: no URL limit,
markdown supported, free, per-chat rate limit 30 msg/sec. Revisit only
if WhatsApp depth feels constrained.

Implementation sketch: `scripts/telegram.sh` wrapper modeled on
`scripts/whatsapp.sh`; env `TELEGRAM_BOT_TOKEN` + `TELEGRAM_CHAT_ID`;
skills emit the rich version to Telegram and the terse version to
WhatsApp.

---

## 7. Paid news feeds (Polygon, Alpha Vantage premium, MarketAux)

If the free tiers (NewsAPI 100/day, Finnhub 60/min, EDGAR unlimited,
Google News + Reddit free) prove limiting in practice — e.g., NewsAPI
runs out by midday — promote to paid. Order of preference:
1. **Polygon news** — best company news coverage at $29/mo.
2. **Alpha Vantage premium** — adds news sentiment scores; cheap.
3. **MarketAux** — deduplicated financial news.

Only revisit once we have N weeks of "research depth blocked by quota"
events to justify the cost.

---

## 8. Confidence audit loop (post N=30 closed trades)

The weekly review already produces a calibration table (Bull / Bear
claims hit rate). Once we have ≥30 closed trades, formalize into
`memory/CONFIDENCE-AUDIT.md`: rolling 30-trade calibration with
hit-rate by source (newsapi vs finnhub vs reddit), by regime, and by
catalyst type. Feeds back into the synthesis prompt as "down-weight
Reddit when …" rules.

Deferred: needs trade volume to be meaningful. Start writing this file
in week 7-8 once N ≥ 20.

---

## 9. Lower-leverage ML repo asks (defer until items 1-3 of section 5 land)

The ML repo pushes ml-insights.json with regime + sectors today. Items
1-3 of the active ask list (in section 5 above) are: universe_ranking,
anomalies, earnings_calendar. These four are lower priority — flag for
later:

- **`correlation_matrix_30d`** — 820 pairs across the universe.
  Replaces yfinance round-trips in the buy-gate correlation check.
- **`sector_relative_strength`** — sector z-scores vs SPY (not just
  Trend/Choppy/Bear). Gives "by how much" a sector is leading, not
  just "is it leading".
- **`vol_per_ticker`** — realized vol vs 90d baseline. Enables
  vol-aware sizing later in `scripts/sizing.py`.
- **`breadth`** — % of universe above 50/200 SMA. Confirms regime;
  already approximated by `scripts/regime.py`.

---

## Not in backlog (active in current roadmap)

- **HMM regime consumer hook** — Phase B3, reads `ml-insights.json`
- **Half-Kelly sizing** — Phase D4, auto-activates at N=30 closed trades
- **ATR stops, correlation filter, earnings blackout, time-stop** — Phase A
- **Rule-based regime fallback** — Phase B1/B2
- **R-multiple tracking, sector attribution** — Phase D1/D2
- **Walk-forward backtest** — Phase C (deprioritized but on roadmap)
