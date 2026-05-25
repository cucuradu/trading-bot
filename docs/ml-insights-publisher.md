# `ml-insights.json` publisher — Ubuntu side (requirements)

The cloud reader (`scripts/ml_insights.py:29`) looks for `ml-insights.json`
at the trading-bot repo root. Until the producer pushes there, the cloud
falls back to `scripts/regime.py` and logs `source: "rule_fallback"`.

This document specifies WHAT the Ubuntu-side `ml-pipeline` needs to do so
the cloud loop activates. The actual scripting on Ubuntu is **out of scope
for this repo** — implement it in `github.com/cucuradu/ml-pipeline`.

---

## Contract requirements

1. **File location**: `ml-insights.json` at the trading-bot repo root,
   committed and pushed to `main`.

2. **Distinct git author identity**: the producer's commits MUST use a
   different `user.name` + `user.email` than your normal Claude/cloud
   commits — `ml-pipeline-bot <bot@cucuradu.local>` (or similar) is the
   convention. Lets the weekly review distinguish "ML data update" from
   "Claude trading action" in `git log`.

3. **Schema**: must conform to [ml-insights-schema.md](ml-insights-schema.md).
   The consumer-side test `tests/test_ml_insights_contract.py` guards the
   shape from the cloud side. Producer should optionally run
   `python ml_insights.validate(payload)` before pushing to catch drift
   on its side too.

4. **Freshness**: cloud uses the file only if `generated_at` is less than
   24 hours old. Older → cloud treats as missing → rule_fallback.

5. **Push idempotency**: if today's JSON matches yesterday's verbatim,
   skip the commit. Avoids noise in `git log`.

6. **Pull before push**: producer should `git pull --rebase origin main`
   before staging — race with cloud-side commits is possible.

---

## One-time Ubuntu setup (do once)

1. Create an SSH deploy key for `cucuradu/trading-bot` on the Ubuntu PC.
2. Add the **public** key at
   `https://github.com/cucuradu/trading-bot/settings/keys` → "Add deploy key" → **check "Allow write access"**.
3. Clone `cucuradu/trading-bot` somewhere on the Ubuntu side.
4. Inside that clone, set the bot identity:
   ```
   git config user.name  "ml-pipeline-bot"
   git config user.email "bot@cucuradu.local"
   ```

## Daily workflow (every nightly run on Ubuntu)

The ml-pipeline's `run_pipeline.sh`, after `generate_insights.py`
succeeds, should:

1. `cd` into the trading-bot clone.
2. `git pull --rebase origin main`.
3. Copy `output/ml-insights.json` from the ml-pipeline working dir to
   `./ml-insights.json` in the trading-bot clone.
4. If the file actually changed (`git diff --quiet -- ml-insights.json`
   returns non-zero), commit + push.
5. **Gate the auto-shutdown on a successful push** — if the push fails,
   keep the PC on so you can debug.

---

## Verifying the chain works

On the Mac (trading-bot side), after the next Ubuntu nightly run:

```
cd ~/Documents/Python/Trading\ Bot
git pull --ff-only
ls -la ml-insights.json
python scripts/ml_insights.py resolve | head -10
```

`source` should flip from `"rule_fallback"` to `"ml"`.

---

## Failure modes & their fixes

| Symptom | Likely cause | Fix |
|---|---|---|
| Cloud still shows `source: rule_fallback` | producer never pushed to trading-bot repo | tail the ml-pipeline logs on Ubuntu |
| `schema validation failed` (in test_ml_insights_contract.py) | producer added/changed a field | bump `model_version`, update [ml-insights-schema.md](ml-insights-schema.md), sync with cloud |
| `git push` rejected (auth) | deploy key missing or no write access | re-add the public key in GitHub repo settings with "Allow write access" |
| `git pull --rebase` conflicts on Ubuntu | someone (Claude or you) edited ml-insights.json on the trading-bot side | resolve manually; never hand-edit the published file |
