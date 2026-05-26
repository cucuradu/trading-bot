"""Tests for scripts/research.py — parsing helpers + Gemini-stubbed orchestration.

The Gemini subprocess is monkeypatched: tests verify the orchestrator calls
gemini.sh with the right flags and parses the response payload correctly.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

import research  # noqa: E402


# ---------------- _run_gemini: response parsing ----------------

class _FakeCompleted:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def test_run_gemini_extracts_text_from_standard_payload(monkeypatch):
    body = json.dumps({
        "candidates": [{
            "content": {"parts": [{"text": "Hello synthesis."}]}
        }]
    })
    monkeypatch.setattr(research.subprocess, "run",
                        lambda *a, **kw: _FakeCompleted(stdout=body))
    out = research._run_gemini("anything")
    assert out == "Hello synthesis."


def test_run_gemini_passes_flags(monkeypatch):
    captured = {}

    def fake_run(cmd, *a, **kw):
        captured["cmd"] = cmd
        return _FakeCompleted(stdout=json.dumps({
            "candidates": [{"content": {"parts": [{"text": "ok"}]}}]
        }))
    monkeypatch.setattr(research.subprocess, "run", fake_run)
    research._run_gemini("q", smart=True, synth=True, temperature=0.1)
    assert "--smart" in captured["cmd"]
    assert "--synth" in captured["cmd"]
    assert "--temperature" in captured["cmd"]
    idx = captured["cmd"].index("--temperature")
    assert captured["cmd"][idx + 1] == "0.1"


def test_run_gemini_handles_api_key_missing(monkeypatch):
    monkeypatch.setattr(research.subprocess, "run",
                        lambda *a, **kw: _FakeCompleted(returncode=3))
    out = research._run_gemini("q")
    assert "GEMINI_API_KEY" in out


def test_run_gemini_handles_quota_exhausted(monkeypatch):
    monkeypatch.setattr(research.subprocess, "run",
                        lambda *a, **kw: _FakeCompleted(returncode=4))
    out = research._run_gemini("q", smart=True)
    assert "quota exhausted" in out.lower()


def test_run_gemini_handles_block(monkeypatch):
    body = json.dumps({"promptFeedback": {"blockReason": "SAFETY"}})
    monkeypatch.setattr(research.subprocess, "run",
                        lambda *a, **kw: _FakeCompleted(stdout=body))
    out = research._run_gemini("q")
    assert "blocked" in out.lower()


def test_run_gemini_falls_back_to_raw_text_on_non_json(monkeypatch):
    monkeypatch.setattr(research.subprocess, "run",
                        lambda *a, **kw: _FakeCompleted(stdout="raw response"))
    out = research._run_gemini("q")
    assert out == "raw response"


def test_run_gemini_timeout_returns_marker(monkeypatch):
    def boom(*a, **kw):
        raise research.subprocess.TimeoutExpired(cmd="gemini", timeout=120)
    monkeypatch.setattr(research.subprocess, "run", boom)
    assert "timeout" in research._run_gemini("q").lower()


# ---------------- _split_research_log + _extract_h2_section ----------------

_SAMPLE_LOG = """\
# Research Log

## 2026-05-23 — Pre-market

regime: Bull, NVDA mentioned.

## 2026-05-24 — Pre-market

regime: Bull, no AAPL today.

## 2026-05-25 — Pre-market

regime: Neutral, NVDA + AAPL covered.
"""


def test_split_research_log_parses_dates():
    sections = research._split_research_log(_SAMPLE_LOG)
    assert len(sections) == 3
    assert [s[0].isoformat() for s in sections] == ["2026-05-23", "2026-05-24", "2026-05-25"]


def test_extract_h2_section_finds_match():
    notes = "## AAPL (XLK)\n- Thesis: X\n\n## NVDA (XLK)\n- Thesis: Y\n"
    section = research._extract_h2_section(notes, "NVDA")
    assert section.startswith("## NVDA (XLK)")
    assert "Thesis: Y" in section


def test_extract_h2_section_returns_none_on_miss():
    notes = "## AAPL (XLK)\n- Thesis: X\n"
    assert research._extract_h2_section(notes, "ZZZZ") is None


# ---------------- cmd_latest_on ----------------

def test_cmd_latest_on_returns_matching_sections(monkeypatch, tmp_path):
    log = tmp_path / "RESEARCH-LOG.md"
    log.write_text(_SAMPLE_LOG)
    monkeypatch.setattr(research, "RESEARCH_LOG", log)
    # Use a date that includes the latest entry
    from datetime import date
    class _FrozenDate(date):
        @classmethod
        def today(cls):
            return date(2026, 5, 25)
    monkeypatch.setattr(research, "date", _FrozenDate)

    out = research.cmd_latest_on("NVDA", days=7)
    assert "NVDA mentioned" in out  # from 2026-05-23
    assert "NVDA + AAPL covered" in out  # from 2026-05-25


def test_cmd_latest_on_excludes_old(monkeypatch, tmp_path):
    log = tmp_path / "RESEARCH-LOG.md"
    log.write_text(_SAMPLE_LOG)
    monkeypatch.setattr(research, "RESEARCH_LOG", log)
    from datetime import date
    class _FrozenDate(date):
        @classmethod
        def today(cls):
            return date(2026, 5, 25)
    monkeypatch.setattr(research, "date", _FrozenDate)

    out = research.cmd_latest_on("NVDA", days=1)
    # 2026-05-23 is too old; only 2026-05-25 should match
    assert "NVDA mentioned" not in out
    assert "NVDA + AAPL covered" in out


def test_cmd_latest_on_returns_friendly_message_when_no_log(monkeypatch, tmp_path):
    monkeypatch.setattr(research, "RESEARCH_LOG", tmp_path / "missing.md")
    out = research.cmd_latest_on("AAPL")
    assert "RESEARCH-LOG.md not found" in out


# ---------------- cmd_ticker_notes ----------------

def test_cmd_ticker_notes_returns_section(monkeypatch, tmp_path):
    notes = tmp_path / "TICKER-NOTES.md"
    notes.write_text(
        "# Ticker Notes\n\n"
        "## AAPL (XLK)\n- Thesis (2026-05-25): cheap.\n\n"
        "## NVDA (XLK)\n- Thesis (2026-05-25): expensive.\n"
    )
    monkeypatch.setattr(research, "TICKER_NOTES", notes)
    out = research.cmd_ticker_notes("nvda")
    assert "## NVDA" in out
    assert "expensive" in out


def test_cmd_ticker_notes_when_missing_file(monkeypatch, tmp_path):
    monkeypatch.setattr(research, "TICKER_NOTES", tmp_path / "nope.md")
    out = research.cmd_ticker_notes("AAPL")
    assert "not yet created" in out


# ---------------- cmd_macro ----------------

def test_cmd_macro_returns_latest_paragraph(monkeypatch, tmp_path):
    macro = tmp_path / "MACRO-FRAMEWORK.md"
    macro.write_text(
        "# Macro Framework\n\n"
        "## 2026-05-23\n\nFirst day macro.\n\n"
        "## 2026-05-24\n\nSecond day macro: yields fell.\n"
    )
    monkeypatch.setattr(research, "MACRO_FRAMEWORK", macro)
    out = research.cmd_macro()
    assert "Second day macro" in out
    assert "First day macro" not in out


def test_cmd_macro_when_empty(monkeypatch, tmp_path):
    macro = tmp_path / "MACRO-FRAMEWORK.md"
    macro.write_text("")
    monkeypatch.setattr(research, "MACRO_FRAMEWORK", macro)
    assert "empty" in research.cmd_macro()


# ---------------- cmd_synthesize wires gemini + news_sources ----------------

def test_cmd_synthesize_invokes_news_then_gemini(monkeypatch):
    captured = {"news_sym": None, "gemini_prompt": None, "smart": False, "synth": False}

    def fake_gather(sym):
        captured["news_sym"] = sym
        return [{"source": "newsapi", "ticker": sym, "title": "T",
                 "url": "https://x", "published": "", "summary": None,
                 "confidence": "high"}]

    def fake_gemini(prompt, *, smart=False, synth=False, temperature=None,
                    no_cache=False, timeout=120):
        captured["gemini_prompt"] = prompt
        captured["smart"] = smart
        captured["synth"] = synth
        return "Bull case: ..."

    monkeypatch.setattr(research.news_sources, "gather", fake_gather)
    monkeypatch.setattr(research, "_run_gemini", fake_gemini)

    out = research.cmd_synthesize("NVDA")
    assert "Bull case" in out
    assert captured["news_sym"] == "NVDA"
    assert captured["smart"] is True
    assert captured["synth"] is True
    assert "NVDA" in captured["gemini_prompt"]


def test_cmd_synthesize_prefixes_low_conf_when_few_records(monkeypatch):
    # < LOW_CONFIDENCE_THRESHOLD raw records → output gets the LOW-CONF prefix
    # so the WhatsApp brief and RESEARCH-LOG header can flag the run.
    monkeypatch.setattr(
        research.news_sources, "gather",
        lambda sym: [{"source": "newsapi", "ticker": sym, "title": "x",
                       "url": "u", "published": "2026-05-26",
                       "confidence": "high", "summary": ""}],
    )
    monkeypatch.setattr(research, "_run_gemini",
                        lambda *a, **kw: "**Bull case:** ...")
    out = research.cmd_synthesize("NVDA")
    assert out.startswith("[LOW-CONFIDENCE:")
    assert "only 1 raw records" in out
    assert "**Bull case:**" in out


def test_cmd_synthesize_no_prefix_when_enough_records(monkeypatch):
    raw = [{"source": "newsapi", "ticker": "NVDA", "title": f"x{i}",
            "url": f"u{i}", "published": "2026-05-26",
            "confidence": "high", "summary": ""}
           for i in range(research.LOW_CONFIDENCE_THRESHOLD + 2)]
    monkeypatch.setattr(research.news_sources, "gather", lambda sym: raw)
    monkeypatch.setattr(research, "_run_gemini",
                        lambda *a, **kw: "**Bull case:** ...")
    out = research.cmd_synthesize("NVDA")
    assert not out.startswith("[LOW-CONFIDENCE:")
    assert out.startswith("**Bull case:**")


def test_cmd_critique_reads_prior_synthesis(monkeypatch, tmp_path):
    log = tmp_path / "RESEARCH-LOG.md"
    log.write_text(
        "## 2026-05-25 — Pre-market\n\n"
        "#### NVDA (XLK, $145)\nBull case: cited\n\n"
    )
    monkeypatch.setattr(research, "RESEARCH_LOG", log)

    captured = {"prompt": ""}
    def fake_gemini(prompt, *, smart=False, **kw):
        captured["prompt"] = prompt
        return "Strongest counter: ..."

    monkeypatch.setattr(research, "_run_gemini", fake_gemini)
    out = research.cmd_critique("NVDA")
    assert "Strongest counter" in out
    # The prior synthesis should appear in the critique prompt
    assert "Bull case: cited" in captured["prompt"]
