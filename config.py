"""
Configuration loader for UK Property CLI.

Reads preferences.json and provides defaults when not available.
All tools should import from here instead of hardcoding values.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).parent
PREFERENCES_FILE = SCRIPT_DIR / "preferences.json"

# Sensible defaults when no preferences.json exists
DEFAULTS = {
    "user": {
        "name": "Property Searcher",
        "location": "Edinburgh",
    },
    "search": {
        "min_beds": 4,
        "max_beds": None,
        "min_price": None,
        "max_price": 600000,
        "property_types": ["house", "detached", "semi-detached"],
    },
    "areas": {
        "desired": [],
        "excluded": [
            "Moredun", "Niddrie", "Wester Hailes", "Sighthill",
            "Muirhouse", "Pilton", "Granton",
        ],
        "premium": [],
    },
    "scoring": {
        "area_weights": {"premium": 30, "excellent": 25, "good": 20},
        "price_ideal_min": 400000,
        "price_ideal_max": 550000,
        "prefer_images": True,
        "prefer_multiple_portals": True,
    },
    "deduplication": {
        "enabled": True,
        "threshold": 0.85,
    },
    "briefing": {
        "enabled": True,
        "schedule": "0 9 * * *",
        "include_price_changes": True,
        "include_new_only": False,
        "max_results": 10,
    },
}

# Rightmove region IDs for common UK cities
RIGHTMOVE_REGIONS = {
    "edinburgh": "REGION%5E550",
    "glasgow": "REGION%5E798",
    "aberdeen": "REGION%5E103",
    "dundee": "REGION%5E461",
    "manchester": "REGION%5E904",
    "london": "REGION%5E87490",
    "birmingham": "REGION%5E162",
    "leeds": "REGION%5E787",
    "bristol": "REGION%5E219",
    "liverpool": "REGION%5E821",
    "sheffield": "REGION%5E1195",
    "cardiff": "REGION%5E274",
    "belfast": "REGION%5E148",
    "newcastle": "REGION%5E992",
    "nottingham": "REGION%5E1019",
}

# ESPC only covers Edinburgh and Lothians
ESPC_LOCATIONS = {
    "edinburgh": "edinburgh",
}

# Zoopla uses city names in URLs
ZOOPLA_LOCATIONS = {
    "edinburgh": "edinburgh",
    "glasgow": "glasgow",
    "aberdeen": "aberdeen",
    "manchester": "manchester",
    "london": "london",
    "birmingham": "birmingham",
    "leeds": "leeds",
    "bristol": "bristol",
    "liverpool": "liverpool",
}


_config_cache: Optional[Dict[str, Any]] = None


def load_config() -> Dict[str, Any]:
    """Load preferences from preferences.json, falling back to defaults."""
    global _config_cache
    if _config_cache is not None:
        return _config_cache

    config = _deep_copy(DEFAULTS)

    if PREFERENCES_FILE.exists():
        try:
            with open(PREFERENCES_FILE) as f:
                user_prefs = json.load(f)
            _merge_dict(config, user_prefs)
        except (json.JSONDecodeError, IOError):
            pass  # Use defaults on error

    _config_cache = config
    return config


def get_excluded_areas() -> List[str]:
    """Get excluded areas from config."""
    config = load_config()
    return config.get("areas", {}).get("excluded", DEFAULTS["areas"]["excluded"])


def get_desired_areas() -> List[str]:
    """Get desired areas from config."""
    config = load_config()
    return config.get("areas", {}).get("desired", [])


def get_premium_areas() -> List[str]:
    """Get premium areas from config."""
    config = load_config()
    return config.get("areas", {}).get("premium", [])


def get_location() -> str:
    """Get configured location (lowercase)."""
    config = load_config()
    return config.get("user", {}).get("location", "Edinburgh").lower()


def get_search_config() -> Dict[str, Any]:
    """Get search criteria from config."""
    config = load_config()
    return config.get("search", DEFAULTS["search"])


def get_scoring_config() -> Dict[str, Any]:
    """Get scoring config."""
    config = load_config()
    return config.get("scoring", DEFAULTS["scoring"])


def get_dedup_threshold() -> float:
    """Get deduplication similarity threshold."""
    config = load_config()
    return config.get("deduplication", {}).get("threshold", 0.85)


def get_rightmove_region() -> Optional[str]:
    """Get Rightmove region identifier for configured location."""
    location = get_location()
    return RIGHTMOVE_REGIONS.get(location)


def get_zoopla_location() -> Optional[str]:
    """Get Zoopla location slug for configured location."""
    location = get_location()
    return ZOOPLA_LOCATIONS.get(location)


def get_espc_location() -> Optional[str]:
    """Get ESPC location slug (Edinburgh only)."""
    location = get_location()
    return ESPC_LOCATIONS.get(location)


def _deep_copy(d: Dict) -> Dict:
    """Simple deep copy for JSON-compatible dicts."""
    return json.loads(json.dumps(d))


def _merge_dict(base: Dict, override: Dict) -> None:
    """Recursively merge override into base (mutates base)."""
    for key, value in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(value, dict):
            _merge_dict(base[key], value)
        else:
            base[key] = value
