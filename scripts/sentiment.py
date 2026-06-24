#!/usr/bin/env python3
"""Local news-sentiment via VADER — free, offline, no API quota.

Replaces the "ask Gemini if the news is bullish" step. Pulls recent headlines
from yfinance (no key, no quota) and scores them with VADER, returning an
aggregate compound score + a Bullish/Neutral/Bearish label. Deterministic, so it
never degrades on a Gemini 429.

Usage:
  python scripts/sentiment.py score SYM          # fetch yfinance headlines + score
  python scripts/sentiment.py score -            # score headlines from stdin (one per line)
"""
from __future__ import annotations

import json
import sys

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

_ANALYZER = SentimentIntensityAnalyzer()


def _headlines_from_yf(symbol: str) -> list[str]:
    import yfinance as yf
    from _yf_compat import patch as _patch_yf
    _patch_yf()
    out: list[str] = []
    for item in (yf.Ticker(symbol).news or []):
        # yfinance has shifted schema across versions: flat {title} or {content:{title}}.
        title = item.get("title") or (item.get("content") or {}).get("title")
        if title:
            out.append(str(title))
    return out


def score(headlines: list[str]) -> dict:
    scored = [(_ANALYZER.polarity_scores(h)["compound"], h) for h in headlines]
    n = len(scored)
    if not n:
        return {"n_headlines": 0, "mean_compound": None, "label": "no_data",
                "pct_positive": None, "pct_negative": None, "headlines": []}
    comps = [c for c, _ in scored]
    mean = sum(comps) / n
    pos = sum(1 for c in comps if c >= 0.05)
    neg = sum(1 for c in comps if c <= -0.05)
    label = "Bullish" if mean >= 0.05 else "Bearish" if mean <= -0.05 else "Neutral"
    return {
        "n_headlines": n,
        "mean_compound": round(mean, 3),
        "label": label,
        "pct_positive": round(100 * pos / n, 1),
        "pct_negative": round(100 * neg / n, 1),
        # most-positive and most-negative headline for the candidate block
        "top_positive": max(scored)[1],
        "top_negative": min(scored)[1],
    }


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) < 2 or argv[0] != "score":
        print(__doc__, file=sys.stderr)
        return 1
    target = argv[1]
    if target == "-":
        headlines = [ln.strip() for ln in sys.stdin if ln.strip()]
    else:
        headlines = _headlines_from_yf(target)
    result = score(headlines)
    result["symbol"] = None if target == "-" else target.upper()
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
