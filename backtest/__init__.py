"""Walk-forward backtest engine (Phase C).

Validates the deterministic layer of the strategy (exits, sizing, regime gauge,
risk gates) against historical data. Does NOT model Claude's catalyst research
— entries come from a top-N momentum proxy. Use this to compare exit variants
and stress-test the safety net, not to predict live returns.

Modules:
  data           — bar fetcher + parquet cache
  exit_engine    — exit strategies (FixedTrail, ATRTrail, ChandelierTrail)
  entry_simulator — weekly top-N rebalance proxy
  engine         — walk-forward orchestrator (positions + equity curve)
  benchmarks     — SPY buy-hold, SPY 200-SMA, equal-weight random
  reports        — Sharpe / max DD / win rate / markdown report writer
  stress         — synthetic crash injection (C4)
  cli            — `python -m backtest run --start ... --end ... --exit atr`
"""
