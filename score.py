#!/usr/bin/env python3
"""
Score and rank properties based on preferences.

Usage:
    python3 score.py <properties.json>

Reads scoring weights from preferences.json and ranks properties
by a composite score based on area, price, features, and portal coverage.
"""

import json
import sys
from typing import Any, Dict, List

from config import get_desired_areas, get_premium_areas, get_scoring_config


def score_property(prop: Dict[str, Any], scoring: Dict[str, Any], desired: List[str], premium: List[str]) -> int:
    """
    Score a single property. Higher is better.

    Scoring factors:
    - Area quality (premium > desired > other)
    - Price proximity to ideal range
    - Has images
    - Listed on multiple portals
    - Bedroom count
    """
    score = 0
    weights = scoring.get("area_weights", {})
    address = (prop.get("address", "") + " " + prop.get("postcode", "")).lower()

    # Area scoring
    premium_lower = [a.lower() for a in premium]
    desired_lower = [a.lower() for a in desired]

    if any(a in address for a in premium_lower):
        score += weights.get("premium", 30)
    elif any(a in address for a in desired_lower):
        score += weights.get("good", 20)

    # Price scoring (closer to ideal range = higher score)
    price = prop.get("price", 0)
    ideal_min = scoring.get("price_ideal_min", 400000)
    ideal_max = scoring.get("price_ideal_max", 550000)

    if price > 0:
        if ideal_min <= price <= ideal_max:
            score += 25  # Perfect price range
        elif price < ideal_min:
            # Below ideal - still good, score proportionally
            ratio = price / ideal_min if ideal_min > 0 else 0
            score += int(15 * ratio)
        else:
            # Above ideal - penalize proportionally
            overshoot = (price - ideal_max) / ideal_max if ideal_max > 0 else 0
            score += max(0, int(15 * (1 - overshoot)))

    # Image bonus
    if scoring.get("prefer_images", True):
        if prop.get("images"):
            score += 5
            if len(prop.get("images", [])) >= 3:
                score += 5  # Extra for multiple images

    # Multi-portal bonus
    if scoring.get("prefer_multiple_portals", True):
        portals = prop.get("portals", [])
        if len(portals) > 1:
            score += 10 * (len(portals) - 1)

    # Bedroom bonus (more beds in a family home = better)
    beds = prop.get("beds", 0)
    if beds >= 5:
        score += 10
    elif beds >= 4:
        score += 5

    return score


def score_properties(properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Score and sort all properties."""
    scoring = get_scoring_config()
    desired = get_desired_areas()
    premium = get_premium_areas()

    scored = []
    for prop in properties:
        prop_copy = prop.copy()
        prop_copy["score"] = score_property(prop, scoring, desired, premium)
        scored.append(prop_copy)

    scored.sort(key=lambda p: p["score"], reverse=True)
    return scored


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 score.py <properties.json>")
        print("\nExample:")
        print("  python3 score.py cache/all.json")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file) as f:
            data = json.load(f)
            properties = data.get("properties", data) if isinstance(data, dict) else data
    except Exception as e:
        print(f"Error loading {input_file}: {e}", file=sys.stderr)
        sys.exit(1)

    scored = score_properties(properties)

    scores = [p["score"] for p in scored]
    result = {
        "scoring": {
            "count": len(scored),
            "max_score": max(scores) if scores else 0,
            "min_score": min(scores) if scores else 0,
            "avg_score": round(sum(scores) / len(scores), 1) if scores else 0,
        },
        "properties": scored,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
