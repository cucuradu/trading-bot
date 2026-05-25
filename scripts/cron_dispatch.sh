#!/usr/bin/env bash
# launchd dispatcher — runs every 5 minutes, fires the right Claude Code
# routine when the US Eastern wall-clock crosses a schedule boundary.
#
# Why this design instead of one plist per routine:
#   macOS launchd's StartCalendarInterval is local-time only; if you
#   hardcode CEST hours they break twice a year at DST flips. A single
#   periodic dispatcher checks ET via `TZ=America/New_York date` and is
#   DST-correct in both Europe AND the US.
#
# Idempotency: per-routine "done" files under cache/dispatch/<date>_<routine>
# prevent duplicate runs the same day.
#
# Schedule (US Eastern Time):
#   06:30 ET (±5 min)   pre-market         every weekday
#   09:35 ET            market-open        every weekday
#   12:30 ET            midday             every weekday
#   16:15 ET            daily-summary      every weekday
#   16:30 ET Fri        weekly-review      Fridays only
#
# Each Claude run uses --max-budget-usd 2 as a hard ceiling and logs to
# cache/dispatch/logs/<date>_<routine>.log.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
DISPATCH_DIR="$ROOT/cache/dispatch"
LOG_DIR="$DISPATCH_DIR/logs"
mkdir -p "$DISPATCH_DIR" "$LOG_DIR"

# Use ET for all schedule decisions
et_now() { TZ=America/New_York date +"$1"; }
ET_DATE="$(et_now '%Y-%m-%d')"
ET_HHMM="$(et_now '%H%M')"
ET_DOW="$(et_now '%u')"  # 1=Mon ... 7=Sun

# Skip weekends entirely (US markets closed; pre-market is the dry-run-friendly
# slot, but live trading routines should not run Sat/Sun).
if [[ "$ET_DOW" -ge 6 ]]; then
    exit 0
fi

# Skip US market holidays. Hardcoded short list; extend at the end of each year.
# Format: YYYY-MM-DD per holiday.
US_HOLIDAYS=(
    "2026-01-01"  # New Year
    "2026-01-19"  # MLK
    "2026-02-16"  # Presidents'
    "2026-04-03"  # Good Friday
    "2026-05-25"  # Memorial Day (mon)
    "2026-06-19"  # Juneteenth
    "2026-07-03"  # Independence (observed)
    "2026-09-07"  # Labor Day
    "2026-11-26"  # Thanksgiving
    "2026-12-25"  # Christmas
)
for h in "${US_HOLIDAYS[@]}"; do
    if [[ "$ET_DATE" == "$h" ]]; then
        # Pre-market still runs on a holiday — useful to research for the NEXT
        # trading session. But trading-routines themselves do not.
        SKIP_TRADING=1
        break
    fi
done
SKIP_TRADING="${SKIP_TRADING:-0}"

# Convert HHMM to integer for ±5-min window comparisons
hhmm_int() { echo $((10#$1)); }
NOW="$(hhmm_int "$ET_HHMM")"

# Window: routine fires when ET wall-clock is within ±5 min of the target.
in_window() {
    local target="$1"
    local diff=$((NOW - target))
    [[ $diff -ge -5 && $diff -le 5 ]]
}

# Run a routine if not already done today
maybe_run() {
    local routine="$1"
    local guard="$DISPATCH_DIR/${ET_DATE}_${routine}.done"
    local log="$LOG_DIR/${ET_DATE}_${routine}.log"

    if [[ -f "$guard" ]]; then
        return 0
    fi

    echo "[$(date)] dispatching /${routine} (ET ${ET_HHMM})" | tee -a "$log"
    # Claude needs a working directory; cd into the trading bot repo.
    # --max-budget-usd is a per-invocation hard ceiling.
    if cd "$ROOT" && claude -p "/${routine}" --max-budget-usd 2 >>"$log" 2>&1; then
        touch "$guard"
        echo "[$(date)] /${routine} OK" | tee -a "$log"
    else
        rc=$?
        echo "[$(date)] /${routine} FAILED rc=$rc" | tee -a "$log"
        # Alert via WhatsApp; bot still owns the situation but user is notified.
        bash "$ROOT/scripts/whatsapp.sh" "ALERT: /${routine} dispatcher failed (rc=$rc) at $(et_now '%F %H:%M ET'); see ${log}" >/dev/null 2>&1 || true
    fi
}

# ---- Schedule dispatch ----
if in_window 630; then
    # Pre-market: runs every weekday, even on US holidays (research for next session)
    maybe_run pre-market
fi

if [[ "$SKIP_TRADING" -eq 0 ]]; then
    if in_window 935; then
        maybe_run market-open
    fi
    if in_window 1230; then
        maybe_run midday
    fi
    if in_window 1615; then
        maybe_run daily-summary
    fi
    # Weekly review only on Fridays (US ET day 5)
    if [[ "$ET_DOW" == "5" ]] && in_window 1630; then
        maybe_run weekly-review
    fi
fi
