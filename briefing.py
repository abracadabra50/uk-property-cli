#!/usr/bin/env python3
"""
Generate comprehensive property briefing.

Combines: fetch → dedupe → filter → compare → rank

Usage:
    python3 briefing.py [--min-beds 4] [--max-price 600000]
    
Outputs JSON briefing with:
    - New listings
    - Price changes
    - Top picks
    - Statistics
"""

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path
import argparse


SKILL_DIR = Path(__file__).parent
CACHE_DIR = SKILL_DIR / 'cache'


def fetch_all_portals(min_beds: int = 4) -> dict:
    """Fetch from all portals and combine."""
    print("Fetching from all portals...", file=sys.stderr)
    
    results = {}
    
    # ESPC
    try:
        result = subprocess.run(
            ['python3', str(SKILL_DIR / 'parsers/espc.py'), str(min_beds)],
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
            ['python3', str(SKILL_DIR / 'parsers/rightmove.py'), str(min_beds)],
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
            ['python3', str(SKILL_DIR / 'parsers/zoopla.py'), str(min_beds)],
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


def deduplicate(properties: list) -> dict:
    """Deduplicate properties."""
    from dedupe import deduplicate as dedupe_func
    
    unique = dedupe_func(properties)
    
    return {
        'original_count': len(properties),
        'unique_count': len(unique),
        'duplicate_count': len(properties) - len(unique),
        'properties': unique
    }


def compare_with_yesterday(today_properties: list) -> dict:
    """Compare with yesterday's snapshot."""
    yesterday_file = CACHE_DIR / f"{(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}.json"
    
    if not yesterday_file.exists():
        return {
            'has_comparison': False,
            'new_listings': today_properties,
            'price_changes': []
        }
    
    with open(yesterday_file) as f:
        yesterday_data = json.load(f)
        yesterday = yesterday_data.get('properties', yesterday_data)
    
    from compare import compare_snapshots
    comparison = compare_snapshots(yesterday, today_properties)
    comparison['has_comparison'] = True
    
    return comparison


def filter_properties(properties: list, min_price: int = None, max_price: int = None) -> dict:
    """Filter by preferences."""
    from filter import filter_properties as filter_func, DESIRED_AREAS, EXCLUDED_AREAS
    
    filtered = filter_func(
        properties,
        areas=DESIRED_AREAS,
        exclude=EXCLUDED_AREAS,
        min_price=min_price,
        max_price=max_price
    )
    
    return {
        'original_count': len(properties),
        'filtered_count': len(filtered),
        'properties': filtered
    }


def rank_properties(properties: list) -> list:
    """Score and rank properties."""
    for prop in properties:
        score = 0
        
        # Price scoring (lower is better within range)
        price = prop.get('price', 0)
        if 400000 <= price <= 550000:
            score += 20
        elif 300000 <= price < 400000:
            score += 15
        elif 550000 < price <= 650000:
            score += 10
        
        # Area scoring
        postcode = prop.get('postcode', '').upper()
        if 'EH10' in postcode or 'EH9' in postcode:  # Morningside, Bruntsfield
            score += 30
        elif 'EH12' in postcode or 'EH4' in postcode:  # Corstorphine, Cramond
            score += 25
        elif 'EH13' in postcode or 'EH14' in postcode:  # Colinton
            score += 20
        
        # Beds scoring
        beds = prop.get('beds', 0)
        if beds >= 4:
            score += 15
        
        # Has images
        if prop.get('image_url') or prop.get('images'):
            score += 5
        
        # Multiple portals (likely accurate listing)
        portals = prop.get('portals', [prop.get('portal')])
        if len(portals) > 1:
            score += 10
        
        prop['score'] = score
    
    # Sort by score descending
    return sorted(properties, key=lambda x: x.get('score', 0), reverse=True)


def save_snapshot(properties: list):
    """Save today's snapshot for tomorrow's comparison."""
    CACHE_DIR.mkdir(exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    snapshot_file = CACHE_DIR / f"{today}.json"
    
    with open(snapshot_file, 'w') as f:
        json.dump({'properties': properties}, f, indent=2)


def generate_briefing(min_beds: int = 4, max_price: int = None) -> dict:
    """Generate full briefing."""
    # 1. Fetch all portals
    fetch_result = fetch_all_portals(min_beds)
    
    # 2. Deduplicate
    dedupe_result = deduplicate(fetch_result['all_properties'])
    
    # 3. Filter
    filter_result = filter_properties(
        dedupe_result['properties'],
        max_price=max_price
    )
    
    # 4. Compare with yesterday
    comparison = compare_with_yesterday(filter_result['properties'])
    
    # 5. Rank
    ranked = rank_properties(filter_result['properties'])
    
    # 6. Save snapshot
    save_snapshot(filter_result['properties'])
    
    # Build briefing
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
        'new_listings': comparison.get('new_listings', [])[:10],  # Top 10 new
        'price_changes': comparison.get('price_changes', []),
        'top_picks': ranked[:10],  # Top 10 overall
        'all_properties': ranked
    }
    
    return briefing


def main():
    parser = argparse.ArgumentParser(description='Generate property briefing')
    parser.add_argument('--min-beds', type=int, default=4, help='Minimum bedrooms')
    parser.add_argument('--max-price', type=int, help='Maximum price')
    
    args = parser.parse_args()
    
    briefing = generate_briefing(
        min_beds=args.min_beds,
        max_price=args.max_price
    )
    
    print(json.dumps(briefing, indent=2))


if __name__ == '__main__':
    main()
