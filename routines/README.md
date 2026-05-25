# Cloud Routine Prompts

These five files are the production prompts for **Claude Routines** (Anthropic-hosted scheduled agent runs). Each one is pasted **verbatim** into the routine's prompt field in the Routines UI.

## Schedule (US Eastern Time — adjust the routine's local time to match)

| Routine | Target time (ET) | Why |
|---|---|---|
| `pre-market.md` | 06:30 ET weekdays | Before US futures get noisy |
| `market-open.md` | 09:35 ET weekdays | 5 min after the bell — fade the open spike |
| `midday.md` | 12:30 ET weekdays | Catch broken theses + tighten winners |
| `daily-summary.md` | 16:15 ET weekdays | After 4 PM close, includes EOD prints |
| `weekly-review.md` | 16:30 ET Friday | After daily-summary; weekly aggregates |

For CEST: add 6h to ET (e.g., 06:30 ET = 12:30 CEST during summer time, 13:30 CEST during winter).
DST changes between US and EU twice a year don't align — verify weekly during the spring/fall transition windows.

## One-time setup before creating any routine

1. **Install Claude GitHub App** on the trading-bot repo (least-privilege: only this repo).
2. **Enable "Allow unrestricted branch pushes"** on the routine's environment. This is the #1 cause of first-run failures.
3. **Add env vars on the routine** (NOT a `.env` file — see explicit block in each prompt):

   **Hard requirements (every routine):**
   - `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`
   - `ALPACA_ENDPOINT=https://paper-api.alpaca.markets/v2` (paper phase)
   - `ALPACA_DATA_ENDPOINT=https://data.alpaca.markets/v2`
   - `WHATSAPP_PHONE`, `WHATSAPP_APIKEY`

   **Research routines** (pre-market, market-open, midday, daily-summary, weekly-review):
   - `GEMINI_API_KEY`
   - `GEMINI_MODEL=gemini-2.5-flash` (default; routines also call `--smart` which uses Pro)
   - `GEMINI_SMART_MODEL=gemini-2.5-pro` (optional override; default is Pro)

   **Research-pipeline adapters** (pre-market + daily-summary):
   - `NEWS_API_KEY` — newsapi.org free tier (100/day)
   - `FINNHUB_KEY` — finnhub.io free tier (60/min)
   - `EDGAR_USER_AGENT="Your Name <your-email>"` — SEC EDGAR fair-use header

   **NEVER set during paper phase:**
   - `ALLOW_LIVE_TRADING` — leave unset. Setting it to `1` disables the live-endpoint failsafe in `scripts/alpaca.sh`.

4. Click **Run now** once per routine to test before relying on the cron.

## Updating routines

When `.claude/commands/<routine>.md` changes (the local version), update the matching `routines/<routine>.md` (cloud version), then **re-paste the cloud version into the Routines UI** — the UI does not auto-sync from the repo.

The cloud version differs from the local version only in:
- Cloud header (env vars, no `.env`, failsafe, persistence, token budget)
- Final STEP — mandatory `git pull --rebase` / `git commit` / `git push origin HEAD:main`

Body steps (everything between header and final commit) should stay identical between the two files. If they drift, the cloud will run an older workflow than your local `claude` sessions.

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Routine never runs | Cron not enabled in UI / wrong TZ | Toggle "Active" in UI; check the routine's local-time setting |
| First-run push fails | "Allow unrestricted branch pushes" not enabled | Routines settings → environment → enable |
| "KEY not set in environment" | Missing env var on the routine | Add the named var in routine settings |
| `exit 42` from `scripts/alpaca.sh` | `ALPACA_ENDPOINT` doesn't contain `paper-api` OR `ALLOW_LIVE_TRADING=1` | Verify endpoint env var; unset ALLOW_LIVE_TRADING |
| WhatsApp truncated | Body > 1500 chars URL-encoded | Each routine has a length-shrink fallback documented in its STEP for WhatsApp |
