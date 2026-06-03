#!/usr/bin/env python3
"""
Converts sector-analyst JSON (tradermonty format) to the format expected
by exposure-coach's calculate_exposure.py --sector flag.

exposure-coach needs top-level keys: leadership, dispersion, sector_score
"""
import json
import sys

data = json.load(open(sys.argv[1]))

groups = data.get("groups", {})
ranking = data.get("ranking", [])

# Leadership = top-ranked sector by uptrend ratio
leadership = ranking[0]["sector"] if ranking else "unknown"

# Dispersion = spread between cyclical and defensive avg ratios (0–1 scale)
dispersion = abs(groups.get("difference", 0))

# Map sector-analyst score (0–100) directly if present
sector_score = groups.get("score")

out = {
    "leadership": leadership,
    "dispersion": round(dispersion, 4),
    "sector_score": sector_score,
    "regime": groups.get("regime", "mixed"),
    "cycle_phase": data.get("cycle_phase", {}).get("phase", "unknown"),
}

print(json.dumps(out))
