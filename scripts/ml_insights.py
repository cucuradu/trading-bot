#!/usr/bin/env python3
"""Hybrid ML regime hook — read ml-insights.json with fallback to scripts/regime.py.

The local Ubuntu PC (RTX 5060 Ti) writes ml-insights.json overnight per the
contract in docs/ml-insights-schema.md. This reader is the cloud-side consumer:

  1. Look for ml-insights.json under docs/ (current publisher target).
     If absent, fall back to repo root (original contract location).
  2. Validate freshness (generated_at < 24h old, UTC)
  3. Validate schema (required market.* fields + enum values)
  4. Return resolved regime + source ("ml" | "rule_fallback")
  5. On any failure, fall back to scripts/regime.py and record the reason

Cloud loop NEVER writes ml-insights.json. It is committed by the local pipeline.

Usage:
  python scripts/ml_insights.py resolve            # JSON: best-available regime
  python scripts/ml_insights.py resolve --no-screener  # skip local screener fallback
  python scripts/ml_insights.py surface            # one-line RESEARCH-LOG advisory of UNUSED fields (read-only)
  python scripts/ml_insights.py read-only          # JSON: file contents if valid, else error
  python scripts/ml_insights.py validate FILE      # JSON: validation report for a specific path
"""
from __future__ import annotations

import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
# Publisher writes to docs/ today. Repo root is the original contract
# location and is honored as a fallback so a producer can choose either.
_ML_FILE_DOCS = ROOT / "docs" / "ml-insights.json"
_ML_FILE_ROOT = ROOT / "ml-insights.json"


def _resolve_ml_file() -> Path:
    """Return the on-disk ml-insights.json path, preferring docs/."""
    if _ML_FILE_DOCS.exists():
        return _ML_FILE_DOCS
    return _ML_FILE_ROOT


# Back-compat alias — older callers and tests import ML_FILE directly. This
# resolves at import-time, but read_and_validate() re-resolves on every call
# so dynamic changes are honored at runtime.
ML_FILE = _resolve_ml_file()
FRESHNESS_HOURS = 24

VALID_MARKET_REGIMES = {"Bull", "Neutral", "Caution", "Defensive"}
VALID_SECTOR_REGIMES = {"Trend", "Choppy", "Bear"}


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _parse_iso_utc(s: str) -> datetime | None:
    """Best-effort ISO 8601 parse; returns None if it can't be made UTC-aware."""
    if not isinstance(s, str):
        return None
    # Python's fromisoformat is strict but handles `2026-05-26T05:30:00+00:00`.
    # The contract uses `Z` suffix, so normalize.
    try:
        normalized = s.strip().replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if dt.tzinfo is None:
        # Assume UTC if naive — schema requires Z but be forgiving.
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def validate(payload: dict, *, now: datetime | None = None) -> dict:
    """Validate an ml-insights payload against the schema contract.

    Returns:
      {
        "ok": True | False,
        "reason": "..." or None,
        "fields": {parsed subset suitable for caller use}
      }

    Validation rules (mirror docs/ml-insights-schema.md):
      - generated_at exists, parseable, < 24h old
      - market.regime in VALID_MARKET_REGIMES
      - market.deployment_target in [0, 1]
      - market.trade_slots clamped to [0, 3] (clamp, not reject)
      - sectors[*].regime in VALID_SECTOR_REGIMES if present (else skipped)
      - Unknown fields tolerated (forward-compat)
    """
    now = now or _now_utc()

    if not isinstance(payload, dict):
        return {"ok": False, "reason": "payload is not a JSON object", "fields": None}

    gen_raw = payload.get("generated_at")
    gen_dt = _parse_iso_utc(gen_raw) if gen_raw is not None else None
    if gen_dt is None:
        return {"ok": False, "reason": "generated_at missing or unparseable", "fields": None}

    age = now - gen_dt
    if age > timedelta(hours=FRESHNESS_HOURS):
        return {
            "ok": False,
            "reason": f"stale: generated_at is {age.total_seconds() / 3600:.1f}h old (> {FRESHNESS_HOURS}h)",
            "fields": None,
        }
    if age < timedelta(seconds=-300):  # >5 min in the future = clock skew, suspicious
        return {
            "ok": False,
            "reason": f"future-dated: generated_at is {-age.total_seconds():.0f}s ahead",
            "fields": None,
        }

    market = payload.get("market")
    if not isinstance(market, dict):
        return {"ok": False, "reason": "market block missing or not an object", "fields": None}

    regime = market.get("regime")
    if regime not in VALID_MARKET_REGIMES:
        return {
            "ok": False,
            "reason": f"market.regime '{regime}' not in {sorted(VALID_MARKET_REGIMES)}",
            "fields": None,
        }

    dep_target = market.get("deployment_target")
    if not isinstance(dep_target, (int, float)) or not (0.0 <= float(dep_target) <= 1.0):
        return {
            "ok": False,
            "reason": f"market.deployment_target {dep_target!r} not in [0, 1]",
            "fields": None,
        }

    trade_slots_raw = market.get("trade_slots")
    if not isinstance(trade_slots_raw, (int, float)):
        return {"ok": False, "reason": "market.trade_slots missing or not numeric", "fields": None}
    trade_slots = max(0, min(3, int(trade_slots_raw)))  # clamp per schema

    breadth_divergence_raw = market.get("breadth_divergence")
    breadth_divergence = (
        breadth_divergence_raw if isinstance(breadth_divergence_raw, bool) else None
    )

    systemic_fragility_raw = market.get("systemic_fragility")
    if systemic_fragility_raw is None:
        systemic_fragility = None
    elif not isinstance(systemic_fragility_raw, (int, float)) or isinstance(systemic_fragility_raw, bool) \
            or not (0.0 <= float(systemic_fragility_raw) <= 1.0):
        return {
            "ok": False,
            "reason": f"market.systemic_fragility {systemic_fragility_raw!r} not in [0, 1]",
            "fields": None,
        }
    else:
        systemic_fragility = float(systemic_fragility_raw)

    sectors_raw = payload.get("sectors") or {}
    sectors: dict[str, dict] = {}
    if isinstance(sectors_raw, dict):
        for sym, info in sectors_raw.items():
            if not isinstance(info, dict):
                continue
            sec_regime = info.get("regime")
            if sec_regime in VALID_SECTOR_REGIMES:
                sectors[sym] = {
                    "regime": sec_regime,
                    "score": info.get("score"),
                }

    universe_ranking_raw = payload.get("universe_ranking") or []
    universe_ranking: list[dict] = []
    if isinstance(universe_ranking_raw, list):
        for entry in universe_ranking_raw:
            if not isinstance(entry, dict):
                continue
            sym = entry.get("symbol")
            score = entry.get("ml_score")
            if isinstance(sym, str) and isinstance(score, (int, float)) and not isinstance(score, bool):
                universe_ranking.append({"symbol": sym, "ml_score": float(score)})

    universe_weights_raw = payload.get("universe_weights") or {}
    universe_weights: dict[str, float] = {}
    if isinstance(universe_weights_raw, dict):
        for sym, weight in universe_weights_raw.items():
            if not isinstance(sym, str):
                continue
            if not isinstance(weight, (int, float)) or isinstance(weight, bool):
                continue
            w = float(weight)
            if 0.0 <= w <= 1.0:
                universe_weights[sym] = w

    return {
        "ok": True,
        "reason": None,
        "fields": {
            "generated_at": gen_dt.isoformat(),
            "age_hours": round(age.total_seconds() / 3600, 2),
            "model_version": payload.get("model_version"),
            "market": {
                "regime": regime,
                "deployment_target": float(dep_target),
                "trade_slots": trade_slots,
                "confidence": market.get("confidence"),
                "persistence_bars": market.get("persistence_bars"),
                "breadth_divergence": breadth_divergence,
                "systemic_fragility": systemic_fragility,
            },
            "sectors": sectors,
            "universe_ranking": universe_ranking,
            "universe_weights": universe_weights,
        },
    }


def read_and_validate(path: Path | None = None, *, now: datetime | None = None) -> dict:
    """Load + validate the on-disk artifact.

    Returns the same shape as validate(), with an extra `path` field.
    """
    path = path or ML_FILE
    if not path.exists():
        return {"ok": False, "reason": "ml-insights.json not found", "fields": None, "path": str(path)}
    try:
        raw = path.read_text()
        payload = json.loads(raw)
    except json.JSONDecodeError as e:
        return {"ok": False, "reason": f"malformed JSON: {e}", "fields": None, "path": str(path)}
    except OSError as e:
        return {"ok": False, "reason": f"read error: {e}", "fields": None, "path": str(path)}

    result = validate(payload, now=now)
    result["path"] = str(path)
    return result


def resolve(*, now: datetime | None = None, enable_local_screener: bool = True) -> dict:
    """Best-available regime: ML if fresh + valid, else rule-based fallback.

    When the ML payload is rejected and `enable_local_screener=True`, the
    rule-based fallback also calls `scripts/screener.py:rank_universe()` to
    populate `universe_ranking` (drop-in schema-compatible). On any screener
    failure the ranking stays empty — `resolve()` never raises.

    Returns:
      {
        "source": "ml" | "rule_fallback",
        "fallback_reason": "..." or None,
        "market": {regime, deployment_target, trade_slots, ...},
        "sectors": {SYM: {regime, score}, ...},
        "universe_ranking": [{symbol, ml_score}, ...],
        "universe_weights": {SYM: weight, ...},
        "ml_metadata": {generated_at, model_version, age_hours} or None,
      }
    """
    validated = read_and_validate(now=now)
    if validated["ok"]:
        fields = validated["fields"]
        return {
            "source": "ml",
            "fallback_reason": None,
            "market": fields["market"],
            "sectors": fields["sectors"],
            "universe_ranking": fields["universe_ranking"],
            "universe_weights": fields["universe_weights"],
            "ml_metadata": {
                "generated_at": fields["generated_at"],
                "model_version": fields["model_version"],
                "age_hours": fields["age_hours"],
            },
        }

    # Fallback to scripts/regime.py
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import regime as rb  # noqa: E402

    market = rb.market_regime()
    sectors_full = rb.sector_regimes()["sectors"]
    sectors = {
        sym: {"regime": info.get("regime"), "score": info.get("score")}
        for sym, info in sectors_full.items()
        if info.get("regime") is not None
    }

    # Local-screener fallback ranking (informational; not part of the producer
    # contract — see docs/ml-insights-schema.md appendix). When the publisher
    # is offline, this prevents `universe_ranking` from being empty, which
    # otherwise leaves pre-market candidate selection without signal.
    universe_ranking: list[dict] = []
    ml_metadata: dict | None = None
    if enable_local_screener:
        try:
            import screener  # noqa: E402

            # Auto-detect binary macro-event days → use defensive weights.
            macro_event_today = False
            try:
                import trading_calendar as tc  # noqa: E402
                macro_event_today = bool(tc.pre_macro_event_check(date.today()).get("within_24h"))
            except Exception:
                # trading_calendar absent or shape changed — default to normal weights
                pass

            ranked = screener.rank_universe(
                sector_regimes=sectors,
                macro_event=macro_event_today,
                enable_catalyst_fetch=True,
            )
            survivors = [r for r in ranked if r.get("drop_reason") is None]
            universe_ranking = [
                {"symbol": r["symbol"], "ml_score": r["ml_score"]}
                for r in survivors
            ]
            weights_used = (
                screener.MACRO_DAY_FACTOR_WEIGHTS if macro_event_today
                else screener.FACTOR_WEIGHTS
            )
            ml_metadata = {
                "source_detail": "local_screener_v1",
                "macro_event_weighting": macro_event_today,
                "factor_weights": weights_used,
            }
        except Exception as e:  # never crash resolve() because screener failed
            print(f"[ml_insights] local screener fallback failed: {e}", file=sys.stderr)

    # G5.3 — when the local screener fallback succeeded AND the ML rejection
    # was just "stale" or "not found", collapse the verbose reason to a stable
    # terse string. Preserve "malformed JSON" / schema-validation reasons —
    # those are real signal worth logging. Keeps routines from pasting a noisy
    # 74h-stale message into every RESEARCH-LOG entry while the local PC
    # producer is offline.
    fallback_reason = validated["reason"]
    if (
        universe_ranking
        and ml_metadata is not None
        and fallback_reason
        and ("stale" in fallback_reason or "not found" in fallback_reason)
    ):
        fallback_reason = "ml unavailable; using local_screener_v1"

    return {
        "source": "rule_fallback",
        "fallback_reason": fallback_reason,
        "market": {
            "regime": market["regime"],
            "deployment_target": market["deployment_target"],
            "trade_slots": market["trade_slots"],
            "persistence_bars": market["persistence_bars"],
            "stable": market["stable"],
            "breadth_divergence": None,
            "systemic_fragility": None,
        },
        "sectors": sectors,
        "universe_ranking": universe_ranking,
        "universe_weights": {},
        "ml_metadata": ml_metadata,
    }


def format_advisory_signals(payload: dict) -> str:
    """One-line, greppable summary of the ML fields the trading loop does NOT
    act on during the forward-test phase: crash_risk, systemic_fragility, macro
    conditions, GARCH vol, inverse-vol weights, and out-of-sample rank IC.

    Pure (no IO, no freshness check — the caller gates on validate()). Returns
    "" when the payload carries none of the advisory blocks. Every field is
    optional and read defensively: the producer adds these incrementally, so a
    missing block must drop its segment, never raise.
    """
    if not isinstance(payload, dict):
        return ""

    segs: list[str] = []

    crash = payload.get("crash_risk")
    if isinstance(crash, dict) and isinstance(crash.get("score"), (int, float)) \
            and not isinstance(crash.get("score"), bool):
        elevated = bool(crash.get("elevated"))
        seg = f"crash={float(crash['score']):.2f} {'ELEVATED' if elevated else 'calm'}"
        reasons = crash.get("reasons")
        if elevated and isinstance(reasons, list) and reasons:
            seg += f" ({', '.join(str(r) for r in reasons[:3])})"
        segs.append(seg)

    market = payload.get("market")
    if isinstance(market, dict):
        frag = market.get("systemic_fragility")
        if isinstance(frag, (int, float)) and not isinstance(frag, bool):
            segs.append(f"fragility={float(frag):.2f}")

    macro = payload.get("macro")
    if isinstance(macro, dict) and macro.get("available"):
        bits = []
        if isinstance(macro.get("macro_regime"), str):
            bits.append(macro["macro_regime"])
        extra = []
        if isinstance(macro.get("hy_oas"), (int, float)) and not isinstance(macro.get("hy_oas"), bool):
            extra.append(f"HY-OAS {float(macro['hy_oas']):.2f}%")
        if isinstance(macro.get("nfci"), (int, float)) and not isinstance(macro.get("nfci"), bool):
            extra.append(f"NFCI {float(macro['nfci']):+.2f}")
        if "curve_inverted" in macro:
            extra.append("curve INVERTED" if macro.get("curve_inverted") else "curve normal")
        if extra:
            bits.append(f"({', '.join(extra)})")
        if bits:
            segs.append("macro=" + " ".join(bits))

    vol = payload.get("volatility")
    if isinstance(vol, dict):
        bits = []
        if isinstance(vol.get("garch_1d_forecast_pct"), (int, float)) and not isinstance(vol.get("garch_1d_forecast_pct"), bool):
            bits.append(f"GARCH1d {float(vol['garch_1d_forecast_pct']):.1f}%")
        if isinstance(vol.get("vix"), (int, float)) and not isinstance(vol.get("vix"), bool):
            bits.append(f"VIX {float(vol['vix']):.1f}")
        if isinstance(vol.get("vvix"), (int, float)) and not isinstance(vol.get("vvix"), bool):
            bits.append(f"VVIX {float(vol['vvix']):.0f}")
        if isinstance(vol.get("vix_implied_term_structure"), str):
            bits.append(str(vol["vix_implied_term_structure"]))
        if bits:
            segs.append("vol=" + " ".join(bits))

    rq = payload.get("ranking_quality")
    if isinstance(rq, dict) and isinstance(rq.get("oof_rank_ic"), (int, float)) \
            and not isinstance(rq.get("oof_rank_ic"), bool):
        segs.append(f"rankIC(oof)={float(rq['oof_rank_ic']):.3f}")

    weights = payload.get("universe_weights")
    if isinstance(weights, dict) and weights:
        parts = [
            f"{sym} {float(w):.2f}"
            for sym, w in weights.items()
            if isinstance(w, (int, float)) and not isinstance(w, bool)
        ]
        if parts:
            segs.append("wts " + "/".join(parts))

    if not segs:
        return ""
    return ("**ML signals (advisory — surfaced for post-phase analysis, "
            "not acted on):** " + " | ".join(segs))


def surface(*, now: datetime | None = None) -> str:
    """RESEARCH-LOG advisory line for the unused ML fields, gated on freshness.

    Read-only: never influences regime/sizing/gates. Returns an `n/a (<reason>)`
    line (not an exception) when the file is missing, unreadable, or stale, so
    the pre-market routine can paste the output deterministically either way.
    """
    path = _resolve_ml_file()
    if not path.exists():
        return "**ML signals:** n/a (ml-insights.json not found)"
    try:
        payload = json.loads(path.read_text())
    except (json.JSONDecodeError, OSError) as e:
        return f"**ML signals:** n/a (unreadable: {e})"
    v = validate(payload, now=now)
    if not v["ok"]:
        return f"**ML signals:** n/a ({v['reason']})"
    return format_advisory_signals(payload) or "**ML signals:** (payload carries no advisory fields)"


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        return 1

    cmd = sys.argv[1]
    if cmd == "resolve":
        enable_screener = "--no-screener" not in sys.argv[2:]
        print(json.dumps(resolve(enable_local_screener=enable_screener), indent=2))
    elif cmd == "surface":
        print(surface())
    elif cmd == "read-only":
        result = read_and_validate()
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 3
    elif cmd == "validate":
        if len(sys.argv) < 3:
            print("usage: validate FILE", file=sys.stderr)
            return 2
        result = read_and_validate(Path(sys.argv[2]))
        print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 3
    else:
        print(f"unknown command: {cmd}", file=sys.stderr)
        print(__doc__, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
