"""Tests for the pre-open gap guard (Phase G3)."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import gap_guard as gg  # noqa: E402


def test_within_tolerance_proceeds():
    d = gg.evaluate(planned=138.50, current=139.20)  # +0.5%
    assert d.action == "proceed"


def test_gap_up_above_threshold_skips():
    d = gg.evaluate(planned=138.50, current=145.10)  # +4.77%
    assert d.action == "skip"
    assert "gap_above_plan" in d.reason


def test_gap_down_below_threshold_proceeds_lower():
    d = gg.evaluate(planned=138.50, current=130.50)  # -5.78%
    assert d.action == "proceed_lower"
    assert "gap_below_plan" in d.reason


def test_exactly_at_upper_bound_proceeds():
    """+3.00% is the boundary — strictly greater than triggers skip."""
    planned = 100.0
    d_at = gg.evaluate(planned=planned, current=planned * 1.03)
    assert d_at.action == "proceed"
    d_over = gg.evaluate(planned=planned, current=planned * 1.030001)
    assert d_over.action == "skip"


def test_exactly_at_lower_bound_proceeds():
    planned = 100.0
    d_at = gg.evaluate(planned=planned, current=planned * 0.97)
    assert d_at.action == "proceed"
    d_under = gg.evaluate(planned=planned, current=planned * 0.969999)
    assert d_under.action == "proceed_lower"


def test_custom_tolerance_widens_window():
    """With a 5% tolerance, the same 4% gap that would have skipped passes."""
    d = gg.evaluate(planned=138.50, current=143.50, tolerance=0.05)  # +3.6%
    assert d.action == "proceed"


def test_negative_planned_rejects():
    with pytest.raises(ValueError):
        gg.evaluate(planned=-1.0, current=100.0)


def test_zero_planned_rejects():
    with pytest.raises(ValueError):
        gg.evaluate(planned=0.0, current=100.0)


def test_negative_current_rejects():
    with pytest.raises(ValueError):
        gg.evaluate(planned=100.0, current=-1.0)


def test_invalid_tolerance_rejects():
    with pytest.raises(ValueError):
        gg.evaluate(planned=100.0, current=100.0, tolerance=0.0)
    with pytest.raises(ValueError):
        gg.evaluate(planned=100.0, current=100.0, tolerance=1.0)


def test_decision_serializes_to_dict():
    d = gg.evaluate(planned=100.0, current=110.0)  # +10%, skip
    j = d.as_dict()
    assert j["action"] == "skip"
    assert j["ratio"] == pytest.approx(1.10, rel=1e-4)
    assert "reason" in j
