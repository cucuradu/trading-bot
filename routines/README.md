# Cloud Routine Prompts

These five files are the production prompts for Claude Code cloud routines (cron-scheduled agent runs). Each one is pasted **verbatim** into the routine's prompt field in the Claude Code cloud UI.

## Cron schedules (America/Chicago — adjust to your timezone)

| Routine | Cron | Local time |
|---|---|---|
| `pre-market.md` | `0 6 * * 1-5` | 6:00 AM weekdays |
| `market-open.md` | `30 8 * * 1-5` | 8:30 AM weekdays |
| `midday.md` | `0 12 * * 1-5` | 12:00 PM weekdays |
| `daily-summary.md` | `0 15 * * 1-5` | 3:00 PM weekdays |
| `weekly-review.md` | `0 16 * * 5` | 4:00 PM Friday |

## One-time setup before creating any routine

1. **Install Claude GitHub App** on the trading-bot repo (least-privilege: only this repo).
2. **Enable "Allow unrestricted branch pushes"** on the routine's environment. This is the #1 cause of first-run failures.
3. **Add env vars on the routine** (NOT a `.env` file — see explicit block in each prompt):
   - `ALPACA_API_KEY`, `ALPACA_SECRET_KEY`
   - `ALPACA_ENDPOINT=https://paper-api.alpaca.markets/v2` (paper phase)
   - `ALPACA_DATA_ENDPOINT=https://data.alpaca.markets/v2`
   - `GEMINI_API_KEY`, `GEMINI_MODEL=gemini-3.5-flash`
   - `WHATSAPP_PHONE`, `WHATSAPP_APIKEY`
   - **DO NOT set** `ALLOW_LIVE_TRADING` during the paper phase.
4. Click "Run now" once per routine to test before relying on the cron.
