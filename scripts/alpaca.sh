#!/usr/bin/env bash
# Alpaca API wrapper. All trading API calls go through here.
# Usage: bash scripts/alpaca.sh <subcommand> [args...]
#
# FAILSAFE: order/cancel/close operations are REFUSED if ALPACA_ENDPOINT does
# not contain "paper-api" UNLESS ALLOW_LIVE_TRADING=1 is set. This is the
# code-level guard against accidentally trading live during the paper phase.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"

if [[ -f "$ENV_FILE" ]]; then
  # Load .env WITHOUT overriding vars already set in the caller's environment.
  # Critical for the failsafe: tests/automation that inject ALPACA_ENDPOINT
  # (e.g., to simulate a live endpoint) must not be silently reverted by .env.
  while IFS='=' read -r _env_key _env_val || [[ -n "$_env_key" ]]; do
    # Skip blanks and comments
    [[ -z "$_env_key" || "$_env_key" =~ ^[[:space:]]*# ]] && continue
    # Strip optional "export " prefix and surrounding whitespace from the key
    _env_key="${_env_key#export }"
    _env_key="${_env_key// /}"
    [[ -z "$_env_key" ]] && continue
    # Honor caller's environment: do not override pre-set vars.
    [[ -n "${!_env_key+x}" ]] && continue
    # Strip optional surrounding quotes from the value
    _env_val="${_env_val%\"}"; _env_val="${_env_val#\"}"
    _env_val="${_env_val%\'}"; _env_val="${_env_val#\'}"
    export "$_env_key=$_env_val"
  done < "$ENV_FILE"
  unset _env_key _env_val
fi

: "${ALPACA_API_KEY:?ALPACA_API_KEY not set in environment}"
: "${ALPACA_SECRET_KEY:?ALPACA_SECRET_KEY not set in environment}"

API="${ALPACA_ENDPOINT:-https://paper-api.alpaca.markets/v2}"
DATA="${ALPACA_DATA_ENDPOINT:-https://data.alpaca.markets/v2}"

H_KEY="APCA-API-KEY-ID: $ALPACA_API_KEY"
H_SEC="APCA-API-SECRET-KEY: $ALPACA_SECRET_KEY"

cmd="${1:-}"
shift || true

# Live-endpoint failsafe — applies to mutating operations only.
case "$cmd" in
  order|cancel|cancel-all|close|close-all)
    if [[ "$API" != *"paper-api"* ]] && [[ "${ALLOW_LIVE_TRADING:-0}" != "1" ]]; then
      echo "REFUSED: ALPACA_ENDPOINT does not look like paper, and ALLOW_LIVE_TRADING is not set to 1." >&2
      echo "Current endpoint: $API" >&2
      echo "Subcommand attempted: $cmd" >&2
      exit 42
    fi
    ;;
esac

case "$cmd" in
  account)
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/account"
    ;;
  positions)
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/positions"
    ;;
  position)
    sym="${1:?usage: position SYM}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/positions/$sym"
    ;;
  quote)
    sym="${1:?usage: quote SYM}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$DATA/stocks/$sym/quotes/latest"
    ;;
  orders)
    status="${1:-open}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" "$API/orders?status=$status"
    ;;
  order)
    body="${1:?usage: order '<json>'}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" -H "Content-Type: application/json" \
      -X POST -d "$body" "$API/orders"
    ;;
  cancel)
    oid="${1:?usage: cancel ORDER_ID}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" -X DELETE "$API/orders/$oid"
    ;;
  cancel-all)
    curl -fsS -H "$H_KEY" -H "$H_SEC" -X DELETE "$API/orders"
    ;;
  close)
    sym="${1:?usage: close SYM}"
    curl -fsS -H "$H_KEY" -H "$H_SEC" -X DELETE "$API/positions/$sym"
    ;;
  close-all)
    curl -fsS -H "$H_KEY" -H "$H_SEC" -X DELETE "$API/positions"
    ;;
  *)
    echo "Usage: bash scripts/alpaca.sh <account|positions|position|quote|orders|order|cancel|cancel-all|close|close-all> [args]" >&2
    exit 1
    ;;
esac
echo
