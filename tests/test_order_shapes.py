"""Validates the 3 canonical Alpaca order JSON shapes from the guide.

Alpaca quietly rejects orders where qty or trail_percent are numbers — they
must be strings. This test pins the contract.
"""
import json


def market_buy(symbol: str, qty: int) -> dict:
    return {
        "symbol": symbol,
        "qty": str(qty),
        "side": "buy",
        "type": "market",
        "time_in_force": "day",
    }


def trailing_stop(symbol: str, qty: int, trail_pct: int = 10) -> dict:
    return {
        "symbol": symbol,
        "qty": str(qty),
        "side": "sell",
        "type": "trailing_stop",
        "trail_percent": str(trail_pct),
        "time_in_force": "gtc",
    }


def fixed_stop(symbol: str, qty: int, stop_price: float) -> dict:
    return {
        "symbol": symbol,
        "qty": str(qty),
        "side": "sell",
        "type": "stop",
        "stop_price": f"{stop_price:.2f}",
        "time_in_force": "gtc",
    }


def test_market_buy_shape():
    o = market_buy("XOM", 12)
    assert isinstance(o["qty"], str), "qty must be a string per Alpaca contract"
    assert o == {
        "symbol": "XOM", "qty": "12", "side": "buy",
        "type": "market", "time_in_force": "day"
    }


def test_trailing_stop_shape():
    o = trailing_stop("XOM", 12, 10)
    assert isinstance(o["qty"], str)
    assert isinstance(o["trail_percent"], str), "trail_percent must be a string per Alpaca contract"
    assert o == {
        "symbol": "XOM", "qty": "12", "side": "sell",
        "type": "trailing_stop", "trail_percent": "10", "time_in_force": "gtc"
    }


def test_fixed_stop_shape():
    o = fixed_stop("XOM", 12, 140.0)
    assert isinstance(o["qty"], str)
    assert isinstance(o["stop_price"], str), "stop_price must be a string per Alpaca contract"
    assert o == {
        "symbol": "XOM", "qty": "12", "side": "sell",
        "type": "stop", "stop_price": "140.00", "time_in_force": "gtc"
    }


def test_all_shapes_serializable_to_json():
    for o in (market_buy("AAPL", 1), trailing_stop("AAPL", 1), fixed_stop("AAPL", 1, 100.0)):
        s = json.dumps(o)
        assert json.loads(s) == o


def test_tightened_trail_at_15pct_gain():
    o = trailing_stop("AAPL", 100, 7)
    assert o["trail_percent"] == "7"


def test_tightened_trail_at_20pct_gain():
    o = trailing_stop("AAPL", 100, 5)
    assert o["trail_percent"] == "5"
