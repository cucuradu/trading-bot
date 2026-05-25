#!/usr/bin/env bash
# Install (or refresh) the trading-bot launchd dispatcher.
#
# Idempotent: safe to re-run after editing the plist or cron_dispatch.sh.
# Unloads the old job (if any), copies the plist to ~/Library/LaunchAgents/,
# and bootstraps the new one.
#
# Uninstall: bash scripts/install-launchd.sh uninstall

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LABEL="com.cucuradu.trading-dispatch"
PLIST_SRC="$ROOT/scripts/launchd/${LABEL}.plist"
PLIST_DST="$HOME/Library/LaunchAgents/${LABEL}.plist"
UID_NUM="$(id -u)"
DOMAIN="gui/${UID_NUM}"

action="${1:-install}"

unload_if_loaded() {
    if launchctl print "${DOMAIN}/${LABEL}" >/dev/null 2>&1; then
        echo "[install-launchd] unloading existing ${LABEL}"
        launchctl bootout "${DOMAIN}/${LABEL}" 2>/dev/null || true
    fi
}

case "$action" in
    install)
        if [[ ! -f "$PLIST_SRC" ]]; then
            echo "ERROR: plist source missing: $PLIST_SRC" >&2
            exit 1
        fi
        mkdir -p "$HOME/Library/LaunchAgents"
        chmod +x "$ROOT/scripts/cron_dispatch.sh"
        unload_if_loaded
        cp "$PLIST_SRC" "$PLIST_DST"
        echo "[install-launchd] copied to $PLIST_DST"
        launchctl bootstrap "$DOMAIN" "$PLIST_DST"
        echo "[install-launchd] loaded ${LABEL}"
        echo
        echo "Verify with:"
        echo "  launchctl print ${DOMAIN}/${LABEL} | head -20"
        echo "Logs:"
        echo "  tail -f $ROOT/cache/dispatch/launchd.out"
        ;;
    uninstall)
        unload_if_loaded
        if [[ -f "$PLIST_DST" ]]; then
            rm "$PLIST_DST"
            echo "[install-launchd] removed $PLIST_DST"
        fi
        echo "[install-launchd] ${LABEL} uninstalled"
        ;;
    status)
        if launchctl print "${DOMAIN}/${LABEL}" >/dev/null 2>&1; then
            launchctl print "${DOMAIN}/${LABEL}" | head -30
        else
            echo "[install-launchd] ${LABEL} NOT loaded"
            exit 1
        fi
        ;;
    *)
        echo "usage: bash scripts/install-launchd.sh {install|uninstall|status}" >&2
        exit 2
        ;;
esac
