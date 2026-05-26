#!/usr/bin/env bash
# Research wrapper. All market research goes through Gemini (free tier).
#
# Usage:
#   bash scripts/gemini.sh [FLAGS] "<query>"
#
# Flags:
#   --synth                 use the synthesis system prompt (no 3-5 bullets cap,
#                           chain-of-thought scaffold, maxOutputTokens=2048)
#   --smart | --model pro   route to gemini-2.5-pro (better reasoning)
#   --temperature N         override temperature (default 0.2; 0.1 recommended
#                           for synthesis, 0.4 for critique)
#   --no-cache              skip the response cache
#   --json                  set response_mime_type=application/json
#
# Exit codes:
#   0  success
#   1  usage error
#   3  GEMINI_API_KEY unset (caller can fall back to WebSearch)
#   4  Pro quota exhausted AND Flash fallback also failed
#   5  Flash daily budget pre-exhausted (cap at 18 calls/day; 2 in reserve)
#
# Cache: responses are saved to cache/gemini/<sha256-16>.json keyed by
# (model, synth-flag, json-flag, temperature, query). Subsequent identical
# calls return the cached body; --no-cache forces a refetch.
#
# Pro 429 handling: if --smart returns 429 RESOURCE_EXHAUSTED, automatically
# retry on Flash with --synth (CoT scaffold). If THAT also 429s, sleep with
# exponential backoff (capped 32s) and propagate.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
CACHE_DIR="$ROOT/cache/gemini"

# Load .env without clobbering pre-set env vars (mirrors scripts/alpaca.sh).
if [[ -f "$ENV_FILE" ]]; then
  while IFS='=' read -r _env_key _env_val || [[ -n "$_env_key" ]]; do
    [[ -z "$_env_key" || "$_env_key" =~ ^[[:space:]]*# ]] && continue
    _env_key="${_env_key#export }"
    _env_key="${_env_key// /}"
    [[ -n "${!_env_key+x}" ]] && continue
    export "$_env_key=$_env_val"
  done < "$ENV_FILE"
fi

# ---------------- flag parsing ----------------
USE_SYNTH=0
USE_SMART=0
USE_JSON=0
USE_CACHE=1
TEMPERATURE=""
query=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --synth)        USE_SYNTH=1; shift ;;
    --smart)        USE_SMART=1; shift ;;
    --model)        [[ "${2:-}" == "pro" ]] && USE_SMART=1; shift 2 ;;
    --temperature)  TEMPERATURE="$2"; shift 2 ;;
    --no-cache)     USE_CACHE=0; shift ;;
    --json)         USE_JSON=1; shift ;;
    --)             shift; query="${1:-}"; shift; break ;;
    -h|--help)
      sed -n '2,30p' "$0"; exit 0 ;;
    *)              query="$1"; shift ;;
  esac
done

if [[ -z "$query" ]]; then
  echo "usage: bash scripts/gemini.sh [--synth] [--smart] [--temperature N] [--no-cache] [--json] \"<query>\"" >&2
  exit 1
fi

if [[ -z "${GEMINI_API_KEY:-}" ]]; then
  echo "WARNING: GEMINI_API_KEY not set. Fall back to native WebSearch." >&2
  exit 3
fi

# ---------------- resolve model + prompt ----------------
DEFAULT_MODEL="${GEMINI_MODEL:-gemini-2.5-flash}"
SMART_MODEL="${GEMINI_SMART_MODEL:-gemini-2.5-pro}"

if [[ "$USE_SMART" -eq 1 ]]; then
  MODEL="$SMART_MODEL"
else
  MODEL="$DEFAULT_MODEL"
fi

if [[ "$USE_SYNTH" -eq 1 ]]; then
  SYSTEM_PROMPT='You are a precise financial research assistant. Use Google Search grounding for any current data (prices, news, dates). Cite every claim with a source URL and a publication date. Think step by step before answering: first enumerate the evidence, then state the bull case (each item cited), then the bear case (each item cited), then list disconfirming evidence and catalysts ahead. Only then write the final structured answer. Prefer specificity over breadth.'
  # Gemini 2.5 uses internal "thinking tokens" that count against this cap.
  # 8192 leaves ~5-6k for the visible answer after thinking overhead.
  MAX_TOKENS=8192
  DEFAULT_TEMP=0.1
else
  SYSTEM_PROMPT='You are a precise financial research assistant. Use Google Search grounding for any current data (prices, news, dates). Cite every claim with a source URL. Be concise: 3-5 bullet points max.'
  # 4096 leaves room for Gemini 2.5 thinking tokens (~1500-2500) plus the
  # ~500-1000 visible-token answer the concise prompt asks for.
  MAX_TOKENS=4096
  DEFAULT_TEMP=0.2
fi

TEMP="${TEMPERATURE:-$DEFAULT_TEMP}"
MIME=""
[[ "$USE_JSON" -eq 1 ]] && MIME="application/json"

# ---------------- cache key ----------------
cache_path() {
  local hash
  hash="$(printf '%s\n' "$MODEL|$USE_SYNTH|$USE_JSON|$TEMP|$1" \
         | python3 -c "import hashlib,sys; print(hashlib.sha256(sys.stdin.read().encode()).hexdigest()[:32])")"
  echo "$CACHE_DIR/$hash.json"
}

CACHE_FILE="$(cache_path "$query")"

if [[ "$USE_CACHE" -eq 1 && -f "$CACHE_FILE" ]]; then
  cat "$CACHE_FILE"
  echo
  exit 0
fi

mkdir -p "$CACHE_DIR"

# ---------------- daily quota guard ----------------
# Free tier is roughly 20 Flash RPD / ~25-100 Pro RPD. Hard-cap at 18 Flash
# and 20 Pro per UTC day so we never hit mid-routine 429s. Counter file
# resets daily via filename (cloud fresh-clone resets too).
TODAY_UTC="$(date -u +%Y-%m-%d)"
FLASH_COUNT_FILE="$CACHE_DIR/_calls_flash_${TODAY_UTC}.txt"
PRO_COUNT_FILE="$CACHE_DIR/_calls_pro_${TODAY_UTC}.txt"
RETRY_LOG="$CACHE_DIR/_retries_${TODAY_UTC}.log"
FLASH_DAILY_CAP=18
PRO_DAILY_CAP=20

_read_count() {
  [[ -f "$1" ]] && cat "$1" || echo 0
}
_bump_count() {
  local f="$1"
  local n
  n="$(_read_count "$f")"
  echo $((n + 1)) > "$f"
}
_log_retry() {
  # Demote retry-cycle messages from stderr to a quiet log file so routine
  # output stays clean; diagnostic is still recoverable.
  printf '[%s] %s\n' "$(date '+%H:%M:%S')" "$*" >> "$RETRY_LOG"
}

if [[ "$USE_SMART" -eq 1 ]]; then
  CURRENT_COUNT="$(_read_count "$PRO_COUNT_FILE")"
  if [[ "$CURRENT_COUNT" -ge "$PRO_DAILY_CAP" ]]; then
    echo "[gemini.sh] Flash daily budget pre-exhausted (Pro $CURRENT_COUNT/$PRO_DAILY_CAP)" >&2
    exit 5
  fi
else
  CURRENT_COUNT="$(_read_count "$FLASH_COUNT_FILE")"
  if [[ "$CURRENT_COUNT" -ge "$FLASH_DAILY_CAP" ]]; then
    echo "[gemini.sh] Flash daily budget pre-exhausted ($CURRENT_COUNT/$FLASH_DAILY_CAP)" >&2
    exit 5
  fi
fi

# ---------------- payload + call ----------------
make_payload() {
  local q="$1" sysp="$2" temp="$3" maxtok="$4" mime="$5"
  python3 -c "
import json, sys
payload = {
  'system_instruction': {'parts': [{'text': sys.argv[1]}]},
  'contents': [{'role': 'user', 'parts': [{'text': sys.argv[2]}]}],
  'tools': [{'google_search': {}}],
  'generationConfig': {
    'temperature': float(sys.argv[3]),
    'maxOutputTokens': int(sys.argv[4]),
  },
}
if sys.argv[5]:
    payload['generationConfig']['response_mime_type'] = sys.argv[5]
print(json.dumps(payload))
" "$sysp" "$q" "$temp" "$maxtok" "$mime"
}

call_gemini() {
  # echoes status code on stderr, body on stdout
  local model="$1" payload="$2" tmp http_code
  tmp="$(mktemp)"
  http_code="$(curl -sS -o "$tmp" -w "%{http_code}" \
    -H "Content-Type: application/json" \
    "https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${GEMINI_API_KEY}" \
    -d "$payload")"
  cat "$tmp"
  rm -f "$tmp"
  echo "$http_code" >&2
}

# First attempt
PAYLOAD="$(make_payload "$query" "$SYSTEM_PROMPT" "$TEMP" "$MAX_TOKENS" "$MIME")"
ERR_FILE="$(mktemp)"
BODY="$(call_gemini "$MODEL" "$PAYLOAD" 2>"$ERR_FILE" || true)"
HTTP_CODE="$(cat "$ERR_FILE" || echo 000)"
rm -f "$ERR_FILE"

# Handle Pro quota exhausted: retry on Flash with --synth (CoT)
if [[ "$HTTP_CODE" == "429" && "$USE_SMART" -eq 1 ]]; then
  _log_retry "Pro 429; falling back to Flash with synth/CoT prompt"
  FALLBACK_MODEL="$DEFAULT_MODEL"
  # Force --synth on the fallback so reasoning quality is preserved.
  FALLBACK_SYS='You are a precise financial research assistant. Use Google Search grounding. Cite every claim with a source URL and a date. Think step by step before answering: list evidence, then bull case, then bear case, then disconfirming evidence. Only then write the final structured answer.'
  FALLBACK_PAYLOAD="$(make_payload "$query" "$FALLBACK_SYS" "$TEMP" 8192 "$MIME")"
  ERR_FILE="$(mktemp)"
  BODY="$(call_gemini "$FALLBACK_MODEL" "$FALLBACK_PAYLOAD" 2>"$ERR_FILE" || true)"
  HTTP_CODE="$(cat "$ERR_FILE" || echo 000)"
  rm -f "$ERR_FILE"
fi

# If still 429, back off generously — free-tier per-minute caps need a full
# minute. Steps: 5s, 15s, 30s, 60s (>= the typical retryDelay returned by Google).
if [[ "$HTTP_CODE" == "429" ]]; then
  for sleep_s in 5 15 30 60; do
    _log_retry "429 persisted; sleeping ${sleep_s}s then retrying"
    sleep "$sleep_s"
    ERR_FILE="$(mktemp)"
    BODY="$(call_gemini "$MODEL" "$PAYLOAD" 2>"$ERR_FILE" || true)"
    HTTP_CODE="$(cat "$ERR_FILE" || echo 000)"
    rm -f "$ERR_FILE"
    [[ "$HTTP_CODE" != "429" ]] && break
  done
fi

if [[ "$HTTP_CODE" != "200" ]]; then
  echo "[gemini.sh] failed with HTTP $HTTP_CODE" >&2
  echo "$BODY" >&2
  [[ "$HTTP_CODE" == "429" ]] && exit 4
  exit 1
fi

# Success: cache + bump counter + emit
if [[ "$USE_CACHE" -eq 1 ]]; then
  printf '%s' "$BODY" > "$CACHE_FILE"
fi

if [[ "$USE_SMART" -eq 1 ]]; then
  _bump_count "$PRO_COUNT_FILE"
else
  _bump_count "$FLASH_COUNT_FILE"
fi

printf '%s\n' "$BODY"
