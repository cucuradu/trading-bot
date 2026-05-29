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
  # Defensive: detect that the caller likely passed `bash scripts/whatsapp.sh
  # "$215.33"` and got bitten by bash positional-arg expansion. If the message
  # looks like dollar-amounts had their leading digit eaten, warn loudly. Use a
  # heredoc piped to stdin instead.
  if printf %s "$msg" | grep -qE '(^|[^0-9.])\.[0-9]+|(^|[^0-9])[0-9]{1,3}\.[0-9]{2}([^0-9]|$)'; then
    echo "[whatsapp] WARNING: argument-mode invocation detected. If your message" >&2
    echo "[whatsapp] contains \$<digit>… amounts, bash may have eaten leading digits." >&2
    echo "[whatsapp] Use heredoc instead: bash scripts/whatsapp.sh << 'WAEOF'..." >&2
  fi
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

# CallMeBot is GET-based, so the encoded message lives inside the URL.
# Long messages silently truncate around ~2000 chars of URL. We split on
# newline boundaries and send multiple chunks tagged "(i/N) ".
MAX_CHARS="${WHATSAPP_MAX_CHARS:-900}"

mapfile -t URLS < <(python3 - "$msg" "$MAX_CHARS" "$WHATSAPP_PHONE" "$WHATSAPP_APIKEY" <<'PY'
import sys, urllib.parse

msg, max_chars, phone, apikey = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4]

def split_message(text, limit):
    if len(text) <= limit:
        return [text]
    chunks, remaining = [], text
    while len(remaining) > limit:
        window = remaining[:limit]
        for sep in ("\n\n", "\n", " "):
            idx = window.rfind(sep)
            if idx > limit // 2:
                chunks.append(remaining[:idx].rstrip())
                remaining = remaining[idx + len(sep):]
                break
        else:
            chunks.append(remaining[:limit])
            remaining = remaining[limit:]
    if remaining.strip():
        chunks.append(remaining)
    return chunks

# Reserve ~8 chars for "(i/N) " prefix when multi-chunk
chunks = split_message(msg, max_chars - 8)
n = len(chunks)
if n > 1:
    chunks = [f"({i+1}/{n}) {c}" for i, c in enumerate(chunks)]

for c in chunks:
    encoded = urllib.parse.quote(c)
    print(f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={encoded}&apikey={apikey}")
PY
)

total="${#URLS[@]}"
for i in "${!URLS[@]}"; do
  if ! curl -fsS "${URLS[$i]}"; then
    echo "[whatsapp] send failed on chunk $((i+1))/${total}; appending full message to fallback" >&2
    printf "\n---\n## %s (send failed on chunk %d/%d, fallback)\n%s\n" "$stamp" "$((i+1))" "$total" "$msg" >> "$FALLBACK"
    exit 1
  fi
  echo
  # space chunks out a bit so CallMeBot doesn't rate-limit
  if (( i < total - 1 )); then
    sleep 1
  fi
done
