#!/usr/bin/env bash
# Notification wrapper. Posts to WhatsApp via the free CallMeBot API.
# Usage: bash scripts/whatsapp.sh "<message>"
# If credentials are unset, appends to a local fallback file.
#
# Setup once (free, personal use):
#   From your phone, message +34 621 331 709 with text:
#     "I allow callmebot to send me messages"
#   The bot replies with your API key. Put it in WHATSAPP_APIKEY.
#   Put your phone number (with country code, no '+') in WHATSAPP_PHONE.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ENV_FILE="$ROOT/.env"
FALLBACK="$ROOT/DAILY-SUMMARY.md"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

if [[ $# -gt 0 ]]; then
  msg="$*"
else
  msg="$(cat)"
fi

if [[ -z "${msg// /}" ]]; then
  echo "usage: bash scripts/whatsapp.sh \"<message>\"" >&2
  exit 1
fi

stamp="$(date '+%Y-%m-%d %H:%M %Z')"

if [[ -z "${WHATSAPP_APIKEY:-}" || -z "${WHATSAPP_PHONE:-}" ]]; then
  printf "\n---\n## %s (fallback — WhatsApp not configured)\n%s\n" "$stamp" "$msg" >> "$FALLBACK"
  echo "[whatsapp fallback] appended to DAILY-SUMMARY.md"
  echo "$msg"
  exit 0
fi

# URL-encode the message (CallMeBot is GET-based)
encoded="$(python3 -c "import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1]))" "$msg")"

URL="https://api.callmebot.com/whatsapp.php?phone=${WHATSAPP_PHONE}&text=${encoded}&apikey=${WHATSAPP_APIKEY}"

# CallMeBot returns an HTML/text body even on success; -fsS so a non-2xx code fails.
curl -fsS "$URL" || {
  echo "[whatsapp] send failed; appending to fallback" >&2
  printf "\n---\n## %s (send failed, fallback)\n%s\n" "$stamp" "$msg" >> "$FALLBACK"
  exit 1
}
echo
