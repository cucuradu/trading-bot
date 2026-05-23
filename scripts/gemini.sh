#!/usr/bin/env bash
# Research wrapper. All market research goes through Gemini (free tier).
# Usage: bash scripts/gemini.sh "<query>"
# Exits with code 3 if GEMINI_API_KEY is unset so callers can fall back to WebSearch.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

query="${1:-}"
if [[ -z "$query" ]]; then
  echo "usage: bash scripts/gemini.sh \"<query>\"" >&2
  exit 1
fi

if [[ -z "${GEMINI_API_KEY:-}" ]]; then
  echo "WARNING: GEMINI_API_KEY not set. Fall back to native WebSearch." >&2
  exit 3
fi

MODEL="${GEMINI_MODEL:-gemini-3.5-flash}"
URL="https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${GEMINI_API_KEY}"

payload="$(python3 -c "
import json, sys
print(json.dumps({
    'system_instruction': {
        'parts': [{'text': 'You are a precise financial research assistant. Cite every claim with a source URL. Be concise: 3-5 bullet points max.'}]
    },
    'contents': [
        {'role': 'user', 'parts': [{'text': sys.argv[1]}]}
    ],
    'generationConfig': {
        'temperature': 0.2,
        'maxOutputTokens': 1024
    }
}))
" "$query")"

curl -fsS "$URL" \
  -H "Content-Type: application/json" \
  -d "$payload"
echo
