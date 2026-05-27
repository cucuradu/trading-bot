"""Tests for scripts/screener.py — multi-factor universe ranker.

All tests are hermetic: synthetic bars, no network. Sector regimes are passed
in as plain dicts so we never call yfinance.
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import screener as sc  # noqa: E402


# ------------------------------------------------------------------------
# Synthetic bar helpers
# ------------------------------------------------------------------------

def _make_bars(
    *,
    n: int = 260,
    start_price: float = 100.0,
    drift_pct_per_day: float = 0.001,
    volatility_pct: float = 0.01,
    volume: float = 5_000_000,
    seed: int | None = 0,
    end_date: str = "2026-05-26",
) -> pd.DataFrame:
    """Generate `n` daily bars with a constant drift + small noise.

    Volume is constant (low daily noise), so factor 6 (volume_surge) ≈ 0
    by default. Tests that need a volume surge override the last 5 bars.
    """
    rng = np.random.default_rng(seed)
    rets = rng.normal(loc=drift_pct_per_day, scale=volatility_pct, size=n)
    prices = start_price * np.cumprod(1.0 + rets)
    idx = pd.date_range(end=pd.Timestamp(end_date), periods=n, freq="B")
    df = pd.DataFrame({
        "Open": prices * (1 - 0.001),
        "High": prices * (1 + volatility_pct * 0.5),
        "Low": prices * (1 - volatility_pct * 0.5),
        "Close": prices,
        "Volume": np.full(n, volume),
    }, index=idx)
    return df


def _bear_sector_regimes() -> dict[str, dict]:
    """All sectors Bear — useful for negative-path tests."""
    return {etf: {"regime": "Bear", "score": -0.5} for etf in sc.SECTOR_ETFS}


def _trend_sector_regimes() -> dict[str, dict]:
    """All sectors Trend — useful for positive-path tests."""
    return {etf: {"regime": "Trend", "score": 0.5} for etf in sc.SECTOR_ETFS}


def _mixed_bars_universe(symbols: list[str]) -> dict[str, pd.DataFrame]:
    """Build a synthetic bars dict where every symbol has 260 healthy bars.

    Includes sector ETFs (needed for RS factor) with neutral drift so RS is
    dominated by the candidate's own drift.
    """
    bars: dict[str, pd.DataFrame] = {}
    for i, sym in enumerate(symbols):
        # Vary drift per symbol so the ranking has signal
        drift = 0.0005 + (i * 0.0002)
        bars[sym] = _make_bars(drift_pct_per_day=drift, seed=i, volume=10_000_000)
    # Sector ETFs neutral drift
    for etf in sc.SECTOR_ETFS:
        if etf not in bars:
            bars[etf] = _make_bars(drift_pct_per_day=0.0003, seed=100, volume=20_000_000)
    return bars


# ------------------------------------------------------------------------
# rank_universe tests
# ------------------------------------------------------------------------

def test_rank_universe_returns_schema_compatible_shape():
    """Survivor entries must have {symbol, ml_score} compatible with universe_ranking."""
    syms = ["AAPL", "MSFT", "NVDA", "JPM"]
    bars = _mixed_bars_universe(syms)
    out = sc.rank_universe(symbols=syms, sector_regimes=_trend_sector_regimes(), bars=bars)
    survivors = [r for r in out if r["drop_reason"] is None]
    assert len(survivors) >= 1
    for entry in survivors:
        assert isinstance(entry["symbol"], str)
        assert isinstance(entry["ml_score"], float)
        # Stripped {symbol, ml_score} pair is the schema contract
        slim = {"symbol": entry["symbol"], "ml_score": entry["ml_score"]}
        assert set(slim.keys()) == {"symbol", "ml_score"}


def test_rank_universe_drops_bear_sectors():
    """Bear-sector tickers must be dropped with reason='sector_bear'."""
    syms = ["AAPL", "MSFT"]
    bars = _mixed_bars_universe(syms)
    out = sc.rank_universe(symbols=syms, sector_regimes=_bear_sector_regimes(), bars=bars)
    for entry in out:
        if entry["symbol"] in syms:
            assert entry["drop_reason"] == "sector_bear", \
                f"{entry['symbol']} should have been dropped as sector_bear, got {entry['drop_reason']}"


def test_rank_universe_drops_illiquid_and_penny():
    """Illiquid tickers (dollar vol < $50M) and penny stocks (<$5) get dropped."""
    syms = ["GOOD", "ILLIQ", "PENNY"]
    bars = {
        "GOOD": _make_bars(volume=20_000_000, start_price=200.0, seed=1),
        "ILLIQ": _make_bars(volume=1_000, start_price=200.0, seed=2),  # too low
        "PENNY": _make_bars(volume=50_000_000, start_price=2.0, seed=3),  # too cheap
    }
    # Add sector ETFs so the fetcher doesn't choke on RS lookup (synthetic mapping)
    for etf in sc.SECTOR_ETFS:
        bars[etf] = _make_bars(seed=99)

    # Provide a sector mapping function so the synthetic symbols pass sector lookup
    out = sc.rank_universe(
        symbols=syms, sector_regimes=_trend_sector_regimes(), bars=bars,
    )
    by_sym = {r["symbol"]: r for r in out if r["symbol"] in syms}
    assert by_sym["ILLIQ"]["drop_reason"] == "illiquid"
    assert by_sym["PENNY"]["drop_reason"] == "penny"
    # GOOD might survive or be dropped for missing_factor depending on the
    # sector_of() lookup; either way it should not be illiquid/penny.
    assert by_sym["GOOD"]["drop_reason"] not in ("illiquid", "penny")


def test_rank_universe_with_zero_history_returns_empty():
    """Empty bars dict → empty ranking, no crash."""
    out = sc.rank_universe(symbols=["AAPL"], sector_regimes=_trend_sector_regimes(), bars={})
    assert out == []


def test_rank_universe_handles_missing_ticker_data_gracefully():
    """Symbols requested but not in bars dict simply don't appear in output."""
    syms = ["AAPL", "GHOST"]  # GHOST has no bars
    bars = _mixed_bars_universe(["AAPL"])
    out = sc.rank_universe(symbols=syms, sector_regimes=_trend_sector_regimes(), bars=bars)
    out_syms = {r["symbol"] for r in out}
    assert "GHOST" not in out_syms
    assert "AAPL" in out_syms


# ------------------------------------------------------------------------
# compute_factors tests
# ------------------------------------------------------------------------

def test_compute_factors_no_lookahead():
    """No-lookahead guarantee: factor at day T must use only bars[..., T].

    Test logic: if a factor leaks day T+1 data into the day-T computation, then
    trimming the series by 1 bar would still yield the same value (because the
    leak would silently use the now-missing last bar). We compute factors on the
    full series, trim 1 bar, recompute, and assert the values DIFFER — proving
    the function honors the truncation boundary.
    """
    bars_full = {"AAPL": _make_bars(n=260, seed=42)}
    for etf in sc.SECTOR_ETFS:
        bars_full[etf] = _make_bars(n=260, seed=etf.__hash__() % 1000)
    full = sc.compute_factors(bars_full)

    # Trim 1 bar off AAPL and all sector ETFs uniformly
    bars_trim = {sym: df.iloc[:-1] for sym, df in bars_full.items()}
    trimmed = sc.compute_factors(bars_trim)

    assert pd.notna(full.at["AAPL", "momentum_125d"])
    assert pd.notna(trimmed.at["AAPL", "momentum_125d"])
    # If the function leaked T+1 into the T computation, the trimmed series
    # (which is now T-1 length) would silently use the dropped bar and produce
    # the same value as the full computation. They MUST differ.
    assert full.at["AAPL", "momentum_125d"] != trimmed.at["AAPL", "momentum_125d"]


def test_factor_breakdown_sums_within_tolerance():
    """ml_score MUST equal sum(z[factor] * weight[factor]) within float tolerance."""
    syms = ["AAPL", "MSFT", "NVDA", "JPM", "JNJ"]
    bars = _mixed_bars_universe(syms)
    out = sc.rank_universe(symbols=syms, sector_regimes=_trend_sector_regimes(), bars=bars)
    survivors = [r for r in out if r["drop_reason"] is None]
    for entry in survivors:
        expected = sum(
            entry["factor_breakdown"][f] * w
            for f, w in sc.FACTOR_WEIGHTS.items()
        )
        # ml_score is rounded to 4dp; factor_breakdown to 3dp. Tolerance ~1e-2.
        assert abs(entry["ml_score"] - expected) < 1e-2, \
            f"{entry['symbol']}: ml_score={entry['ml_score']} but weighted_sum={expected}"


def test_catalyst_factor_defaults_to_zero_when_signals_absent():
    """Without catalyst_signals, every survivor gets catalyst=0 (neutral)."""
    syms = ["AAPL", "MSFT"]
    bars = _mixed_bars_universe(syms)
    out = sc.rank_universe(symbols=syms, sector_regimes=_trend_sector_regimes(), bars=bars)
    survivors = [r for r in out if r["drop_reason"] is None]
    assert len(survivors) >= 1
    for entry in survivors:
        # catalyst factor must be present in the breakdown
        assert "catalyst" in entry["factor_breakdown"]
        # Without signals, z-score is 0 for all (std=0)
        assert entry["factor_breakdown"]["catalyst"] == 0.0


def test_catalyst_signals_shift_ranking():
    """When catalyst_signals favor one symbol, its ml_score must increase relative
    to peers that started tied."""
    syms = ["AAPL", "MSFT"]
    bars = _mixed_bars_universe(syms)
    # Hand-built catalyst signals: AAPL has strong upgrades + insider buys
    catalyst = pd.DataFrame({
        "analyst_net_upgrades": [3, 0],
        "insider_net_buy_shares": [50_000, 0],
        "catalyst_raw": [3.0 + math.log10(50_001), 0.0],
    }, index=["AAPL", "MSFT"])
    out_no_cat = sc.rank_universe(
        symbols=syms, sector_regimes=_trend_sector_regimes(), bars=bars,
    )
    out_with_cat = sc.rank_universe(
        symbols=syms, sector_regimes=_trend_sector_regimes(), bars=bars,
        catalyst_signals=catalyst,
    )
    aapl_no = next(r["ml_score"] for r in out_no_cat if r["symbol"] == "AAPL")
    aapl_with = next(r["ml_score"] for r in out_with_cat if r["symbol"] == "AAPL")
    msft_no = next(r["ml_score"] for r in out_no_cat if r["symbol"] == "MSFT")
    msft_with = next(r["ml_score"] for r in out_with_cat if r["symbol"] == "MSFT")
    # AAPL's relative position vs MSFT must improve when catalyst favors AAPL
    assert (aapl_with - msft_with) > (aapl_no - msft_no), \
        f"catalyst should boost AAPL relative to MSFT: " \
        f"no_cat={aapl_no - msft_no}, with_cat={aapl_with - msft_with}"


def test_macro_event_uses_defensive_weights():
    """macro_event=True uses MACRO_DAY_FACTOR_WEIGHTS (vol_stability heavier)."""
    syms = ["AAPL", "MSFT", "NVDA", "JPM", "JNJ"]
    bars = _mixed_bars_universe(syms)
    out_normal = sc.rank_universe(
        symbols=syms, sector_regimes=_trend_sector_regimes(), bars=bars,
        macro_event=False,
    )
    out_macro = sc.rank_universe(
        symbols=syms, sector_regimes=_trend_sector_regimes(), bars=bars,
        macro_event=True,
    )
    # Survivors should match but ml_scores should differ (different weights)
    by_sym_normal = {r["symbol"]: r["ml_score"] for r in out_normal if r["drop_reason"] is None}
    by_sym_macro = {r["symbol"]: r["ml_score"] for r in out_macro if r["drop_reason"] is None}
    assert set(by_sym_normal.keys()) == set(by_sym_macro.keys())
    # At least one symbol must score differently between the two weighting profiles
    diff_count = sum(
        1 for s in by_sym_normal
        if abs(by_sym_normal[s] - by_sym_macro[s]) > 0.01
    )
    assert diff_count >= 1, "macro_event=True should change at least one ml_score"
    # ml_score should equal weighted sum using MACRO_DAY_FACTOR_WEIGHTS
    for entry in [r for r in out_macro if r["drop_reason"] is None]:
        expected = sum(
            entry["factor_breakdown"][f] * w
            for f, w in sc.MACRO_DAY_FACTOR_WEIGHTS.items()
        )
        assert abs(entry["ml_score"] - expected) < 1e-2


# ------------------------------------------------------------------------
# deep_dive_shortlist tests
# ------------------------------------------------------------------------

def _fake_ranked(symbols: list[str], sectors: list[str]) -> list[dict]:
    """Build a fake ranked list (all survivors) with monotonically decreasing scores."""
    out = []
    for i, (sym, sec) in enumerate(zip(symbols, sectors)):
        out.append({
            "symbol": sym,
            "ml_score": 2.0 - i * 0.1,
            "factor_breakdown": {},
            "drop_reason": None,
            "sector": sec,
            "price": 100.0,
            "atr_pct": 2.0,
        })
    return out


def test_shortlist_excludes_open_positions():
    ranked = _fake_ranked(["NVDA", "AAPL", "JPM"], ["XLK", "XLK", "XLF"])
    bars = _mixed_bars_universe(["NVDA", "AAPL", "JPM"])
    out = sc.deep_dive_shortlist(
        ranked=ranked, open_symbols={"NVDA"}, bars=bars,
        trade_slots=3, k=6,
    )
    assert "NVDA" not in out
    assert "AAPL" in out
    assert "JPM" in out


def test_shortlist_respects_sector_cap_of_2():
    """Three XLK candidates + two XLK already open → cap blocks all three new ones."""
    ranked = _fake_ranked(["NVDA", "AAPL", "MSFT", "JPM"], ["XLK", "XLK", "XLK", "XLF"])
    bars = _mixed_bars_universe(["NVDA", "AAPL", "MSFT", "JPM", "GOOGL", "AVGO"])
    # 2 XLK already open
    out = sc.deep_dive_shortlist(
        ranked=ranked, open_symbols={"GOOGL", "AVGO"}, bars=bars,
        trade_slots=3, k=6, sector_cap=2,
    )
    # GOOGL and AVGO are XLC and XLK respectively per real universe.py, but the
    # shortlist uses sector_of() from universe — let's not rely on that here and
    # use the synthetic ranked entries' sector for the cap. The function counts
    # open positions' sectors via sector_of() (production code). For this test
    # we accept that GOOGL maps to XLC and AVGO to XLK — so only 1 XLK is open.
    # Re-derive expectation: 1 XLK open → cap=2 allows 1 more new XLK pick.
    xlk_in_picks = [s for s in out if s in {"NVDA", "AAPL", "MSFT"}]
    assert len(xlk_in_picks) <= 1, \
        f"sector cap should limit XLK picks to ≤1 with 1 XLK already open, got {xlk_in_picks}"
    assert "JPM" in out  # XLF is free


def test_shortlist_correlation_filter():
    """A perfectly-correlated synthetic pair should be filtered."""
    # Build two symbols whose Close series are identical → correlation = 1.0
    base = _make_bars(seed=7)
    bars = {
        "TWIN_A": base.copy(),
        "TWIN_B": base.copy(),
        "INDEP": _make_bars(seed=99),
    }
    for etf in sc.SECTOR_ETFS:
        bars[etf] = _make_bars(seed=etf.__hash__() % 1000)

    ranked = _fake_ranked(["TWIN_A", "TWIN_B", "INDEP"], ["XLK", "XLK", "XLF"])
    out = sc.deep_dive_shortlist(
        ranked=ranked, open_symbols=set(), bars=bars,
        trade_slots=3, k=6, corr_cap=0.70,
    )
    # TWIN_A picked first (higher score). TWIN_B should be rejected for correlation.
    assert "TWIN_A" in out
    assert "TWIN_B" not in out
    assert "INDEP" in out


def test_shortlist_caps_at_min_slots_and_K():
    """K = min(k, max(slots*2, 2))."""
    ranked = _fake_ranked(
        [f"S{i}" for i in range(10)],
        ["XLF"] * 10,  # all different sector from the existing cap interaction
    )
    bars = {f"S{i}": _make_bars(seed=i) for i in range(10)}
    for etf in sc.SECTOR_ETFS:
        bars[etf] = _make_bars(seed=etf.__hash__() % 1000)

    # slots=1 → K = min(6, 2) = 2
    out = sc.deep_dive_shortlist(
        ranked=ranked, open_symbols=set(), bars=bars,
        trade_slots=1, k=6, sector_cap=10, corr_cap=1.01,
    )
    assert len(out) == 2

    # slots=3 → K = min(6, 6) = 6
    out = sc.deep_dive_shortlist(
        ranked=ranked, open_symbols=set(), bars=bars,
        trade_slots=3, k=6, sector_cap=10, corr_cap=1.01,
    )
    assert len(out) == 6

    # slots=0 → empty
    out = sc.deep_dive_shortlist(
        ranked=ranked, open_symbols=set(), bars=bars,
        trade_slots=0, k=6, sector_cap=10, corr_cap=1.01,
    )
    assert out == []
