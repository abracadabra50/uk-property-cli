#!/usr/bin/env python3
"""
Generate comprehensive property briefing.

Automatically:
- Fetches from all portals
- Deduplicates (AUTOMATIC - no separate step needed)
- Filters by preferences
- Compares with yesterday
- Scores and ranks

Usage:
    python3 briefing.py [--config preferences.json]
    
Or override specific settings:
    python3 briefing.py --min-beds 3 --max-price 500000
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
import argparse


SCRIPT_DIR = Path(__file__).parent
CACHE_DIR = SCRIPT_DIR / 'cache'
DEFAULT_CONFIG = SCRIPT_DIR / 'preferences.json'


def load_preferences(config_file: Path = None) -> dict:
    """Load user preferences."""
    config_path = config_file or DEFAULT_CONFIG
    
    if not config_path.exists():
        print(f"⚠️  No preferences found at {config_path}", file=sys.stderr)
        print(f"Run: python3 setup.py to configure preferences", file=sys.stderr)
        return {}
    
    with open(config_path) as f:
        return json.load(f)


def fetch_all_portals(min_beds: int = 4) -> dict:
    """Fetch from all portals and combine."""
    print("Fetching from all portals...", file=sys.stderr)
    
    results = {}
    
    # ESPC
    try:
        result = subprocess.run(
            ['python3', str(SCRIPT_DIR / 'parsers/espc.py'), str(min_beds)],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            results['espc'] = json.loads(result.stdout)
    except Exception as e:
        print(f"ESPC failed: {e}", file=sys.stderr)
    
    # Rightmove
    try:
        result = subprocess.run(
            ['python3', str(SCRIPT_DIR / 'parsers/rightmove.py'), str(min_beds)],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            results['rightmove'] = json.loads(result.stdout)
    except Exception as e:
        print(f"Rightmove failed: {e}", file=sys.stderr)
    
    # Zoopla
    try:
        result = subprocess.run(
            ['python3', str(SCRIPT_DIR / 'parsers/zoopla.py'), str(min_beds)],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            results['zoopla'] = json.loads(result.stdout)
    except Exception as e:
        print(f"Zoopla failed: {e}", file=sys.stderr)
    
    # Combine
    all_properties = []
    for portal, data in results.items():
        all_properties.extend(data.get('properties', []))
    
    return {
        'portals': results,
        'all_properties': all_properties,
        'total_count': len(all_properties)
    }


def deduplicate_automatic(properties: list, threshold: float = 0.85) -> dict:
    """
    AUTOMATIC deduplication - no separate step needed.
    
    This is built into the briefing workflow.
    Users don't need to call dedupe.py separately.
    """
    from dedupe import deduplicate as dedupe_func
    
    print(f"Deduplicating {len(properties)} properties...", file=sys.stderr)
    
    unique = dedupe_func(properties, threshold)
    
    result = {
        'original_count': len(properties),
        'unique_count': len(unique),
        'duplicate_count': len(properties) - len(unique),
        'properties': unique
    }
    
    print(f"  ✓ {result['duplicate_count']} duplicates removed", file=sys.stderr)
    
    return result


def compare_with_yesterday(today_properties: list) -> dict:
    """Compare with yesterday's snapshot."""
    yesterday_file = CACHE_DIR / f"{(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}.json"
    
    if not yesterday_file.exists():
        return {
            'has_comparison': False,
            'new_listings': today_properties,
            'price_changes': [],
            'removed_listings': []
        }
    
    with open(yesterday_file) as f:
        yesterday_data = json.load(f)
        yesterday = yesterday_data.get('properties', yesterday_data)
    
    from compare import compare_snapshots
    comparison = compare_snapshots(yesterday, today_properties)
    comparison['has_comparison'] = True
    
    return comparison


def filter_by_preferences(properties: list, prefs: dict) -> dict:
    """Filter using preferences."""
    from filter import filter_properties as filter_func
    
    search = prefs.get('search', {})
    areas = prefs.get('areas', {})
    
    filtered = filter_func(
        properties,
        areas=areas.get('desired'),
        exclude=areas.get('excluded'),
        min_price=search.get('min_price'),
        max_price=search.get('max_price'),
        min_beds=search.get('min_beds')
    )
    
    return {
        'original_count': len(properties),
        'filtered_count': len(filtered),
        'properties': filtered
    }


def rank_by_preferences(properties: list, prefs: dict) -> list:
    """Score and rank using preferences."""
    scoring = prefs.get('scoring', {})
    areas = prefs.get('areas', {})
    
    area_weights = scoring.get('area_weights', {'premium': 30, 'excellent': 25, 'good': 20})
    price_min = scoring.get('price_ideal_min', 400000)
    price_max = scoring.get('price_ideal_max', 550000)
    prefer_images = scoring.get('prefer_images', True)
    prefer_multiple = scoring.get('prefer_multiple_portals', True)
    
    premium_areas = areas.get('premium', [])
    desired_areas = areas.get('desired', [])
    
    for prop in properties:
        score = 0
        
        # Price scoring
        price = prop.get('price', 0)
        if price_min <= price <= price_max:
            score += 20
        elif price < price_min:
            score += 10
        elif price <= price_max * 1.2:
            score += 5
        
        # Area scoring
        postcode = prop.get('postcode', '').upper()
        address = prop.get('address', '').upper()
        
        # Premium areas
        if any(area.upper() in postcode or area.upper() in address for area in premium_areas):
            score += area_weights['premium']
        # Other desired areas
        elif any(area.upper() in postcode or area.upper() in address for area in desired_areas):
            score += area_weights['good']
        
        # Beds scoring
        beds = prop.get('beds', 0)
        if beds >= 4:
            score += 15
        
        # Images
        if prefer_images and (prop.get('image_url') or prop.get('images')):
            score += 5
        
        # Multiple portals
        if prefer_multiple:
            portals = prop.get('portals', [prop.get('portal')])
            if len(portals) > 1:
                score += 10
        
        prop['score'] = score
    
    return sorted(properties, key=lambda x: x.get('score', 0), reverse=True)


def save_snapshot(properties: list):
    """Save today's snapshot for tomorrow's comparison."""
    CACHE_DIR.mkdir(exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    snapshot_file = CACHE_DIR / f"{today}.json"
    
    with open(snapshot_file, 'w') as f:
        json.dump({'properties': properties}, f, indent=2)


def generate_briefing(prefs: dict = None, overrides: dict = None) -> dict:
    """
    Generate full briefing with automatic deduplication.
    
    Args:
        prefs: User preferences (loaded from config)
        overrides: CLI argument overrides
    """
    prefs = prefs or {}
    overrides = overrides or {}
    
    # Get search criteria (CLI overrides config)
    min_beds = overrides.get('min_beds') or prefs.get('search', {}).get('min_beds', 4)
    
    # 1. Fetch all portals
    fetch_result = fetch_all_portals(min_beds)
    
    # 2. AUTOMATIC Deduplication (built-in, no separate step)
    dedupe_enabled = prefs.get('deduplication', {}).get('enabled', True)
    dedupe_threshold = prefs.get('deduplication', {}).get('threshold', 0.85)
    
    if dedupe_enabled:
        dedupe_result = deduplicate_automatic(fetch_result['all_properties'], dedupe_threshold)
    else:
        dedupe_result = {
            'original_count': len(fetch_result['all_properties']),
            'unique_count': len(fetch_result['all_properties']),
            'duplicate_count': 0,
            'properties': fetch_result['all_properties']
        }
    
    # 3. Filter by preferences
    filter_result = filter_by_preferences(dedupe_result['properties'], prefs)
    
    # 4. Compare with yesterday
    comparison = compare_with_yesterday(filter_result['properties'])
    
    # 5. Rank by preferences
    ranked = rank_by_preferences(filter_result['properties'], prefs)
    
    # 6. Save snapshot
    save_snapshot(filter_result['properties'])
    
    # Build briefing
    briefing_prefs = prefs.get('briefing', {})
    max_results = briefing_prefs.get('max_results', 10)
    
    briefing = {
        'generated_at': datetime.now().isoformat(),
        'stats': {
            'total_fetched': fetch_result['total_count'],
            'after_dedupe': dedupe_result['unique_count'],
            'duplicates_removed': dedupe_result['duplicate_count'],
            'after_filtering': filter_result['filtered_count'],
            'new_listings': len(comparison.get('new_listings', [])),
            'price_changes': len(comparison.get('price_changes', []))
        },
        'new_listings': comparison.get('new_listings', [])[:max_results],
        'price_changes': comparison.get('price_changes', []),
        'top_picks': ranked[:max_results],
        'all_properties': ranked
    }
    
    return briefing


def main():
    parser = argparse.ArgumentParser(description='Generate property briefing')
    parser.add_argument('--config', type=Path, help='Preferences file (default: preferences.json)')
    parser.add_argument('--min-beds', type=int, help='Override minimum bedrooms')
    parser.add_argument('--max-price', type=int, help='Override maximum price')
    
    args = parser.parse_args()
    
    # Load preferences
    prefs = load_preferences(args.config)
    
    # Build overrides
    overrides = {}
    if args.min_beds:
        overrides['min_beds'] = args.min_beds
    if args.max_price:
        if 'search' not in prefs:
            prefs['search'] = {}
        prefs['search']['max_price'] = args.max_price
    
    briefing = generate_briefing(prefs, overrides)
    
    print(json.dumps(briefing, indent=2))


if __name__ == '__main__':
    main()
