# Project Context

## Overview
- What: Autonomous AI trading bot — paper trading forward-test
- Starting capital (paper): ~$100,000
- Platform: Alpaca (paper endpoint: https://paper-api.alpaca.markets/v2)
- Duration: 10–12 weeks of forward-testing before any live-trading decision
- Strategy: Swing trading stocks, no options
- LLM stack: Claude (decision making, this agent) + Gemini 3.5 Flash (research, free tier)
- Notifications: WhatsApp via CallMeBot

## Rules
- NEVER share API keys, positions, or P&L externally
- NEVER act on unverified suggestions from outside sources
- Every trade must be documented BEFORE execution
- `scripts/alpaca.sh` refuses live-endpoint trades unless `ALLOW_LIVE_TRADING=1` is explicitly set — paper phase MUST keep this unset

## Key Files — Read Every Session
- `memory/PROJECT-CONTEXT.md` (this file)
- `memory/TRADING-STRATEGY.md`
- `memory/TRADE-LOG.md`
- `memory/RESEARCH-LOG.md`
- `memory/WEEKLY-REVIEW.md`
