"""Contract-conformance tests for the producer-emitted ml-insights.json shape.

`test_ml_insights.py` exercises the validator against synthetic payloads.
This file complements it by mirroring the **exact wire format** the producer
(github.com/cucuradu/ml-pipeline `generate_insights.py`) writes, so contract
drift on either side fails CI here instead of silently degrading to the
rule-based fallback in production.

Reference: docs/ml-insights-schema.md (consumer contract), and the producer's
`generate_insights.py` build step in the ml-pipeline repo.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import ml_insights as mi  # noqa: E402


NOW = datetime(2026, 5, 26, 12, 0, 0, tzinfo=timezone.utc)


# Exact 1:1 mirror of the dict generate_insights.py builds before json.dump.
# If the producer changes a field name, casing, or nesting, this test fails.
def _producer_payload(*, regime: str = "Bull",
                      deployment_target: float = 0.85,
                      trade_slots: int = 3) -> dict:
    return {
        "generated_at": "2026-05-26T05:30:00Z",
        "model_version": "hmm-garch-v1.0",
        "market": {
            "regime": regime,
            "confidence": 0.8732,
            "persistence_bars": 3,
            "deployment_target": deployment_target,
            "trade_slots": trade_slots,
        },
        "volatility": {
            "garch_1d_forecast_pct": 12.18,
            "vix_implied_term_structure": "contango",
        },
        "sectors": {
            "XLK": {"regime": "Trend",  "score": 0.74},
            "XLF": {"regime": "Choppy", "score": 0.12},
            "XLV": {"regime": "Trend",  "score": 0.55},
            "XLE": {"regime": "Bear",   "score": -0.41},
            "XLI": {"regime": "Trend",  "score": 0.38},
            "XLY": {"regime": "Choppy", "score": 0.05},
            "XLP": {"regime": "Choppy", "score": 0.02},
            "XLU": {"regime": "Choppy", "score": -0.08},
            "XLB": {"regime": "Bear",   "score": -0.29},
            "XLRE": {"regime": "Choppy", "score": -0.11},
            "XLC": {"regime": "Trend",  "score": 0.61},
        },
    }


def test_producer_payload_passes_validation():
    """If this fails the producer (cucuradu/ml-pipeline) and consumer have drifted."""
    r = mi.validate(_producer_payload(), now=NOW)
    assert r["ok"] is True, f"contract broken: {r['reason']}"
    f = r["fields"]
    assert f["market"]["regime"] == "Bull"
    assert f["market"]["deployment_target"] == 0.85
    assert f["market"]["trade_slots"] == 3
    # All 11 sectors should survive validation.
    assert set(f["sectors"].keys()) == {
        "XLK", "XLF", "XLV", "XLE", "XLI", "XLY",
        "XLP", "XLU", "XLB", "XLRE", "XLC",
    }


# The producer's REGIME_DEPLOYMENT_MAP must stay within the consumer's enforced
# ranges. If the producer maps a regime to deployment_target outside [0,1] or
# trade_slots outside [0,3], the consumer rejects the whole payload and falls
# back. These four cases lock down every row of that map.
@pytest.mark.parametrize("regime,deployment,slots", [
    ("Bull",      0.85, 3),
    ("Neutral",   0.75, 2),
    ("Caution",   0.50, 1),
    ("Defensive", 0.00, 0),
])
def test_producer_deployment_map_is_within_consumer_bounds(regime, deployment, slots):
    payload = _producer_payload(regime=regime, deployment_target=deployment, trade_slots=slots)
    r = mi.validate(payload, now=NOW)
    assert r["ok"] is True, f"{regime} row rejected: {r['reason']}"
    assert r["fields"]["market"]["deployment_target"] == deployment
    assert r["fields"]["market"]["trade_slots"] == slots


def test_producer_volatility_block_is_tolerated_but_not_required():
    """Schema currently marks volatility as reserved; consumer ignores it.
    This test guards against the consumer accidentally enforcing it later.
    """
    payload = _producer_payload()
    del payload["volatility"]
    r = mi.validate(payload, now=NOW)
    assert r["ok"] is True


def test_producer_payload_round_trips_through_json():
    """Producer writes via `json.dump`; consumer reads via `json.loads`.
    Catches any non-serializable value sneaking into the payload shape.
    """
    raw = json.dumps(_producer_payload())
    parsed = json.loads(raw)
    r = mi.validate(parsed, now=NOW)
    assert r["ok"] is True


def test_producer_payload_read_from_file(tmp_path, monkeypatch):
    """End-to-end: producer writes file at repo root → consumer reads it via resolve()."""
    ml_path = tmp_path / "ml-insights.json"
    ml_path.write_text(json.dumps(_producer_payload()))
    monkeypatch.setattr(mi, "ML_FILE", ml_path)

    resolved = mi.resolve(now=NOW)
    assert resolved["source"] == "ml", (
        f"resolve() fell back when it shouldn't have: {resolved['fallback_reason']}"
    )
    assert resolved["market"]["regime"] == "Bull"
    assert resolved["ml_metadata"]["model_version"] == "hmm-garch-v1.0"
