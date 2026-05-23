# Trading Bot

Autonomous AI trading bot. **Paper trading only** for the next 10–12 weeks (forward-test phase). Built on Claude Code (decisions) + Gemini 3.5 Flash (research, free) + Alpaca paper API + WhatsApp notifications.

## Quick start (local mode)

1. **Get credentials** (all free):
   - Alpaca paper account → API key + secret: https://alpaca.markets/
   - Google AI Studio → API key: https://aistudio.google.com/apikey (confirm `gemini-3.5-flash` is in the model list)
   - CallMeBot WhatsApp → from your phone, message `+34 621 331 709` with text `I allow callmebot to send me messages`. The bot replies with your API key.

2. **Configure**:
   ```bash
   cp env.template .env
   # edit .env with your credentials
   ```

3. **Install Python deps for tests + yfinance**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r tests/requirements.txt
   ```

4. **Smoke test**:
   ```bash
   # Open this directory in Claude Code and run:
   /portfolio                              # should print paper account state

   bash scripts/gemini.sh "WTI oil price today"
   bash scripts/whatsapp.sh "test from trading bot"
   python scripts/yfinance.py quote SPY
   ```

5. **Run the safety tests**:
   ```bash
   pytest tests/                           # all green = code matches the rules
   ```

## Strategy

See [memory/TRADING-STRATEGY.md](memory/TRADING-STRATEGY.md). Hard rules:
- Stocks only — never options
- Max 5–6 positions, max 20% per position, max 3 new trades/week
- 10% trailing stop on every position (real GTC order on Alpaca)
- Cut losers at −7%; tighten trail to 7% at +15%, 5% at +20%

## Safety: the live-trading failsafe

`scripts/alpaca.sh` **refuses** `order`/`cancel`/`close` operations if:
- `ALPACA_ENDPOINT` does not contain `paper-api`, AND
- `ALLOW_LIVE_TRADING` is not set to `1`

Exit code 42 indicates a failsafe trip. Verified by `tests/test_alpaca_failsafe.py`.

During the 10–12 week paper-trading phase, `ALLOW_LIVE_TRADING` MUST be unset on every routine and locally.

## Architecture

- `scripts/` — shell wrappers (single I/O boundary): alpaca, gemini, yfinance, whatsapp
- `memory/` — git-as-memory; the bot's state between runs (committed to main)
- `.claude/commands/` — local slash commands (`/portfolio`, `/trade`, `/pre-market`, etc.)
- `routines/` — cloud cron prompts (5 weekday runs, paste into Claude Code cloud routines)
- `tests/` — pytest safety suite (buy-gate logic, order shapes, failsafe)
- `CLAUDE.md` — agent rulebook auto-loaded by Claude Code

## Cloud routines (production)

Setup steps in [routines/README.md](routines/README.md). One-time prerequisites:
- Install the Claude GitHub App on the repo
- Enable "Allow unrestricted branch pushes" on the routine environment
- Set env vars on the routine (NEVER as a `.env` file in the repo)

## After 10–12 weeks of paper trading

Decision criteria in the plan file. **Do not** flip to live without:
- Beating S&P 500 by ≥2% over 10+ weeks
- Zero failsafe trips in the prior 4 weeks
- Reading the bot's reasoning in `memory/RESEARCH-LOG.md` and finding it sound
- Funding the account only with money you can afford to lose
