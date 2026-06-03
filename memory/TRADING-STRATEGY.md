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
3. 5–6 positions at a time, max 20% each, **and per-trade risk ≤ 2.0% of equity** (B5 — the dollar size shrinks below 20% when the ATR stop is wide; see "Position sizing")
4. Trailing stop on every position as a real GTC order (ATR-based, see "Stop methodology" below; floor 7%, cap 15%). **A logged stop is NOT a real stop until verified in Alpaca — see "Protective-stop coverage" (B1).**
5. Cut losers at R ≤ −1 manually (close ≤ initial_stop; respects ATR stop width)
6. Tighten trail: 7% at +15%, 5% at +20% (or equivalent ATR multiplier — see below)
7. Never within 3% of current price; never move a stop down
8. Max 3 new trades per week
9. Follow sector momentum
10. Exit a sector after 2 consecutive failed trades
11. Patience > activity
12. **Universe filter** — only the 70 tickers in `scripts/universe.py` are allowed (Phase A7; expanded 40→70 in Phase F). Quoting, researching, or trading outside the universe is forbidden.
13. **R:R ≥ 2:1 hard floor** (B5/B3, audit 2026-06-03) — every entry's reward-to-risk, computed from the **real ATR stop** and a **cited target**, must be ≥ 2.0 or the name is demoted (watchlist / no full-size entry). Enforced in `tests/buy_gate.py`.
14. **Never chase** (B7) — do not enter above a level you previously refused as too-high unless the stock has actually pulled back to plan. Gate-creep is a demote-to-watchlist, not a discretionary call.

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

### Protective-stop coverage (B1 — audit 2026-06-03)

Every open position MUST be covered by a live protective sell order
(`trailing_stop`/`stop`) for its full share count, AT ALL TIMES. The OTO child
that arms on entry can silently fail to register — the 2026-06-01 incident left
AMD + CAT open **overnight with no stop in Alpaca**, undetected ~18h until the
TRADE-LOG had falsely recorded both stops as "GTC, active". Rules:
- "Alpaca arms the child automatically" is an assumption, never a verified fact.
  Verify with `python scripts/stop_coverage.py check` and re-place any shortfall.
- Run the coverage guard in `market-open` (STEP 5b, after fills), `midday`
  (STEP 3c, on survivors), and `daily-summary` (STEP 3b-cov, before close).
- NEVER write a stop as "active" in TRADE-LOG until `stop_coverage` confirms a
  live order. A logged-but-absent stop is the most dangerous record error.
- A naked position has no stop to "move down", so re-placing the base ATR trail
  is always an improvement — the "never move a stop down" rule does not block it.

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
- **Target derived from a CITED level** (analyst PT / 52w-high / measured move), and **R:R ≥ 2.0** computed from the real ATR stop (NOT a placeholder +20% target)? If < 2:1 → demote, no full-size entry (B3, hard floor in `tests/buy_gate.py`).
- Per-trade risk ≤ 2.0% of equity after sizing (B5)?
- Not chasing a previously-refused level (B7)?
- Correlation with existing positions < 0.70? (and if it shares a *primary catalyst* with an existing position, is the concentration a conscious, acknowledged choice? — B6 soft advisory)
- Earnings not in next 5 trading days (unless catalyst IS earnings)?
- Symbol in TRADING_UNIVERSE?

## Buy-side Gate (ALL must pass before placing a buy)

Reference implementation: `tests/buy_gate.py`. All checks run at the same time;
the gate reports every failure, not just the first.

System-level kill switches (override everything):
- `memory/LOCK` is NOT present
- Daily-DD response is NOT `freeze_entries_48h`
- Weekly-DD response is NOT `freeze_until_monday`
- **Pre-macro-event deployment cap (Phase E)**: when a known binary macro
  event releases within the next **2 trading days** (FOMC, CPI, PPI, Core
  PCE, NFP), cap total cost-basis deployment at 40% of equity (2× $20k
  for standard sizing). Resume the regime-driven 50/75/85% deployment
  only AFTER the release prints. Detection:
  `python scripts/trading_calendar.py pre-macro-event` returns JSON with
  `cap_active`, `within_24h`, and `event_name`. Surfaced by
  `risk_gates check` as the `pre_macro_event` field. System-level (like
  LOCK), not Claude-discretion. Promoted from the 2026-05-25 pre-market's
  ad-hoc 40% cap before Wed Core PCE — kept the bot from over-extending
  into a binary release.

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
- **R:R floor (B3, audit 2026-06-03)**: R:R at entry ≥ 2.0, computed from the
  cited target and the real ATR stop (`MIN_RR_AT_ENTRY` in `tests/buy_gate.py`).
  Backtest A4 (REMEDIATION-FINDINGS.md): a hard 2:1 floor improved return AND
  drawdown across 2024, 2025, combined, and both stress runs — the single most
  robust improvement found.
- **No gate-creep (B7, audit 2026-06-03)**: do NOT enter above a level refused as
  too-high in the last 5 trading days unless the stock pulled back to plan
  (current ask ≤ plan). Enforced as a demote-to-watchlist in pre-market's
  gate-history audit. Backtest A1: chasing the open returned a quarter of the
  edge of waiting for a pullback.

**Concentration — what is NOT a gate (B6, audit 2026-06-03):** a hard per-sector
**dollar** cap was tested (A2) and **rejected** — at 20% positions it just forces
1-per-sector, which cost ~15pp in the 2024 trend year while only helping 2025
(fails the ≥2-window bar). The sector COUNT cap (≤2) + the 0.70 correlation gate
stay; shared-catalyst concentration (e.g. MU+AMD both on AI-capex, price-corr
0.44 but thematic-corr ~1) is handled as a **soft pre-market advisory** requiring
explicit acknowledgment, NOT a hard gate.

## Research integrity (B2 — audit 2026-06-03)

Decisions are only as good as the data behind them. Two hard rules:

1. **Citation honesty.** A citation must name the source that ACTUALLY returned
   the record (it appears in `research.py gather` output). Facts that came only
   from Gemini grounded search are tagged `[Gemini grounded — unverified]`, never
   `[SEC ...]` / `[<co> IR]` / `[<bank> note]`. A source that returned 0 records
   or was egress-blocked may NOT be cited. (2026-05-27→06-02: every entry showed
   NewsAPI/Finnhub/EDGAR/Reddit = 0 yet cited them as primary sources.)
2. **Contradiction reconciliation.** Before a number changes conviction, compare
   it to the bot's prior record (`research.py latest-on SYM 30`). A metric that
   differs >25% (or flips sign) from the last logged value MUST be resolved with
   one targeted query before use — never silently pick the convenient figure.
   (2026-05-25→27: LLY P/E 26.3x↔56.5x; insider selling $15M↔$577M; Core PCE
   3.2%-benign↔3.3%-hot — the unverified bigger insider figure was used to wave
   away a bear signal.) Log the resolution on a `**Data check:**` line.

## Sell-side Rules
- Close ≤ initial_stop (R ≤ −1) → close immediately at market (Phase C: was a flat
  −7% rule; widened to respect ATR-sized stops so a high-vol position takes its
  full planned risk instead of being cut short)
- Thesis broken (catalyst invalidated, sector rolling, adverse news) → close even if not at −7%
- Up ≥ +20% → tighten trailing stop to 5% (or 1.25 × ATR width, whichever is wider)
- Up ≥ +15% → tighten trailing stop to 7% (or 1.75 × ATR width, whichever is wider)
- **Partial exit (Phase H1)**: weight > 30% of equity AND unrealized > +20% → trim
  residual to 22% weight. See "Partial exits" subsection below for mechanics.
- Position flat (−3% to +3%) for 10 trading days → close (time stop, Phase A5)
- Sector has 2 consecutive failed trades → exit all positions in that sector
- Market regime = Defensive (Phase B) → close winners, hold stops, no new entries

## Partial exits (Phase H1)

A winner can grow past the 20% entry cap purely from price appreciation. Left
alone, a single thesis-break event then costs disproportionately more than
the position would risk under the entry-time sizing rule. The partial-exit
rule keeps realized concentration bounded without forcing a full exit on a
working thesis.

**Trigger** (both must hold):
- `market_value / equity > 0.30` — weight 10pp above the 20% entry cap.
  Loosened from the original 0.25 trigger so the rule only fires on truly
  extreme concentration, not on every winner that crosses the entry cap by
  5pp. Trades a smaller concentration buffer for less drag on runners.
- `unrealized_pnl_pct > +20%` — trim only winners that have meaningfully
  paid off; never trim a position that drifted to the cap via account
  drawdown, and never cut a winner that has barely cleared the entry-time
  R-multiple ceiling.

**Action**: sell `shares_to_sell = ceil((market_value − 0.22 × equity) / current_price)`
so the residual weight lands ≤ 22% (parked just over the entry cap, leaving
room to re-run without re-tripping the trim trigger on the next tick). Order
shape: `type=market`, `time_in_force=day`.

**Stop handling**: do NOT touch the trailing stop on the residual shares. The
original GTC trailing stop covers `shares_remaining`; verify via
`bash scripts/alpaca.sh orders` that the stop's `qty` field matches the
remaining position. If it doesn't (broker didn't auto-adjust the OTO child),
cancel + re-place at the same `trail_percent` for the new qty. The
`initial_stop` value on the original OPEN line is NEVER edited — R-multiple
math on the eventual full close must reference the entry-time risk level.

**TRADE-LOG line format**: append a non-CLOSED `- TRIM` line. The original
OPEN line stays untouched. On eventual full close, the CLOSED line's `pnl`
field reflects only the FINAL exit's P&L; the trimmed P&L lives on the TRIM
line. (Trade aggregators that sum P&L must read both prefixes.)

```
- TRIM YYYY-MM-DD: SYM exit=PRICE shares_sold=N remaining_shares=M pnl_realized=$X.XX reason="trim_to_22pct"
```

**Where executed**: **auto-fired by `midday` and `daily-summary`** — both
routines scan all open positions for the trigger and fire a market sell + log
+ WhatsApp without user confirmation. The `/trim` slash command remains
available as an ad-hoc manual override (same mechanics; useful for an
intraday runner that crosses the trigger between scheduled routine runs).

The original strategy required N≥20 observed manual trims before promotion
to automation — that gate was deliberately overridden 2026-06-03 on user
direction. Track every auto-trim outcome in the weekly review's "What
worked / what didn't" section: was the trimmed position's residual cut by
the trail before recovering (rule was net-positive), or did the position
keep running and the trim left money on the table (rule was net-negative)?
After ~20 auto-trims, revisit the trigger thresholds against the data.

## Position sizing (Phase D4)

Until N=30 closed trades: flat 20% max per position (current behavior).

From N=30 onward: **Half-Kelly** sizing kicks in automatically. The switchover
is data-driven — when `python scripts/trade_log.py count` reaches 30, every
new entry consults `python scripts/sizing.py recommend <regime> <equity>`.

**Per-trade risk cap (B5 — audit 2026-06-03).** On top of the dollar size above,
final share count = `min(size_dollars / entry, RISK_CAP_PCT%·equity / (entry −
stop))` via `python scripts/sizing.py shares <size_dollars> <entry> <stop>
<equity>`. `RISK_CAP_PCT = 2.0`. This shrinks the position when the ATR stop is
wide so per-trade $ risk is bounded — flat-20% had risked 2.9% on MU's 15% stop
vs 1.5% on CAT's 8% stop at the same dollar size. Backtest A3
(REMEDIATION-FINDINGS.md): 2.0% improved return AND drawdown in 2024, 2025,
combined, and both stress runs (2025-stress -8.7%→+3.7%). Complementary to the
R:R floor (B3): the floor filters thin-reward entries, the cap right-sizes the
wide-stop ones that pass.

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

## Entry order types (Phase G — closes the missed-entry gap)

Before Phase G, every entry was a market order at 09:35 ET. If the planned
zone was missed at that one quote, the candidate was dropped — and the next
day's screener could re-rank it out. Real evidence (2026-05-27 NVDA / AMD /
LLY): correct theses, wrong timing, no carry-forward.

Phase G moves the price-timing decision from Claude (one-shot at the bell)
to the broker (intraday limit / stop conditional fills), and adds a
3-trading-day watchlist for residual misses.

### Setup-type → order-type mapping

Each pre-market candidate gets a **Setup type** label in its RESEARCH-LOG
block. Market-open uses the label to choose the order shape:

| Setup     | Thesis shape                              | Market-open order                         |
|-----------|-------------------------------------------|-------------------------------------------|
| PULLBACK  | "Price needs to come back to my level"    | Buy-limit at planned entry, day TIF       |
| BREAKOUT  | "Confirmation above resistance"           | Buy-stop at resistance +0.1–0.2%, day TIF |
| MOMENTUM  | "Open with strength, ride it" (binary day)| Market order at open, day TIF             |

All three are placed with Alpaca's `order_class=oto` and a child trailing
stop using the ATR-based `stop_pct` (Phase A2). The child arms automatically
on entry fill — no unhedged window between fill and stop placement.

### Gap guard (Phase G3)

Market-open STEP 3 compares the current ask to the planned entry from
RESEARCH-LOG:

- `current > planned × 1.03` → SKIP entry. Log a `- SKIPPED ...` line, push
  the candidate to the watchlist so tomorrow's pre-market can re-evaluate at
  the original planned price.
- `current < planned × 0.97` → PROCEED but place the limit at the new lower
  ask and recompute stop_pct (the gap widens realized ATR%).

### PENDING line + EOD reconciliation (Phase G4)

Market-open writes a `- PENDING YYYY-MM-DD: SYM order_id=... type=... ...`
line for every order it places. PENDING orders do NOT count toward the
weekly trade cap or the open-position cap until they fill.

Daily-summary STEP 3b reconciles each PENDING against Alpaca's `orders-today`:

- Filled → write canonical `- OPEN ...` line referencing the same order_id
  (realized fill price, not the planned entry).
- Cancelled / expired → if thesis intact, add to the watchlist (Phase G2).
- Still open + buy-stop with day TIF → explicitly cancel so it doesn't leak
  into the next session.

The `initial_stop` on the OPEN line is the value derived from the **planned**
entry × stop_pct, NOT recomputed from the fill price. R-multiple math depends
on the original risk level being immutable.

### Watchlist (Phase G2)

`memory/WATCHLIST.md` — hard-capped at 6 entries (≤ open-position cap), each
with `days_remaining` (default 3 trading days). Pre-market STEP 4b consults
the watchlist and applies a small `ml_score` bonus (+0.5) to listed symbols
so they compete fairly with fresh screener picks. Daily-summary STEP 3c
prunes expired entries.

A watchlist entry is dropped early if the thesis breaks (sector flips to
Bear, earnings now in blackout, major adverse news). The standard pre-market
filters still apply on each re-evaluation — the bonus does not override hard
rules.

### Independent execution + carry-forward (B4 — audit 2026-06-03)

- **Independent execution.** Each candidate is evaluated and executed on its OWN
  merits. Do NOT make one entry conditional on another filling first unless the
  dependency is genuinely capital- or correlation-driven. (2026-05-27: LLY was
  gated "enter only after NVDA fills"; NVDA missed its gate by $2.25 so LLY
  auto-skipped, even though its ASCO/retatrutide thesis was independent of NVDA.)
- **Carry-forward intact theses.** Any candidate skipped at market-open for a
  *transient* reason (gap above plan, buy-stop not reached, daytrade buffer, a
  same-day correlation/sector clash) with its thesis still intact MUST be added
  to the watchlist — not silently dropped. (2026-05-27: NVDA missed $213 by
  $2.25 with the AI/COMPUTEX thesis intact, then vanished from the next day's
  screener with no carry-forward.) Broken-thesis skips (sector Bear, catalyst
  dead, R:R floor failed on merit) are logged as dropped, not carried.
