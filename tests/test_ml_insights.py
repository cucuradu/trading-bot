"""Tests for scripts/ml_insights.py — schema validation + fallback resolution.

The validate() function is pure; tests run without network. The resolve()
fallback path is exercised against a missing/stale/malformed file by
monkeypatching ML_FILE to a temp path.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import ml_insights as mi  # noqa: E402


NOW = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)


def _fresh_payload(**overrides) -> dict:
    """Baseline valid payload, 1 hour old by default."""
    base = {
        "generated_at": (NOW - timedelta(hours=1)).isoformat().replace("+00:00", "Z"),
        "model_version": "hmm-v1.2",
        "market": {
            "regime": "Bull",
            "confidence": 0.87,
            "persistence_bars": 5,
            "deployment_target": 0.85,
            "trade_slots": 3,
        },
        "sectors": {
            "XLK": {"regime": "Trend", "score": 0.74},
            "XLE": {"regime": "Bear", "score": -0.41},
        },
    }
    base.update(overrides)
    return base


# ---------------- validate() — happy path ----------------

def test_validate_accepts_fresh_well_formed_payload():
    r = mi.validate(_fresh_payload(), now=NOW)
    assert r["ok"] is True
    assert r["reason"] is None
    assert r["fields"]["market"]["regime"] == "Bull"
    assert r["fields"]["market"]["deployment_target"] == 0.85
    assert r["fields"]["market"]["trade_slots"] == 3
    assert r["fields"]["sectors"]["XLK"]["regime"] == "Trend"


def test_validate_accepts_iso_with_z_suffix():
    payload = _fresh_payload(generated_at="2026-05-26T11:00:00Z")
    r = mi.validate(payload, now=NOW)
    assert r["ok"] is True


def test_validate_accepts_iso_with_explicit_offset():
    payload = _fresh_payload(generated_at="2026-05-26T11:00:00+00:00")
    r = mi.validate(payload, now=NOW)
    assert r["ok"] is True


def test_validate_clamps_trade_slots_above_three():
    p = _fresh_payload()
    p["market"]["trade_slots"] = 99
    r = mi.validate(p, now=NOW)
    assert r["ok"] is True
    assert r["fields"]["market"]["trade_slots"] == 3


def test_validate_clamps_negative_trade_slots():
    p = _fresh_payload()
    p["market"]["trade_slots"] = -1
    r = mi.validate(p, now=NOW)
    assert r["ok"] is True
    assert r["fields"]["market"]["trade_slots"] == 0


def test_validate_tolerates_unknown_top_level_fields():
    p = _fresh_payload()
    p["future_field_added_by_local"] = {"x": 1}
    r = mi.validate(p, now=NOW)
    assert r["ok"] is True


def test_validate_skips_unknown_sector_regimes_silently():
    p = _fresh_payload()
    p["sectors"]["XYZ"] = {"regime": "Invalid", "score": 0.5}
    r = mi.validate(p, now=NOW)
    assert r["ok"] is True
    # XYZ omitted from the resolved sectors map.
    assert "XYZ" not in r["fields"]["sectors"]
    # Valid sectors preserved.
    assert "XLK" in r["fields"]["sectors"]


# ---------------- validate() — rejection paths ----------------

def test_validate_rejects_missing_generated_at():
    p = _fresh_payload()
    del p["generated_at"]
    r = mi.validate(p, now=NOW)
    assert r["ok"] is False
    assert "generated_at" in r["reason"]


def test_validate_rejects_unparseable_generated_at():
    p = _fresh_payload(generated_at="not a date")
    r = mi.validate(p, now=NOW)
    assert r["ok"] is False


def test_validate_rejects_stale_file_over_24h():
    p = _fresh_payload(generated_at=(NOW - timedelta(hours=25)).isoformat().replace("+00:00", "Z"))
    r = mi.validate(p, now=NOW)
    assert r["ok"] is False
    assert "stale" in r["reason"]


def test_validate_accepts_exactly_at_24h_boundary():
    p = _fresh_payload(generated_at=(NOW - timedelta(hours=23, minutes=59)).isoformat().replace("+00:00", "Z"))
    r = mi.validate(p, now=NOW)
    assert r["ok"] is True


def test_validate_rejects_far_future_generated_at():
    p = _fresh_payload(generated_at=(NOW + timedelta(hours=1)).isoformat().replace("+00:00", "Z"))
    r = mi.validate(p, now=NOW)
    assert r["ok"] is False
    assert "future" in r["reason"]


def test_validate_allows_small_clock_skew():
    # 30s in the future — clock drift between machines, not suspicious.
    p = _fresh_payload(generated_at=(NOW + timedelta(seconds=30)).isoformat().replace("+00:00", "Z"))
    r = mi.validate(p, now=NOW)
    assert r["ok"] is True


def test_validate_rejects_invalid_market_regime():
    p = _fresh_payload()
    p["market"]["regime"] = "Euphoria"  # not in enum
    r = mi.validate(p, now=NOW)
    assert r["ok"] is False
    assert "regime" in r["reason"]


def test_validate_rejects_deployment_target_above_1():
    p = _fresh_payload()
    p["market"]["deployment_target"] = 1.5
    r = mi.validate(p, now=NOW)
    assert r["ok"] is False


def test_validate_rejects_deployment_target_below_0():
    p = _fresh_payload()
    p["market"]["deployment_target"] = -0.1
    r = mi.validate(p, now=NOW)
    assert r["ok"] is False


def test_validate_rejects_missing_market_block():
    p = _fresh_payload()
    del p["market"]
    r = mi.validate(p, now=NOW)
    assert r["ok"] is False


def test_validate_rejects_non_dict_payload():
    r = mi.validate("not a dict", now=NOW)
    assert r["ok"] is False


def test_validate_rejects_missing_trade_slots():
    p = _fresh_payload()
    del p["market"]["trade_slots"]
    r = mi.validate(p, now=NOW)
    assert r["ok"] is False


# ---------------- read_and_validate() ----------------

def test_read_returns_not_found_when_file_missing(tmp_path):
    r = mi.read_and_validate(tmp_path / "nonexistent.json", now=NOW)
    assert r["ok"] is False
    assert "not found" in r["reason"]


def test_read_returns_malformed_on_bad_json(tmp_path):
    path = tmp_path / "ml.json"
    path.write_text("{ this is not valid json")
    r = mi.read_and_validate(path, now=NOW)
    assert r["ok"] is False
    assert "malformed JSON" in r["reason"]


def test_read_accepts_well_formed_file(tmp_path):
    path = tmp_path / "ml.json"
    path.write_text(json.dumps(_fresh_payload()))
    r = mi.read_and_validate(path, now=NOW)
    assert r["ok"] is True


# ---------------- resolve() — ML path ----------------

def test_resolve_uses_ml_when_file_is_fresh(tmp_path, monkeypatch):
    path = tmp_path / "ml-insights.json"
    path.write_text(json.dumps(_fresh_payload()))
    monkeypatch.setattr(mi, "ML_FILE", path)

    r = mi.resolve(now=NOW)
    assert r["source"] == "ml"
    assert r["fallback_reason"] is None
    assert r["market"]["regime"] == "Bull"
    assert r["ml_metadata"]["model_version"] == "hmm-v1.2"


def test_resolve_falls_back_on_stale_file(tmp_path, monkeypatch):
    path = tmp_path / "ml-insights.json"
    stale = _fresh_payload(generated_at=(NOW - timedelta(hours=30)).isoformat().replace("+00:00", "Z"))
    path.write_text(json.dumps(stale))
    monkeypatch.setattr(mi, "ML_FILE", path)
    # Stub out the rule-based fallback to avoid hitting yfinance in this test.
    import regime as rg
    monkeypatch.setattr(rg, "market_regime", lambda: {
        "regime": "Caution", "deployment_target": 0.5, "trade_slots": 1,
        "persistence_bars": 3, "stable": True,
    })
    monkeypatch.setattr(rg, "sector_regimes", lambda: {"sectors": {
        "XLK": {"symbol": "XLK", "regime": "Trend", "score": 0.5},
    }})

    # Disable the local screener so this test isolates the rule-based fallback.
    r = mi.resolve(now=NOW, enable_local_screener=False)
    assert r["source"] == "rule_fallback"
    assert "stale" in r["fallback_reason"]
    assert r["market"]["regime"] == "Caution"
    assert r["ml_metadata"] is None


def test_resolve_falls_back_on_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr(mi, "ML_FILE", tmp_path / "missing.json")
    import regime as rg
    monkeypatch.setattr(rg, "market_regime", lambda: {
        "regime": "Neutral", "deployment_target": 0.75, "trade_slots": 2,
        "persistence_bars": 3, "stable": True,
    })
    monkeypatch.setattr(rg, "sector_regimes", lambda: {"sectors": {}})

    # Disable the local screener so this test isolates the rule-based fallback.
    r = mi.resolve(now=NOW, enable_local_screener=False)
    assert r["source"] == "rule_fallback"
    assert "not found" in r["fallback_reason"]


# ---------------- resolve() — local screener fallback path (Phase F) ----------------

def _stub_rule_fallback(monkeypatch):
    """Common stub: rule-based market + empty sectors. Avoids yfinance."""
    import regime as rg
    monkeypatch.setattr(rg, "market_regime", lambda: {
        "regime": "Neutral", "deployment_target": 0.75, "trade_slots": 2,
        "persistence_bars": 3, "stable": True,
    })
    monkeypatch.setattr(rg, "sector_regimes", lambda: {"sectors": {
        "XLK": {"symbol": "XLK", "regime": "Trend", "score": 0.5},
    }})


def test_resolve_fallback_calls_local_screener_when_enabled(tmp_path, monkeypatch):
    """When ML is stale + screener enabled, universe_ranking comes from screener."""
    monkeypatch.setattr(mi, "ML_FILE", tmp_path / "missing.json")
    _stub_rule_fallback(monkeypatch)

    fake_ranking = [
        {"symbol": "AAPL", "ml_score": 1.5, "drop_reason": None,
         "factor_breakdown": {}, "sector": "XLK", "price": 200.0, "atr_pct": 2.0},
        {"symbol": "MSFT", "ml_score": 0.7, "drop_reason": None,
         "factor_breakdown": {}, "sector": "XLK", "price": 400.0, "atr_pct": 1.8},
        {"symbol": "XOM", "ml_score": None, "drop_reason": "sector_bear",
         "factor_breakdown": {}, "sector": "XLE", "price": 100.0, "atr_pct": 2.5},
    ]
    import screener
    monkeypatch.setattr(screener, "rank_universe", lambda **kw: fake_ranking)

    r = mi.resolve(now=NOW, enable_local_screener=True)
    assert r["source"] == "rule_fallback"
    # Only survivors (drop_reason=None) should pass through, stripped to {symbol, ml_score}
    assert r["universe_ranking"] == [
        {"symbol": "AAPL", "ml_score": 1.5},
        {"symbol": "MSFT", "ml_score": 0.7},
    ]
    assert r["ml_metadata"]["source_detail"] == "local_screener_v1"


def test_resolve_fallback_with_no_screener_flag_returns_empty_ranking(tmp_path, monkeypatch):
    """enable_local_screener=False preserves the original empty-ranking behavior."""
    monkeypatch.setattr(mi, "ML_FILE", tmp_path / "missing.json")
    _stub_rule_fallback(monkeypatch)

    r = mi.resolve(now=NOW, enable_local_screener=False)
    assert r["source"] == "rule_fallback"
    assert r["universe_ranking"] == []
    assert r["ml_metadata"] is None


def test_resolve_does_not_crash_when_screener_raises(tmp_path, monkeypatch):
    """Screener exceptions must NEVER bubble up — resolve() always returns a regime."""
    monkeypatch.setattr(mi, "ML_FILE", tmp_path / "missing.json")
    _stub_rule_fallback(monkeypatch)

    def _boom(**kw):
        raise RuntimeError("yfinance down")

    import screener
    monkeypatch.setattr(screener, "rank_universe", _boom)

    r = mi.resolve(now=NOW, enable_local_screener=True)
    assert r["source"] == "rule_fallback"
    assert r["universe_ranking"] == []  # screener failed, ranking stays empty
    assert r["market"]["regime"] == "Neutral"  # rule fallback still works


def test_resolve_falls_back_on_malformed_file(tmp_path, monkeypatch):
    path = tmp_path / "ml-insights.json"
    path.write_text("not json")
    monkeypatch.setattr(mi, "ML_FILE", path)
    import regime as rg
    monkeypatch.setattr(rg, "market_regime", lambda: {
        "regime": "Neutral", "deployment_target": 0.75, "trade_slots": 2,
        "persistence_bars": 3, "stable": True,
    })
    monkeypatch.setattr(rg, "sector_regimes", lambda: {"sectors": {}})

    r = mi.resolve(now=NOW)
    assert r["source"] == "rule_fallback"
    assert "malformed" in r["fallback_reason"]


def test_resolve_falls_back_on_bad_schema(tmp_path, monkeypatch):
    path = tmp_path / "ml-insights.json"
    bad = _fresh_payload()
    bad["market"]["regime"] = "Bogus"
    path.write_text(json.dumps(bad))
    monkeypatch.setattr(mi, "ML_FILE", path)
    import regime as rg
    monkeypatch.setattr(rg, "market_regime", lambda: {
        "regime": "Neutral", "deployment_target": 0.75, "trade_slots": 2,
        "persistence_bars": 3, "stable": True,
    })
    monkeypatch.setattr(rg, "sector_regimes", lambda: {"sectors": {}})

    r = mi.resolve(now=NOW)
    assert r["source"] == "rule_fallback"
    assert "regime" in r["fallback_reason"]


# ---------------- format_advisory_signals() / surface() — surface-only fields ----------------

def _rich_payload(**overrides) -> dict:
    """Fresh payload carrying the v2.0 fields the trading loop does NOT act on."""
    p = _fresh_payload(**overrides)
    p["market"]["systemic_fragility"] = 0.46
    p["volatility"] = {
        "garch_1d_forecast_pct": 17.1, "vix": 21.5, "vvix": 102.0,
        "vix_implied_term_structure": "contango",
    }
    p["macro"] = {
        "available": True, "macro_regime": "Risk-On",
        "hy_oas": 2.74, "nfci": -0.49, "curve_inverted": False,
    }
    p["crash_risk"] = {"score": 0.0, "elevated": False, "reasons": []}
    p["ranking_quality"] = {"oof_rank_ic": 0.015}
    p["universe_weights"] = {"MU": 0.43, "NOW": 0.57}
    return p


def test_format_advisory_includes_all_blocks():
    line = mi.format_advisory_signals(_rich_payload())
    assert "crash=0.00 calm" in line
    assert "fragility=0.46" in line
    assert "macro=Risk-On" in line and "NFCI -0.49" in line and "curve normal" in line
    assert "GARCH1d 17.1%" in line and "VIX 21.5" in line and "contango" in line
    assert "rankIC(oof)=0.015" in line
    assert "MU 0.43" in line and "NOW 0.57" in line


def test_format_advisory_flags_elevated_crash_with_reasons():
    p = _rich_payload()
    p["crash_risk"] = {"score": 0.8, "elevated": True, "reasons": ["vix_spike", "hy_widening"]}
    line = mi.format_advisory_signals(p)
    assert "crash=0.80 ELEVATED" in line
    assert "vix_spike" in line


def test_format_advisory_empty_when_no_blocks():
    # Baseline payload carries none of the advisory blocks.
    assert mi.format_advisory_signals(_fresh_payload()) == ""


def test_format_advisory_tolerates_partial_payload():
    p = _fresh_payload()
    p["crash_risk"] = {"score": 0.1, "elevated": False}
    line = mi.format_advisory_signals(p)
    assert line.startswith("**ML signals")
    assert "crash=0.10 calm" in line
    assert "macro=" not in line and "vol=" not in line


def test_format_advisory_skips_macro_when_unavailable():
    p = _rich_payload()
    p["macro"]["available"] = False
    assert "macro=" not in mi.format_advisory_signals(p)


def test_surface_returns_na_when_file_missing(tmp_path, monkeypatch):
    monkeypatch.setattr(mi, "_resolve_ml_file", lambda: tmp_path / "missing.json")
    out = mi.surface(now=NOW)
    assert out.startswith("**ML signals:** n/a")
    assert "not found" in out


def test_surface_returns_na_when_stale(tmp_path, monkeypatch):
    path = tmp_path / "ml-insights.json"
    path.write_text(json.dumps(_rich_payload(
        generated_at=(NOW - timedelta(hours=30)).isoformat().replace("+00:00", "Z"))))
    monkeypatch.setattr(mi, "_resolve_ml_file", lambda: path)
    out = mi.surface(now=NOW)
    assert "n/a" in out and "stale" in out


def test_surface_formats_when_fresh(tmp_path, monkeypatch):
    path = tmp_path / "ml-insights.json"
    path.write_text(json.dumps(_rich_payload()))
    monkeypatch.setattr(mi, "_resolve_ml_file", lambda: path)
    out = mi.surface(now=NOW)
    assert "rankIC(oof)=0.015" in out
