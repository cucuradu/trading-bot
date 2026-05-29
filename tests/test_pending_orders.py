"""Tests for the PENDING-line parser added in Phase G1.

PENDING lines are written by market-open when it places a limit / stop /
market entry order. Daily-summary reconciles them against Alpaca's order
status and promotes filled ones to canonical OPEN lines.
"""
from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import trade_log as tl  # noqa: E402


PENDING_LIMIT = (
    "- PENDING 2026-05-29: NVDA order_id=abc123 type=limit entry=138.50 "
    "initial_stop=125.00 shares=140 regime_entry=Bull sector=XLK "
    'sizing=flat_20pct thesis="AI capex cycle, COMPUTEX June"'
)

PENDING_STOP = (
    "- PENDING 2026-05-29: AMD order_id=def456 type=stop entry=475.20 "
    "initial_stop=425.00 shares=42 regime_entry=Bull sector=XLK "
    'sizing=flat_20pct thesis="breakout above 52w base"'
)

PENDING_MARKET = (
    "- PENDING 2026-05-29: SPY order_id=ghi789 type=market entry=585.00 "
    "initial_stop=540.00 shares=34 regime_entry=Neutral sector=BROAD "
    'sizing=flat_20pct thesis="momentum into FOMC print"'
)


def test_parse_pending_limit_extracts_all_fields():
    po = tl.parse_pending_line(PENDING_LIMIT)
    assert po is not None
    assert po.symbol == "NVDA"
    assert po.placed_date == date(2026, 5, 29)
    assert po.order_id == "abc123"
    assert po.order_type == "limit"
    assert po.planned_entry == 138.50
    assert po.initial_stop == 125.00
    assert po.shares == 140
    assert po.regime_at_entry == "Bull"
    assert po.sector == "XLK"
    assert po.sizing_method == "flat_20pct"
    assert po.thesis == "AI capex cycle, COMPUTEX June"


def test_parse_pending_stop_recognizes_breakout_shape():
    po = tl.parse_pending_line(PENDING_STOP)
    assert po is not None
    assert po.order_type == "stop"
    assert po.planned_entry == 475.20


def test_parse_pending_market_recognizes_momentum_shape():
    po = tl.parse_pending_line(PENDING_MARKET)
    assert po is not None
    assert po.order_type == "market"
    assert po.sector == "BROAD"


def test_parse_pending_line_ignores_non_pending():
    closed = (
        "- CLOSED 2026-05-23: NVDA entry=180.50 exit=195.00 initial_stop=165.00 "
        'shares=110 pnl=$1595.00 r=0.97 reason="trailing stop hit"'
    )
    assert tl.parse_pending_line(closed) is None


def test_parse_pending_line_requires_order_id():
    missing = (
        "- PENDING 2026-05-29: NVDA type=limit entry=138.50 "
        "initial_stop=125.00 shares=140"
    )
    assert tl.parse_pending_line(missing) is None


def test_parse_pending_orders_filters_promoted_ids():
    """A PENDING followed by an OPEN/CLOSED referencing the same order_id
    is considered superseded — daily-summary's reconciliation already wrote
    the canonical OPEN line, so the PENDING is no longer 'open'."""
    body = "\n".join([
        PENDING_LIMIT,                                                     # NVDA / abc123
        PENDING_STOP,                                                      # AMD / def456 — still pending
        (
            "- OPEN 2026-05-29: NVDA order_id=abc123 entry=138.42 "
            "initial_stop=125.00 shares=140 regime_entry=Bull sector=XLK "
            'sizing=flat_20pct thesis="filled at limit"'
        ),
    ])
    pendings = tl.parse_pending_orders(body)
    syms = sorted(p.symbol for p in pendings)
    assert syms == ["AMD"]


def test_parse_pending_orders_filters_promoted_via_closed():
    """If the entry filled and then got stopped out same-day, the PENDING
    should also be excluded — the CLOSED line carries the order_id."""
    body = "\n".join([
        PENDING_LIMIT,
        (
            "- CLOSED 2026-05-29: NVDA order_id=abc123 entry=138.42 exit=124.80 "
            "initial_stop=125.00 shares=140 regime_entry=Bull sector=XLK "
            'pnl=-$1906.80 r=-1.01 reason="R<=-1 (gapped through stop)"'
        ),
    ])
    pendings = tl.parse_pending_orders(body)
    assert pendings == []


def test_parse_pending_orders_keeps_unmatched_open_lines_alone():
    """An OPEN line without an order_id field (legacy entries from before
    Phase G) must NOT cause a PENDING to be filtered out."""
    legacy_open = (
        "- OPEN 2026-05-28: MU entry=922.91 initial_stop=784.47 shares=21 "
        'regime_entry=Neutral sector=XLK sizing=flat_20pct thesis="HBM demand"'
    )
    body = "\n".join([PENDING_LIMIT, legacy_open])
    pendings = tl.parse_pending_orders(body)
    assert len(pendings) == 1
    assert pendings[0].symbol == "NVDA"


def test_load_pending_orders_returns_empty_on_missing_file(tmp_path):
    missing = tmp_path / "no-such.md"
    assert tl.load_pending_orders(missing) == []


def test_load_pending_orders_round_trip(tmp_path):
    """Write PENDING + OPEN to a file, verify only the unmatched PENDING comes back."""
    f = tmp_path / "TRADE-LOG.md"
    f.write_text("\n".join([PENDING_LIMIT, PENDING_STOP]))
    pendings = tl.load_pending_orders(f)
    assert sorted(p.symbol for p in pendings) == ["AMD", "NVDA"]


def test_pending_order_as_jsonable_serializes_date():
    po = tl.parse_pending_line(PENDING_LIMIT)
    j = po.as_jsonable()
    assert j["placed_date"] == "2026-05-29"
    assert j["symbol"] == "NVDA"
    assert j["order_type"] == "limit"
