#!/usr/bin/env python3
"""Research orchestrator: multi-source gather + Gemini synthesis + retrieval.

Orchestrates the pro-level research pipeline:
  Pass 1: scripts/news_sources.py gather(SYM) → normalized raw records.
  Pass 2: Gemini 2.5 Pro synthesis (bull / bear / disconfirming / catalysts).
  Pass 3: Gemini 2.5 Pro adversarial critique.
  Cross-cutting: persistent retrieval against memory/RESEARCH-LOG.md,
                 memory/TICKER-NOTES.md, memory/MACRO-FRAMEWORK.md.

Subcommands:
  gather SYM [SYM ...]      pass-through to news_sources.gather_many (JSON).
  synthesize SYM            full synthesis pass (markdown to stdout).
  critique SYM              adversarial critique of prior synthesis.
  historical-analog         single Gemini call: macro-setup analog narrative.
  latest-on SYM             last 7 days of SYM mentions from RESEARCH-LOG.
  ticker-notes SYM          section from TICKER-NOTES.md.
  macro                     latest paragraph from MACRO-FRAMEWORK.md.
  digest [YYYY-MM-DD]       compose the WhatsApp brief from today's RESEARCH-LOG.

Gemini calls go through scripts/gemini.sh (handles model routing, cache,
429 fallback). research.py is responsible for building the right prompt and
parsing the response.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import news_sources  # noqa: E402

ROOT = _HERE.parent
MEMORY = ROOT / "memory"
RESEARCH_LOG = MEMORY / "RESEARCH-LOG.md"
TICKER_NOTES = MEMORY / "TICKER-NOTES.md"
MACRO_FRAMEWORK = MEMORY / "MACRO-FRAMEWORK.md"
GEMINI_SH = _HERE / "gemini.sh"


# ---------------------------------------------------------------------------
# Gemini wrapper helpers
# ---------------------------------------------------------------------------

def _run_gemini(query: str, *, smart: bool = False, synth: bool = False,
                temperature: float | None = None, no_cache: bool = False,
                timeout: int = 120) -> str:
    """Invoke scripts/gemini.sh and return the extracted text payload.

    Falls back to raw response body if the expected JSON shape is missing
    (e.g., on Gemini's safety blocks).
    """
    cmd: list[str] = ["bash", str(GEMINI_SH)]
    if smart:
        cmd.append("--smart")
    if synth:
        cmd.append("--synth")
    if temperature is not None:
        cmd.extend(["--temperature", str(temperature)])
    if no_cache:
        cmd.append("--no-cache")
    cmd.append(query)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True,
                                timeout=timeout, check=False)
    except subprocess.TimeoutExpired:
        return "[gemini timeout]"

    if result.returncode == 3:
        return "[gemini: GEMINI_API_KEY not set; falling back]"
    if result.returncode == 4:
        return "[gemini: Pro quota exhausted and Flash fallback also failed]"
    if result.returncode != 0:
        stderr = (result.stderr or "")[-500:]
        return f"[gemini failed rc={result.returncode}: {stderr.strip()}]"

    body = result.stdout.strip()
    if not body:
        return "[gemini: empty response]"
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return body  # raw text

    # Standard Gemini API shape:
    #   {"candidates": [{"content": {"parts": [{"text": "..."}]}}, ...]}
    candidates = payload.get("candidates") or []
    if not candidates:
        # blocked / no content; surface the prompt feedback
        feedback = payload.get("promptFeedback") or {}
        block_reason = feedback.get("blockReason")
        if block_reason:
            return f"[gemini blocked: {block_reason}]"
        return "[gemini: no candidates returned]"

    parts = (candidates[0].get("content") or {}).get("parts") or []
    text_chunks = [p.get("text", "") for p in parts if p.get("text")]
    text = "\n".join(text_chunks).strip()
    return text or "[gemini: empty text]"


# ---------------------------------------------------------------------------
# Synthesis prompts
# ---------------------------------------------------------------------------

_SYNTH_TEMPLATE = """\
You are synthesizing trade-relevant research for {symbol}.

Today: {today}.
Raw source records (JSON list, normalized across NewsAPI / Finnhub / SEC
EDGAR / Google News / Reddit; "confidence" tag is source-based):

```json
{raw_json}
```

Think step by step. First enumerate the strongest 5-7 facts you can verify
against the sources (skip Reddit posts unless they contain primary data).
Then produce the structured answer below, using ONLY facts you've enumerated.
Cite each Bull / Bear bullet with a `[source-domain]` tag (e.g., `[reuters.com]`).
If a Bull or Bear bullet cannot be cited, drop it. Reject anything sourced
only from Reddit unless it links to a primary article.

Output the following sections in markdown, with no preamble:

**Bull case (cited):**
- ...
- ...
- ...

**Bear case (cited):**
- ...
- ...
- ...

**Disconfirming evidence to watch for:**
- ...

**Catalysts ahead (next 14 trading days, dated):**
- YYYY-MM-DD: ...

**One-line takeaway (≤25 words):** ...
"""


_CRITIQUE_TEMPLATE = """\
The following is a synthesis of research for {symbol} produced today
({today}). Be adversarial: find the strongest counter-arguments to the
bull case, expose any unsourced or weakly-sourced claims, and surface the
single risk that would most likely invalidate this trade.

Think step by step, then output in markdown with three sections:

**Strongest counter to the bull case:** one paragraph (≤80 words), cited.
**Weakly-sourced or unsourced claims:** bullet list of any Bull/Bear items
  that fail the citation rule (URL + date).
**Single most-likely invalidator (next 5 trading days):** one sentence,
  with the specific trigger level or event that would activate it.

Synthesis to critique:
---
{synthesis}
---
"""


_HISTORICAL_TEMPLATE = """\
Today's market setup:

{macro_summary}

Find the closest analog in U.S. equity market history within the past 5
years. Be specific about the prior date and which conditions matched
(VIX level, yield curve, sector leadership, macro backdrop). Then describe
what happened in the following 5 / 10 / 20 trading days, with one cited
data point per window. Conclude with one sentence on what differs today
that argues against the analog playing out the same way.

Output as three short paragraphs in markdown:
**Analog:** date + matching conditions (cited).
**What followed:** 5d / 10d / 20d outcomes (cited).
**Why this time might differ:** one sentence on the key divergence.
"""


# ---------------------------------------------------------------------------
# Public subcommand implementations
# ---------------------------------------------------------------------------

def cmd_gather(symbols: list[str]) -> str:
    data = news_sources.gather_many(symbols)
    return json.dumps(data, indent=2)


def cmd_synthesize(symbol: str) -> str:
    raw = news_sources.gather(symbol)
    today = date.today().isoformat()
    # Keep prompt token size reasonable: cap at the 25 most-recent + highest-confidence
    raw_sorted = sorted(
        raw,
        key=lambda r: ({"high": 0, "medium": 1, "low": 2}.get(r.get("confidence", "low"), 3),
                       r.get("published", "")),
        reverse=False,
    )[:25]
    prompt = _SYNTH_TEMPLATE.format(
        symbol=symbol.upper(),
        today=today,
        raw_json=json.dumps(raw_sorted, indent=2),
    )
    return _run_gemini(prompt, smart=True, synth=True, temperature=0.1)


def cmd_critique(symbol: str, synthesis: str | None = None) -> str:
    today = date.today().isoformat()
    if not synthesis:
        synthesis = _read_last_synthesis(symbol) or "(no prior synthesis found)"
    prompt = _CRITIQUE_TEMPLATE.format(
        symbol=symbol.upper(),
        today=today,
        synthesis=synthesis,
    )
    return _run_gemini(prompt, smart=True, synth=True, temperature=0.4)


def cmd_historical_analog(macro_summary: str | None = None) -> str:
    if not macro_summary:
        macro_summary = cmd_macro() or "(no macro snapshot available)"
    prompt = _HISTORICAL_TEMPLATE.format(macro_summary=macro_summary)
    return _run_gemini(prompt, smart=True, synth=True, temperature=0.2)


def cmd_latest_on(symbol: str, *, days: int = 7) -> str:
    """Return the last `days` of RESEARCH-LOG.md sections mentioning `symbol`."""
    if not RESEARCH_LOG.exists():
        return "(RESEARCH-LOG.md not found)"
    text = RESEARCH_LOG.read_text()

    sym = symbol.upper()
    cutoff = date.today() - timedelta(days=days)
    sections = _split_research_log(text)
    out: list[str] = []
    for section_date, body in sections:
        if section_date and section_date < cutoff:
            continue
        if re.search(rf"\b{re.escape(sym)}\b", body, re.IGNORECASE):
            out.append(body)
    if not out:
        return f"(no mentions of {sym} in the last {days} days)"
    return ("\n\n---\n\n".join(out)).strip()


def cmd_ticker_notes(symbol: str) -> str:
    if not TICKER_NOTES.exists():
        return f"(TICKER-NOTES.md not yet created)"
    sym = symbol.upper()
    text = TICKER_NOTES.read_text()
    section = _extract_h2_section(text, sym)
    return section or f"(no section for {sym} in TICKER-NOTES.md)"


def cmd_macro() -> str:
    if not MACRO_FRAMEWORK.exists():
        return "(MACRO-FRAMEWORK.md not yet created)"
    text = MACRO_FRAMEWORK.read_text().strip()
    if not text:
        return "(MACRO-FRAMEWORK.md is empty)"
    sections = _split_research_log(text)
    if sections:
        _, body = sections[-1]
        return body.strip()
    return text


def cmd_digest(target_date: str | None = None) -> str:
    """Compose a WhatsApp-shaped brief from the chosen day's RESEARCH-LOG entry."""
    if not RESEARCH_LOG.exists():
        return "(RESEARCH-LOG.md not found)"
    target = target_date or date.today().isoformat()
    text = RESEARCH_LOG.read_text()
    sections = _split_research_log(text)
    chosen: str | None = None
    for section_date, body in sections:
        if section_date and section_date.isoformat() == target:
            chosen = body
            break
    if chosen is None:
        return f"(no RESEARCH-LOG entry for {target})"

    # Pull the headline fields with simple regex over the section body.
    regime_match = re.search(r"\*\*Regime:\*\*\s*([^\n]+)", chosen)
    decision_match = re.search(r"###?\s*Decision\b[\s\S]{0,2000}", chosen)

    # Best-effort: extract per-ticker idea blocks (#### SYM lines).
    idea_blocks = re.findall(r"####\s+([A-Z]{1,5})\b[\s\S]{0,400}?(?=\n####|\n###|\n##|\Z)",
                              chosen)

    lines: list[str] = []
    lines.append(f"PRE-MARKET • {target} • {regime_match.group(1).strip() if regime_match else 'Regime ?'}")
    lines.append("─" * 28)
    if idea_blocks:
        lines.append(f"Top ideas ({len(idea_blocks)}):")
        for sym in idea_blocks[:3]:
            lines.append(f" • {sym}")
    if decision_match:
        # First non-empty line after the Decision header
        body_after = decision_match.group(0).split("\n", 1)[1].strip()
        first = next((ln for ln in body_after.split("\n") if ln.strip()), "")
        if first:
            lines.append(f"Decision: {first.strip().lstrip('-').strip()}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Parsing helpers (pure)
# ---------------------------------------------------------------------------

_H2_DATE_RE = re.compile(r"^##\s+(\d{4}-\d{2}-\d{2})\b", re.MULTILINE)


def _split_research_log(text: str) -> list[tuple[date | None, str]]:
    """Split a markdown file into (date, section_body) tuples on `## YYYY-MM-DD` headers.

    Sections without a parseable date are returned with date=None.
    """
    indices: list[tuple[int, date | None]] = []
    for m in _H2_DATE_RE.finditer(text):
        try:
            d = date.fromisoformat(m.group(1))
        except ValueError:
            d = None
        indices.append((m.start(), d))
    if not indices:
        return []
    sections: list[tuple[date | None, str]] = []
    for i, (start, d) in enumerate(indices):
        end = indices[i + 1][0] if i + 1 < len(indices) else len(text)
        sections.append((d, text[start:end].strip()))
    return sections


def _extract_h2_section(text: str, header_starts_with: str) -> str | None:
    """Return the H2 section whose header begins with `header_starts_with`."""
    pat = re.compile(rf"(?ms)^##\s+{re.escape(header_starts_with)}\b.*?(?=^##\s|\Z)")
    m = pat.search(text)
    return m.group(0).strip() if m else None


def _read_last_synthesis(symbol: str) -> str | None:
    if not RESEARCH_LOG.exists():
        return None
    text = RESEARCH_LOG.read_text()
    sym = symbol.upper()
    # Find the most recent `#### SYM (...)` block in the file.
    pat = re.compile(rf"(?ms)^####\s+{re.escape(sym)}\b.*?(?=^####|\Z)")
    matches = list(pat.finditer(text))
    if not matches:
        return None
    return matches[-1].group(0).strip()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    cmd = sys.argv[1]
    args = sys.argv[2:]

    if cmd == "gather":
        if not args:
            print("usage: gather SYM [SYM ...]", file=sys.stderr)
            return 2
        print(cmd_gather(args))
    elif cmd == "synthesize":
        if not args:
            print("usage: synthesize SYM", file=sys.stderr)
            return 2
        print(cmd_synthesize(args[0]))
    elif cmd == "critique":
        if not args:
            print("usage: critique SYM [optional: --synthesis-file PATH]", file=sys.stderr)
            return 2
        synthesis = None
        if len(args) >= 3 and args[1] == "--synthesis-file":
            synthesis = Path(args[2]).read_text()
        print(cmd_critique(args[0], synthesis))
    elif cmd == "historical-analog":
        macro = sys.stdin.read() if not sys.stdin.isatty() else None
        print(cmd_historical_analog(macro))
    elif cmd == "latest-on":
        if not args:
            print("usage: latest-on SYM [days]", file=sys.stderr)
            return 2
        days = int(args[1]) if len(args) > 1 else 7
        print(cmd_latest_on(args[0], days=days))
    elif cmd == "ticker-notes":
        if not args:
            print("usage: ticker-notes SYM", file=sys.stderr)
            return 2
        print(cmd_ticker_notes(args[0]))
    elif cmd == "macro":
        print(cmd_macro())
    elif cmd == "digest":
        target = args[0] if args else None
        print(cmd_digest(target))
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
