# Trading Strategy

## Mission
Forward-test this strategy on an Alpaca paper account for 10–12 weeks. Goal: beat the S&P 500 over the validation window. Stocks only — no options, ever.

## Capital & Constraints
- Starting capital (paper): ~$100,000
- Platform: Alpaca (paper)
- Instruments: Stocks ONLY
- PDT limit: 3 day trades per 5 rolling days (applies even on paper for realism)

## Core Rules
1. NO OPTIONS — ever
2. 75–85% deployed
3. 5–6 positions at a time, max 20% each
4. Trailing stop on every position as a real GTC order (ATR-based, see "Stop methodology" below; floor 7%, cap 15%)
5. Cut losers at R ≤ −1 manually (close ≤ initial_stop; respects ATR stop width)
6. Tighten trail: 7% at +15%, 5% at +20% (or equivalent ATR multiplier — see below)
7. Never within 3% of current price; never move a stop down
8. Max 3 new trades per week
9. Follow sector momentum
10. Exit a sector after 2 consecutive failed trades
11. Patience > activity
12. **Universe filter** — only the 40 tickers in `scripts/universe.py` are allowed (Phase A7). Quoting, researching, or trading outside the universe is forbidden.

## Trading Universe (Phase A7)

The bot may only research, quote, or trade tickers in `scripts/universe.py`:
`python scripts/universe.py list`. Universe changes require a dedicated commit
with rationale in the commit body — treat it as a strategy rule, not config.

## Account-level Circuit Breakers (Phase A1)

Run via `python scripts/risk_gates.py check` at the top of every market-touching
skill (`market-open`, `midday`, `trade`). Each gate independent, each tripping
narrows what's allowed:

| Gate | Threshold | Response |
|---|---|---|
| Daily DD | equity ≤ −2% vs. yesterday EOD | Tighten all trails by 30% (e.g., 10% → 7%); no new entries today |
| Daily DD | equity ≤ −3% vs. yesterday EOD | Close all positions in profit; freeze entries 48h |
| Weekly DD | equity ≤ −5% vs. last Friday EOD | Freeze entries until next Monday review |
| Drawdown lock | equity ≤ −10% from all-time peak | Create `memory/LOCK` (records trigger metadata); refuse all buy/sell. Auto-clears once both: 5 consecutive non-negative EOD days **and** drawdown improved ≥3pp from trigger (Phase C). Otherwise manual unlock. |

`memory/PEAK-EQUITY.txt` tracks the all-time high EOD equity. The daily-summary
skill bumps it whenever today's EOD > prior peak. The drawdown lock is the
hardest stop — if `memory/LOCK` exists, no skill may place orders.

**Auto-recovery (Phase C)**: when the lock is created it embeds the trigger
`date`, `equity`, and `dd_pct`. On every `risk_gates check`, if the lock is no
longer tripping AND both of the recovery conditions below hold, `check_all`
deletes the LOCK file and reports `lock_auto_recovered` in its JSON output:

1. ≥ 5 consecutive EOD entries after the trigger date that are non-negative
   day-over-day (no down day in the streak).
2. Current drawdown improved by ≥ 3 percentage points vs. the trigger dd.

If only one condition holds, the lock stays. If the lock was created by a
non-DD path (or pre-Phase-C, without metadata), auto-recovery is disabled
and the user must delete the file manually.

## Stop methodology (Phase A2 — ATR-based, supersedes flat 10%)

| Mechanism | When | Math |
|---|---|---|
| Initial stop | At entry | `entry − 2.5 × ATR(14)`; floor 7%, cap 15% |
| Trailing default | GTC, live | Same width; recomputed daily by `midday` skill |
| Profit-tighten | At +15% unrealized | Shrink ATR multiplier to 1.75× |
| Profit-tighten | At +20% unrealized | Shrink ATR multiplier to 1.25× |
| Hard cut | Close ≤ initial_stop (R ≤ −1) | Market-close immediately, do not rely on GTC |
| Time stop | 10 trading days flat (−3% ≤ P&L ≤ +3%) | Close, free up capital |
| Regime override | Defensive market regime | Close winners, hold stops; no new entries |

Concrete commands (Phase A2/A3/A4):

```
# ATR width for a candidate (returns stop_pct clamped to [7, 15] + stop_price)
python scripts/market_data.py stop-for-entry SYM

# Raw ATR(14) + multipliers (use during midday trail recompute)
python scripts/market_data.py atr SYM

# Earnings-blackout check before any buy
python scripts/market_data.py earnings SYM

# Correlation with existing positions (Phase A3 — must be ≤ 0.70)
python scripts/market_data.py max-correlation-with CANDIDATE EXIST1 EXIST2 ...
```

## Entry Checklist
- Specific catalyst?
- Sector in momentum (and sector not in Bear regime)?
- ATR(14) computed; stop width within [7%, 15%]?
- Target (min 2:1 R:R)?
- Correlation with existing positions < 0.70?
- Earnings not in next 5 trading days (unless catalyst IS earnings)?
- Symbol in TRADING_UNIVERSE?

## Buy-side Gate (ALL must pass before placing a buy)

Reference implementation: `tests/buy_gate.py`. All checks run at the same time;
the gate reports every failure, not just the first.

System-level kill switches (override everything):
- `memory/LOCK` is NOT present
- Daily-DD response is NOT `freeze_entries_48h`
- Weekly-DD response is NOT `freeze_until_monday`

Per-trade:
- Symbol IS in `TRADING_UNIVERSE` (Phase A7)
- Instrument is a stock (not an option, not anything else)
- Total positions after this fill ≤ 6
- Trades this week (including this one) ≤ 3
- Position cost ≤ 20% of account equity
- Position cost ≤ available cash
- `daytrade_count` < 3 (PDT room on sub-$25k accounts)
- Specific catalyst documented in today's RESEARCH-LOG entry
- Max pairwise 30d correlation with existing positions ≤ 0.70 (Phase A3)
- Days to next earnings ≥ 5 OR catalyst IS earnings (Phase A4)
- **Sector cap (Phase C)**: ≤ 2 existing positions in the candidate's sector
  (lookup via `python scripts/universe.py sector SYM`). BROAD ETFs exempt.
  This rule was added after the Phase C backtest sweep showed it adds
  +5-6pp annualized return over a 2-year window vs. an uncapped baseline,
  with no change in trade count.

## Sell-side Rules
- Close ≤ initial_stop (R ≤ −1) → close immediately at market (Phase C: was a flat
  −7% rule; widened to respect ATR-sized stops so a high-vol position takes its
  full planned risk instead of being cut short)
- Thesis broken (catalyst invalidated, sector rolling, adverse news) → close even if not at −7%
- Up ≥ +20% → tighten trailing stop to 5% (or 1.25 × ATR width, whichever is wider)
- Up ≥ +15% → tighten trailing stop to 7% (or 1.75 × ATR width, whichever is wider)
- Position flat (−3% to +3%) for 10 trading days → close (time stop, Phase A5)
- Sector has 2 consecutive failed trades → exit all positions in that sector
- Market regime = Defensive (Phase B) → close winners, hold stops, no new entries

## Position sizing (Phase D4)

Until N=30 closed trades: flat 20% max per position (current behavior).

From N=30 onward: **Half-Kelly** sizing kicks in automatically. The switchover
is data-driven — when `python scripts/trade_log.py count` reaches 30, every
new entry consults `python scripts/sizing.py recommend <regime> <equity>`.

Formula:
- `W = win_rate` over all closed trades in `memory/TRADE-LOG.md`
- `R = avg_R_win / |avg_R_loss|` (payoff ratio)
- `f = W − (1 − W) / R` (Kelly fraction)
- `f_half = max(0, f) × 0.5`
- `pre_clamp_pct = f_half × 100 × regime_factor`
- `size_pct = clamp(8%, 20%, pre_clamp_pct)`

Regime factors: Bull ×1.0, Neutral ×0.85, Caution ×0.50, Defensive ×0.0.
Degenerate samples (no wins or no losses) default to the floor (8%).

On the entry that triggers the switchover (N=30 → N=31), market-open sends a
one-off WhatsApp alert: `"Half-Kelly sizing now ACTIVE — W=X.XX, R=Y.YY,
expectancy=Z.ZZ"`.

## TRADE-LOG.md canonical line formats (Phase D1)

Beyond the human-readable prose, two machine-parseable line formats are
required. Both have their own line in `memory/TRADE-LOG.md`:

```
- EOD YYYY-MM-DD: equity $X,XXX.XX
- OPEN YYYY-MM-DD: SYM entry=PRICE initial_stop=STOP shares=N regime_entry=REGIME sector=XL? sizing=METHOD thesis="..."
- CLOSED YYYY-MM-DD: SYM entry=PRICE exit=PRICE initial_stop=STOP shares=N regime_entry=REGIME sector=XL? pnl=$X.XX r=R.RR reason="..."
```

Parsers:
- `scripts/risk_gates.py` reads EOD lines for daily/weekly DD.
- `scripts/trade_log.py` reads CLOSED lines for D1/D2/D3 aggregates and the
  Phase D4 N-counter (drives sizing-method switchover).

The OPEN line is reference data for the exit-side skill: when a trailing stop
hits or a position is cut, the skill grep's the matching OPEN line to recover
entry, initial_stop, regime_at_entry, and sector — the inputs needed to write
the CLOSED line with correct `r=` and `pnl=`.

R-multiple formula (long positions):
- `r = (exit_price − entry_price) / (entry_price − initial_stop)`
- A stop hit at the initial stop yields `r = -1.0` exactly.
- The `initial_stop` value in the OPEN line must NEVER be edited later, even
  when the trail tightens. R-multiple math depends on the original risk level.

## Performance attribution (Phase D1/D2/D3)

The Friday weekly-review reads aggregates from `scripts/trade_log.py`:

```
python scripts/trade_log.py stats-since <YYYY-MM-DD>  # week-only
python scripts/trade_log.py stats                     # phase-cumulative
```

Captures:
- **D1 R-multiples**: avg_r_win, avg_r_loss, payoff_ratio, expectancy.
- **D2 sector attribution**: P&L grouped by sector ETF (XLK/XLF/.../BROAD).
  Empirically validates or rejects "follow sector momentum" thesis.
- **D3 regime-conditional**: P&L and win-rate bucketed by regime at entry.
  Confirms whether the bot trades better in Bull than Caution.

**Expectancy guardrail**: if rolling 4-week `expectancy < 0.2` for 4
consecutive weeks → mandatory strategy review, blocks new trades until done.

## Regime gauge (Phase B)

Each morning, `pre-market` resolves a market regime + per-sector regimes:

1. **Primary**: read `ml-insights.json` if present and `generated_at` < 24h old.
   Schema in [docs/ml-insights-schema.md](../docs/ml-insights-schema.md). Local
   Ubuntu PC (RTX 5060 Ti) writes this overnight. Cloud loop NEVER writes it.
2. **Fallback**: `scripts/regime.py current` (rule-based: VIX + SPY-200SMA + SPY 20d).

Resolve via:

```
python scripts/ml_insights.py resolve     # one call — does both above
```

Returns JSON with `source` (`"ml"` or `"rule_fallback"`), `market.regime`,
`market.deployment_target`, `market.trade_slots`, and `sectors.*`.

Market regimes drive daily slot count and target deployment:

| Regime | Deployment | Slots | Posture |
|---|---|---|---|
| Bull | 85% | 3 | Full deployment |
| Neutral | 75% | 2 | Default |
| Caution | 50% | 1 | One trade max, tight stops |
| Defensive | 0% | 0 | No new entries; hold winners |

**Stability filter**: regime must persist ≥ 3 trading days before posture
change (matches the tutorial's anti-whipsaw rule). The rule-based classifier
exposes `persistence_bars` and `stable`; the ML path exposes `confidence` and
`persistence_bars` in the same field.

**Classification rules** (rule-based fallback, also documents what the ML
classifier should converge to):

Market:
- `Defensive`: VIX > 30
- `Caution`: VIX ∈ [22, 30] OR SPY < 200-day SMA
- `Bull`: VIX < 15 AND SPY > 200-SMA AND SPY 20-day return > 0
- `Neutral`: everything else (default)

Sector (each XLK/XLF/.../XLC vs. its 50-day SMA + 10-day return):
- `Bear`: ETF < 50-SMA OR 10d return < −4%
- `Trend`: ETF > 50-SMA AND 10d return > +2%
- `Choppy`: anything else

Sector-Bear blocks new entries in that sector — a hard rule, not a
Claude-discretion item.

**Skill integration**:
- `pre-market`: resolves regime, writes header line to RESEARCH-LOG, caps day's `trade_slots`.
- `market-open`: re-resolves at the bell; flips to conservative if regime changed since pre-market.
- `daily-summary`: logs `- Regime YYYY-MM-DD: ...` line; flags transitions.
- `weekly-review`: bucket win rate + R-multiple by regime (Phase D3).
