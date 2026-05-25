"""Tests for scripts/news_sources.py — adapters + gather orchestration.

All HTTP is monkeypatched. No live network calls. Tests verify:
- Each adapter returns the normalized record shape.
- Missing API key → adapter returns [] (graceful degradation).
- Network error / bad JSON → adapter returns [] (no crash).
- gather() dedupes by URL and tolerates per-source failures.
"""
from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import news_sources as ns  # noqa: E402


# ---------------- helpers ----------------

class _FakeResponse:
    def __init__(self, *, json_data=None, content=b"", status=200):
        self._json = json_data
        self.content = content
        self.status_code = status

    def json(self):
        if self._json is None:
            raise ValueError("no json")
        return self._json

    def raise_for_status(self):
        if 400 <= self.status_code:
            raise ns.requests.HTTPError(f"HTTP {self.status_code}")


def _patch_get(monkeypatch, response_or_raiser):
    """If `response_or_raiser` is callable, call it with (url, **kw) and return its result."""
    if callable(response_or_raiser):
        monkeypatch.setattr(ns.requests, "get", response_or_raiser)
    else:
        monkeypatch.setattr(ns.requests, "get", lambda *a, **kw: response_or_raiser)


# ---------------- NewsAPI ----------------

def test_newsapi_returns_empty_when_key_missing(monkeypatch):
    monkeypatch.delenv("NEWS_API_KEY", raising=False)
    assert ns.newsapi("anything") == []


def test_newsapi_parses_articles_and_tags_confidence(monkeypatch):
    monkeypatch.setenv("NEWS_API_KEY", "x")
    payload = {
        "articles": [
            {
                "source": {"name": "Reuters"},
                "title": "Apple beats Q3 estimates",
                "url": "https://reuters.com/a",
                "publishedAt": "2026-05-26T12:00:00Z",
                "description": "summary",
            },
            {
                "source": {"name": "RandomBlog"},
                "title": "...",
                "url": "https://example.com/b",
                "publishedAt": "2026-05-26T11:00:00Z",
                "description": None,
            },
        ]
    }
    _patch_get(monkeypatch, _FakeResponse(json_data=payload))
    out = ns.newsapi("AAPL", limit=10)
    assert len(out) == 2
    assert out[0]["source"] == "newsapi"
    assert out[0]["confidence"] == "high"
    assert out[1]["confidence"] == "medium"
    assert out[0]["url"] == "https://reuters.com/a"


def test_newsapi_returns_empty_on_network_error(monkeypatch):
    monkeypatch.setenv("NEWS_API_KEY", "x")

    def boom(*a, **kw):
        raise ns.requests.ConnectionError("nope")
    _patch_get(monkeypatch, boom)
    assert ns.newsapi("AAPL") == []


# ---------------- Finnhub ----------------

def test_finnhub_news_missing_key(monkeypatch):
    monkeypatch.delenv("FINNHUB_KEY", raising=False)
    assert ns.finnhub_news("AAPL") == []


def test_finnhub_news_parses(monkeypatch):
    monkeypatch.setenv("FINNHUB_KEY", "x")
    payload = [
        {
            "datetime": 1714377600,  # epoch
            "headline": "AAPL: Q1 ER beat",
            "url": "https://finnhub.io/news/1",
            "summary": "...",
        }
    ]
    _patch_get(monkeypatch, _FakeResponse(json_data=payload))
    out = ns.finnhub_news("AAPL")
    assert len(out) == 1
    assert out[0]["source"] == "finnhub"
    assert out[0]["confidence"] == "high"
    assert out[0]["ticker"] == "AAPL"
    assert out[0]["published"].endswith("Z")


def test_finnhub_earnings_filters_by_symbol(monkeypatch):
    monkeypatch.setenv("FINNHUB_KEY", "x")
    payload = {"earningsCalendar": [
        {"symbol": "AAPL", "date": "2026-08-01", "hour": "amc",
         "epsEstimate": 1.4, "revenueEstimate": 90e9},
        {"symbol": "MSFT", "date": "2026-07-25", "hour": "amc",
         "epsEstimate": 2.6, "revenueEstimate": 56e9},
    ]}
    _patch_get(monkeypatch, _FakeResponse(json_data=payload))
    out = ns.finnhub_earnings(symbols=["AAPL"])
    assert len(out) == 1
    assert out[0]["ticker"] == "AAPL"


def test_finnhub_analyst_changes_labels_direction(monkeypatch):
    monkeypatch.setenv("FINNHUB_KEY", "x")
    payload = [
        {"company": "Morgan Stanley", "fromGrade": "Equal-Weight",
         "toGrade": "Overweight", "action": "up", "gradeTime": "2026-05-26"},
    ]
    _patch_get(monkeypatch, _FakeResponse(json_data=payload))
    out = ns.finnhub_analyst_changes("AAPL")
    assert "Overweight" in out[0]["title"]
    assert out[0]["confidence"] == "high"


def test_finnhub_insider_classifies_buy_vs_sell(monkeypatch):
    monkeypatch.setenv("FINNHUB_KEY", "x")
    payload = {"data": [
        {"name": "Cook, Timothy", "change": -1000, "share": 100000,
         "transactionPrice": 220.0, "transactionDate": "2026-05-20"},
    ]}
    _patch_get(monkeypatch, _FakeResponse(json_data=payload))
    out = ns.finnhub_insider("AAPL")
    assert "SELL" in out[0]["title"]


# ---------------- SEC EDGAR ----------------

def test_edgar_parses_atom_feed(monkeypatch):
    atom = b"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>8-K - Apple Inc</title>
    <link href="https://www.sec.gov/Archives/...8-K.htm"/>
    <updated>2026-05-25T13:00:00-04:00</updated>
  </entry>
</feed>"""
    _patch_get(monkeypatch, _FakeResponse(content=atom))
    out = ns.edgar_filings("AAPL", types=["8-K"], limit=5)
    # types loop iterates 1 time × 1 entry parsed
    assert len(out) == 1
    assert out[0]["source"] == "edgar"
    assert out[0]["url"].startswith("https://www.sec.gov")
    assert out[0]["confidence"] == "high"


def test_edgar_skips_unparseable(monkeypatch):
    _patch_get(monkeypatch, _FakeResponse(content=b"not xml"))
    out = ns.edgar_filings("AAPL", types=["8-K"], limit=5)
    assert out == []


# ---------------- Google News RSS ----------------

def test_google_news_parses_rss(monkeypatch):
    rss = b"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <item>
      <title>AAPL launches iPhone 18</title>
      <link>https://news.google.com/foo</link>
      <pubDate>Wed, 21 May 2026 12:00:00 GMT</pubDate>
      <source>Reuters</source>
    </item>
    <item>
      <title>RandomBlog Take</title>
      <link>https://news.google.com/bar</link>
      <pubDate>Tue, 20 May 2026 09:00:00 GMT</pubDate>
      <source>RandomBlog</source>
    </item>
  </channel>
</rss>"""
    _patch_get(monkeypatch, _FakeResponse(content=rss))
    out = ns.google_news_rss("AAPL")
    assert len(out) == 2
    assert out[0]["source"] == "google_news"
    assert out[0]["confidence"] == "high"
    assert out[1]["confidence"] == "medium"


# ---------------- Reddit ----------------

def test_reddit_mentions_parses_json(monkeypatch):
    payload = {"data": {"children": [
        {"data": {
            "title": "Discussion on AAPL Q3",
            "permalink": "/r/investing/comments/abc/",
            "created_utc": 1716729600,
            "score": 250,
            "num_comments": 30,
        }},
    ]}}
    _patch_get(monkeypatch, _FakeResponse(json_data=payload))
    out = ns.reddit_mentions("AAPL", subs=["investing"])
    assert len(out) == 1
    assert out[0]["source"] == "reddit"
    # score > 100 in r/investing → medium confidence
    assert out[0]["confidence"] == "medium"
    assert out[0]["url"].endswith("/r/investing/comments/abc/")


def test_reddit_low_confidence_on_wsb(monkeypatch):
    payload = {"data": {"children": [
        {"data": {
            "title": "$AAPL to the moon",
            "permalink": "/r/wallstreetbets/comments/xyz/",
            "created_utc": 1716729600,
            "score": 4000,
            "num_comments": 200,
        }},
    ]}}
    _patch_get(monkeypatch, _FakeResponse(json_data=payload))
    out = ns.reddit_mentions("AAPL", subs=["wallstreetbets"])
    assert out[0]["confidence"] == "low"


# ---------------- Orchestration ----------------

def test_gather_dedupes_by_url(monkeypatch):
    """If two adapters return the same URL, gather() keeps the first."""
    monkeypatch.setattr(ns, "newsapi", lambda *a, **kw: [{
        "source": "newsapi", "ticker": "", "title": "A",
        "url": "https://x/a", "published": "", "summary": None, "confidence": "high",
    }])
    monkeypatch.setattr(ns, "finnhub_news", lambda *a, **kw: [{
        "source": "finnhub", "ticker": "AAPL", "title": "B",
        "url": "https://x/a", "published": "", "summary": None, "confidence": "high",
    }])
    # Stub everything else to empty
    for name in ("finnhub_analyst_changes", "finnhub_insider", "edgar_filings",
                 "google_news_rss", "reddit_mentions"):
        monkeypatch.setattr(ns, name, lambda *a, **kw: [])
    out = ns.gather("AAPL")
    assert len(out) == 1


def test_gather_tolerates_per_source_exceptions(monkeypatch):
    monkeypatch.setattr(ns, "newsapi", lambda *a, **kw: [{
        "source": "newsapi", "ticker": "", "title": "OK",
        "url": "https://ok", "published": "", "summary": None, "confidence": "high",
    }])

    def boom(*a, **kw):
        raise RuntimeError("nope")
    for name in ("finnhub_news", "finnhub_analyst_changes", "finnhub_insider",
                 "edgar_filings", "google_news_rss", "reddit_mentions"):
        monkeypatch.setattr(ns, name, boom)
    out = ns.gather("AAPL")
    assert len(out) == 1
    assert out[0]["title"] == "OK"
