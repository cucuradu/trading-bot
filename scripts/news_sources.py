#!/usr/bin/env python3
"""Free-tier news/data source adapters for the research pipeline.

Each adapter returns a list of normalized records:

    {
        "source": "newsapi|finnhub|edgar|google_news|reddit",
        "ticker": "NVDA",                # may be "" for keyword searches
        "title": "...",
        "url": "https://...",
        "published": "2026-05-26T12:30:00Z",   # ISO 8601 UTC
        "summary": "..." or None,
        "confidence": "high|medium|low",       # source-based heuristic
    }

Graceful degradation: a missing API key produces `[]` with a stderr warning,
never an exception. Network failures are caught and logged; the caller decides
what to do with partial results.

CLI:
    python scripts/news_sources.py gather SYM [SYM ...]
    python scripts/news_sources.py newsapi-query "Fed rate cut"
    python scripts/news_sources.py finnhub-earnings 14
    python scripts/news_sources.py finnhub-news NVDA 7
    python scripts/news_sources.py finnhub-analyst NVDA
    python scripts/news_sources.py finnhub-insider NVDA
    python scripts/news_sources.py edgar NVDA
    python scripts/news_sources.py google-news "NVDA AI capex"
    python scripts/news_sources.py reddit NVDA

Env vars:
    NEWS_API_KEY      free at newsapi.org
    FINNHUB_KEY       free at finnhub.io
    EDGAR_USER_AGENT  recommended; "Trading Bot <your-email>" per SEC fair-use
"""
from __future__ import annotations

import concurrent.futures
import json
import os
import sys
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests


_TIMEOUT = 10  # seconds per request
_ROOT = Path(__file__).resolve().parent.parent


# Load .env once at import time without overwriting pre-set env vars.
_ENV_FILE = _ROOT / ".env"
if _ENV_FILE.exists():
    for _line in _ENV_FILE.read_text().splitlines():
        _line = _line.strip()
        if not _line or _line.startswith("#"):
            continue
        if "=" not in _line:
            continue
        _k, _v = _line.split("=", 1)
        _k = _k.removeprefix("export ").strip()
        if _k and _k not in os.environ:
            os.environ[_k] = _v.strip().strip('"').strip("'")


_REDDIT_UA = "trading-bot-research/0.1 (research-pipeline; +https://github.com/cucuradu)"
_EDGAR_UA_DEFAULT = "trading-bot-research research-pipeline@example.com"


def _warn(msg: str) -> None:
    print(f"[news_sources] {msg}", file=sys.stderr)


def _iso_z(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# NewsAPI.org
# ---------------------------------------------------------------------------

def newsapi(query: str, *, limit: int = 10, hours_back: int = 48) -> list[dict]:
    """NewsAPI /v2/everything keyword search. 100/day free quota."""
    key = os.environ.get("NEWS_API_KEY")
    if not key:
        _warn("NEWS_API_KEY not set; newsapi adapter returning []")
        return []

    since = datetime.now(timezone.utc) - timedelta(hours=hours_back)
    params = {
        "q": query,
        "from": since.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": min(limit, 100),
        "apiKey": key,
    }
    try:
        r = requests.get("https://newsapi.org/v2/everything", params=params, timeout=_TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except (requests.RequestException, ValueError) as e:
        msg = str(e).replace(key, "***REDACTED***") if key else str(e)
        _warn(f"newsapi error: {msg}")
        return []

    out: list[dict] = []
    for item in (data.get("articles") or [])[:limit]:
        source_name = ((item.get("source") or {}).get("name") or "").lower()
        # Heuristic: tier-1 outlets get high confidence; others medium.
        conf = "high" if any(b in source_name for b in (
            "reuters", "bloomberg", "wall street journal", "wsj",
            "financial times", "associated press", "ap news", "cnbc",
        )) else "medium"
        out.append({
            "source": "newsapi",
            "ticker": "",  # NewsAPI doesn't ticker-tag; caller can add
            "title": item.get("title") or "",
            "url": item.get("url") or "",
            "published": item.get("publishedAt") or "",
            "summary": item.get("description"),
            "confidence": conf,
        })
    return out


# ---------------------------------------------------------------------------
# Finnhub (free tier; 60 req/min, no daily cap on most endpoints)
# ---------------------------------------------------------------------------

def _finnhub_get(path: str, params: dict) -> dict | list:
    key = os.environ.get("FINNHUB_KEY")
    if not key:
        _warn("FINNHUB_KEY not set; finnhub adapter returning []")
        return []
    params = {**params, "token": key}
    try:
        r = requests.get(f"https://finnhub.io/api/v1{path}", params=params, timeout=_TIMEOUT)
        r.raise_for_status()
        return r.json()
    except (requests.RequestException, ValueError) as e:
        # Redact the token from any error message before logging.
        msg = str(e).replace(key, "***REDACTED***") if key else str(e)
        _warn(f"finnhub error {path}: {msg}")
        return []


def finnhub_news(symbol: str, *, days: int = 7) -> list[dict]:
    today = datetime.now(timezone.utc).date()
    frm = today - timedelta(days=days)
    data = _finnhub_get("/company-news", {
        "symbol": symbol.upper(),
        "from": frm.isoformat(),
        "to": today.isoformat(),
    })
    if not isinstance(data, list):
        return []
    out: list[dict] = []
    for item in data:
        ts = item.get("datetime")
        try:
            pub = _iso_z(datetime.fromtimestamp(int(ts), tz=timezone.utc)) if ts else ""
        except (TypeError, ValueError):
            pub = ""
        out.append({
            "source": "finnhub",
            "ticker": symbol.upper(),
            "title": item.get("headline") or "",
            "url": item.get("url") or "",
            "published": pub,
            "summary": item.get("summary"),
            "confidence": "high",
        })
    return out


def finnhub_earnings(days_ahead: int = 14, symbols: list[str] | None = None) -> list[dict]:
    today = datetime.now(timezone.utc).date()
    to = today + timedelta(days=days_ahead)
    data = _finnhub_get("/calendar/earnings", {
        "from": today.isoformat(),
        "to": to.isoformat(),
    })
    raw = data.get("earningsCalendar", []) if isinstance(data, dict) else []
    out: list[dict] = []
    sym_filter = {s.upper() for s in symbols} if symbols else None
    for item in raw:
        sym = (item.get("symbol") or "").upper()
        if sym_filter and sym not in sym_filter:
            continue
        out.append({
            "source": "finnhub",
            "ticker": sym,
            "title": f"Earnings {sym} ({item.get('hour') or 'tbd'})",
            "url": "",
            "published": item.get("date") or "",
            "summary": f"epsEstimate={item.get('epsEstimate')}; revenueEstimate={item.get('revenueEstimate')}",
            "confidence": "high",
        })
    return out


def finnhub_analyst_changes(symbol: str) -> list[dict]:
    data = _finnhub_get("/stock/upgrade-downgrade", {"symbol": symbol.upper()})
    if not isinstance(data, list):
        return []
    out: list[dict] = []
    for item in data[:10]:
        out.append({
            "source": "finnhub",
            "ticker": symbol.upper(),
            "title": f"{item.get('company')}: {item.get('fromGrade') or '?'} -> {item.get('toGrade') or '?'} ({item.get('action')})",
            "url": "",
            "published": item.get("gradeTime") or "",
            "summary": None,
            "confidence": "high",
        })
    return out


def finnhub_insider(symbol: str) -> list[dict]:
    data = _finnhub_get("/stock/insider-transactions", {"symbol": symbol.upper()})
    raw = data.get("data", []) if isinstance(data, dict) else []
    out: list[dict] = []
    for item in raw[:10]:
        change = item.get("change")
        action = "BUY" if (isinstance(change, (int, float)) and change > 0) else "SELL"
        out.append({
            "source": "finnhub",
            "ticker": symbol.upper(),
            "title": f"Insider {action} {item.get('name', '?')} ({change} sh)",
            "url": "",
            "published": item.get("transactionDate") or item.get("filingDate") or "",
            "summary": f"position={item.get('share')}; price={item.get('transactionPrice')}",
            "confidence": "high",
        })
    return out


# ---------------------------------------------------------------------------
# SEC EDGAR Atom feed (no key; needs User-Agent per fair-use policy)
# ---------------------------------------------------------------------------

def edgar_filings(symbol: str, *, types: list[str] | None = None, limit: int = 5) -> list[dict]:
    types = types or ["8-K", "10-Q", "4"]
    ua = os.environ.get("EDGAR_USER_AGENT") or _EDGAR_UA_DEFAULT
    headers = {"User-Agent": ua, "Accept-Encoding": "gzip, deflate"}

    out: list[dict] = []
    for filing_type in types:
        params = {
            "action": "getcompany",
            "CIK": symbol.upper(),
            "type": filing_type,
            "dateb": "",
            "owner": "include",
            "count": limit,
            "output": "atom",
        }
        try:
            r = requests.get("https://www.sec.gov/cgi-bin/browse-edgar",
                             params=params, headers=headers, timeout=_TIMEOUT)
            r.raise_for_status()
            root = ET.fromstring(r.content)
        except (requests.RequestException, ET.ParseError) as e:
            _warn(f"edgar error {symbol}/{filing_type}: {e}")
            continue

        ns = {"a": "http://www.w3.org/2005/Atom"}
        for entry in root.findall("a:entry", ns)[:limit]:
            title_el = entry.find("a:title", ns)
            link_el = entry.find("a:link", ns)
            updated_el = entry.find("a:updated", ns)
            out.append({
                "source": "edgar",
                "ticker": symbol.upper(),
                "title": (title_el.text or "").strip() if title_el is not None else f"{filing_type} filing",
                "url": (link_el.get("href") or "") if link_el is not None else "",
                "published": (updated_el.text or "") if updated_el is not None else "",
                "summary": f"filing type {filing_type}",
                "confidence": "high",
            })
    return out


# ---------------------------------------------------------------------------
# Google News RSS (no auth)
# ---------------------------------------------------------------------------

def google_news_rss(query: str, *, limit: int = 10) -> list[dict]:
    url = ("https://news.google.com/rss/search?q="
           + urllib.parse.quote(query) + "&hl=en-US&gl=US&ceid=US:en")
    try:
        r = requests.get(url, timeout=_TIMEOUT,
                         headers={"User-Agent": _REDDIT_UA})
        r.raise_for_status()
        root = ET.fromstring(r.content)
    except (requests.RequestException, ET.ParseError) as e:
        _warn(f"google_news error: {e}")
        return []

    channel = root.find("channel")
    if channel is None:
        return []

    out: list[dict] = []
    for item in channel.findall("item")[:limit]:
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        source_el = item.find("source")
        source_name = (source_el.text or "").lower() if source_el is not None else ""
        conf = "high" if any(b in source_name for b in (
            "reuters", "bloomberg", "wall street journal", "wsj",
            "financial times", "ft.com", "cnbc",
        )) else "medium"
        out.append({
            "source": "google_news",
            "ticker": "",
            "title": title,
            "url": link,
            "published": pub,
            "summary": None,
            "confidence": conf,
        })
    return out


# ---------------------------------------------------------------------------
# Reddit JSON (no auth, custom User-Agent)
# ---------------------------------------------------------------------------

def reddit_mentions(symbol: str, *, subs: list[str] | None = None,
                    limit: int = 10) -> list[dict]:
    subs = subs or ["investing", "stockmarket", "wallstreetbets"]
    headers = {"User-Agent": _REDDIT_UA}
    out: list[dict] = []
    for sub in subs:
        params = {
            "q": symbol.upper(),
            "restrict_sr": "on",
            "sort": "new",
            "t": "week",
            "limit": min(limit, 25),
        }
        url = f"https://www.reddit.com/r/{sub}/search.json"
        try:
            r = requests.get(url, params=params, headers=headers, timeout=_TIMEOUT)
            r.raise_for_status()
            data = r.json()
        except (requests.RequestException, ValueError) as e:
            _warn(f"reddit error r/{sub}: {e}")
            continue

        for child in (data.get("data") or {}).get("children", [])[:limit]:
            d = child.get("data") or {}
            created = d.get("created_utc")
            try:
                pub = _iso_z(datetime.fromtimestamp(float(created), tz=timezone.utc)) if created else ""
            except (TypeError, ValueError):
                pub = ""
            score = d.get("score", 0)
            num_comments = d.get("num_comments", 0)
            # confidence floor: only flag high if heavily upvoted in r/investing
            if sub == "investing" and score > 100:
                conf = "medium"
            else:
                conf = "low"
            out.append({
                "source": "reddit",
                "ticker": symbol.upper(),
                "title": (d.get("title") or "")[:280],
                "url": f"https://reddit.com{d.get('permalink', '')}",
                "published": pub,
                "summary": f"r/{sub} | score={score} | comments={num_comments}",
                "confidence": conf,
            })
    return out


# ---------------------------------------------------------------------------
# Orchestration: parallel gather for one or many symbols
# ---------------------------------------------------------------------------

def gather(symbol: str) -> list[dict]:
    """Fetch from every source for a single symbol; return deduped list."""
    tasks = {
        "newsapi": lambda: newsapi(f'"{symbol}" stock'),
        "finnhub_news": lambda: finnhub_news(symbol),
        "finnhub_analyst": lambda: finnhub_analyst_changes(symbol),
        "finnhub_insider": lambda: finnhub_insider(symbol),
        "edgar": lambda: edgar_filings(symbol),
        "google_news": lambda: google_news_rss(f"{symbol} stock"),
        "reddit": lambda: reddit_mentions(symbol),
    }
    results: list[dict] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=7) as pool:
        futures = {pool.submit(fn): name for name, fn in tasks.items()}
        for fut in concurrent.futures.as_completed(futures):
            name = futures[fut]
            try:
                results.extend(fut.result())
            except Exception as e:  # belt-and-braces
                _warn(f"gather {symbol}/{name} unexpected: {e}")

    # Dedupe by URL (keep first occurrence). Empty-URL records (e.g., earnings)
    # stay as-is.
    seen: set[str] = set()
    deduped: list[dict] = []
    for r in results:
        u = r.get("url") or ""
        if u and u in seen:
            continue
        if u:
            seen.add(u)
        deduped.append(r)
    return deduped


def gather_many(symbols: list[str]) -> dict[str, list[dict]]:
    return {sym.upper(): gather(sym) for sym in symbols}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def egress_probe() -> dict:
    """Cheap reachability check for tier-2 sources that no API key gates.

    The cloud sandbox sometimes blocks outbound to SEC EDGAR, Google News, and
    Reddit at the network layer (observed 2026-05-29). When that happens the
    research pipeline silently degrades to Gemini-only — this probe surfaces
    the degradation up-front so the routine can flag it before researching
    each candidate.

    Per source: ok | http_<code> | error. No body parsing — just status.
    """
    targets = {
        "edgar": ("https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=AAPL&type=8-K&output=atom",
                  {"User-Agent": os.environ.get("EDGAR_USER_AGENT") or _EDGAR_UA_DEFAULT}),
        "google_news": ("https://news.google.com/rss/search?q=SPY&hl=en-US&gl=US&ceid=US:en",
                        {"User-Agent": _REDDIT_UA}),
        "reddit": ("https://www.reddit.com/r/stocks/.json?limit=1",
                   {"User-Agent": _REDDIT_UA}),
    }
    out: dict[str, str] = {}
    for name, (url, headers) in targets.items():
        try:
            r = requests.get(url, headers=headers, timeout=5)
            out[name] = "ok" if r.status_code == 200 else f"http_{r.status_code}"
        except requests.RequestException as e:
            out[name] = f"error:{type(e).__name__}"
    return out


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    cmd = sys.argv[1]
    args = sys.argv[2:]

    try:
        if cmd == "egress-probe":
            out = egress_probe()
        elif cmd == "gather":
            if not args:
                print("usage: gather SYM [SYM ...]", file=sys.stderr)
                return 2
            out = gather_many(args)
        elif cmd == "newsapi-query":
            out = newsapi(args[0])
        elif cmd == "finnhub-earnings":
            days = int(args[0]) if args else 14
            out = finnhub_earnings(days_ahead=days)
        elif cmd == "finnhub-news":
            days = int(args[1]) if len(args) > 1 else 7
            out = finnhub_news(args[0], days=days)
        elif cmd == "finnhub-analyst":
            out = finnhub_analyst_changes(args[0])
        elif cmd == "finnhub-insider":
            out = finnhub_insider(args[0])
        elif cmd == "edgar":
            out = edgar_filings(args[0])
        elif cmd == "google-news":
            out = google_news_rss(args[0])
        elif cmd == "reddit":
            out = reddit_mentions(args[0])
        else:
            print(f"unknown command: {cmd}", file=sys.stderr)
            print(__doc__, file=sys.stderr)
            return 1
    except IndexError:
        print(f"missing args for: {cmd}", file=sys.stderr)
        return 2

    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
