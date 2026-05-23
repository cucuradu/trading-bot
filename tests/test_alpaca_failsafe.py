"""Verifies the live-endpoint failsafe in scripts/alpaca.sh.

This is the most important test in the suite. If this test breaks, the bot
could accidentally place real-money orders during the paper phase.
"""
import os
import subprocess
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
ALPACA_SH = REPO / "scripts" / "alpaca.sh"


def run_alpaca(args: list[str], env_overrides: dict[str, str]) -> subprocess.CompletedProcess:
    env = os.environ.copy()
    # Clear anything from the user's shell that might leak in
    for k in ("ALPACA_ENDPOINT", "ALLOW_LIVE_TRADING"):
        env.pop(k, None)
    env.update(env_overrides)
    return subprocess.run(
        ["bash", str(ALPACA_SH), *args],
        env=env,
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(REPO),
    )


BASE_ENV = {
    "ALPACA_API_KEY": "fake-key-for-test",
    "ALPACA_SECRET_KEY": "fake-secret-for-test",
}


ORDER_JSON = '{"symbol":"SPY","qty":"1","side":"buy","type":"market","time_in_force":"day"}'


def test_live_endpoint_order_is_refused():
    env = {**BASE_ENV, "ALPACA_ENDPOINT": "https://api.alpaca.markets/v2"}
    result = run_alpaca(["order", ORDER_JSON], env)
    assert result.returncode == 42, f"expected exit 42, got {result.returncode}\nstderr: {result.stderr}"
    assert "REFUSED" in result.stderr
    assert "api.alpaca.markets" in result.stderr


def test_live_endpoint_cancel_all_is_refused():
    env = {**BASE_ENV, "ALPACA_ENDPOINT": "https://api.alpaca.markets/v2"}
    result = run_alpaca(["cancel-all"], env)
    assert result.returncode == 42
    assert "REFUSED" in result.stderr


def test_live_endpoint_close_all_is_refused():
    env = {**BASE_ENV, "ALPACA_ENDPOINT": "https://api.alpaca.markets/v2"}
    result = run_alpaca(["close-all"], env)
    assert result.returncode == 42


def test_live_endpoint_with_explicit_allow_passes_failsafe():
    # We don't want a real HTTP call, but we DO want to verify the failsafe doesn't trip.
    # With fake credentials, curl will fail (auth or network), but the failsafe check
    # itself must allow execution to proceed past the case statement.
    env = {**BASE_ENV,
           "ALPACA_ENDPOINT": "https://api.alpaca.markets/v2",
           "ALLOW_LIVE_TRADING": "1"}
    result = run_alpaca(["order", ORDER_JSON], env)
    assert result.returncode != 42, (
        f"failsafe should not trip when ALLOW_LIVE_TRADING=1; got exit {result.returncode}\n"
        f"stderr: {result.stderr}"
    )
    # We expect a non-zero exit (curl auth failure) but NOT the failsafe code.
    assert "REFUSED" not in result.stderr


def test_paper_endpoint_passes_failsafe():
    env = {**BASE_ENV, "ALPACA_ENDPOINT": "https://paper-api.alpaca.markets/v2"}
    result = run_alpaca(["order", ORDER_JSON], env)
    assert result.returncode != 42, (
        f"failsafe should not trip on paper endpoint; got exit {result.returncode}\n"
        f"stderr: {result.stderr}"
    )
    assert "REFUSED" not in result.stderr


def test_paper_endpoint_default_when_unset():
    # The script defaults ALPACA_ENDPOINT to paper. Unset env var → paper → failsafe passes.
    env = {**BASE_ENV}  # no ALPACA_ENDPOINT
    result = run_alpaca(["order", ORDER_JSON], env)
    assert "REFUSED" not in result.stderr


def test_read_only_ops_on_live_endpoint_are_not_refused():
    # account/positions/quote/orders bypass the failsafe — they're safe by definition.
    env = {**BASE_ENV, "ALPACA_ENDPOINT": "https://api.alpaca.markets/v2"}
    for cmd in ("account", "positions", "orders"):
        result = run_alpaca([cmd], env)
        assert "REFUSED" not in result.stderr, f"{cmd} should not trip failsafe"


def test_allow_live_trading_zero_is_treated_as_off():
    env = {**BASE_ENV,
           "ALPACA_ENDPOINT": "https://api.alpaca.markets/v2",
           "ALLOW_LIVE_TRADING": "0"}
    result = run_alpaca(["order", ORDER_JSON], env)
    assert result.returncode == 42, "ALLOW_LIVE_TRADING=0 should NOT enable live trading"
    assert "REFUSED" in result.stderr
