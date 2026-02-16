#!/usr/bin/env python3
"""
Compare property snapshots to detect changes.

Usage:
    python3 compare.py <yesterday.json> <today.json>
    
Output:
    New listings, price changes, removed listings
"""

import json
import sys
from typing import List, Dict, Any


def compare_snapshots(yesterday: List[Dict], today: List[Dict]) -> Dict[str, Any]:
    """
    Compare two property snapshots.
    
    Returns dict with:
        - new_listings: Properties in today but not yesterday
        - removed_listings: Properties in yesterday but not today
        - price_changes: Properties with different prices
    """
    # Build ID sets
    yesterday_ids = {p['id']: p for p in yesterday}
    today_ids = {p['id']: p for p in today}
    
    # Find new listings
    new_ids = set(today_ids.keys()) - set(yesterday_ids.keys())
    new_listings = [today_ids[id] for id in new_ids]
    
    # Find removed listings
    removed_ids = set(yesterday_ids.keys()) - set(today_ids.keys())
    removed_listings = [yesterday_ids[id] for id in removed_ids]
    
    # Find price changes
    price_changes = []
    for id in set(yesterday_ids.keys()) & set(today_ids.keys()):
        old = yesterday_ids[id]
        new = today_ids[id]
        
        old_price = old.get('price', 0)
        new_price = new.get('price', 0)
        
        if old_price > 0 and new_price > 0 and old_price != new_price:
            change = {
                'property': new,
                'old_price': old_price,
                'new_price': new_price,
                'change': new_price - old_price,
                'change_percent': round(((new_price - old_price) / old_price) * 100, 1)
            }
            price_changes.append(change)
    
    # Sort price changes by percentage
    price_changes.sort(key=lambda x: x['change_percent'])
    
    return {
        'new_listings': new_listings,
        'removed_listings': removed_listings,
        'price_changes': price_changes,
        'stats': {
            'new_count': len(new_listings),
            'removed_count': len(removed_listings),
            'price_changes_count': len(price_changes),
            'price_drops': len([c for c in price_changes if c['change'] < 0]),
            'price_increases': len([c for c in price_changes if c['change'] > 0])
        }
    }


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 compare.py <yesterday.json> <today.json>")
        print("\nExample:")
        print("  python3 compare.py cache/2026-02-15.json cache/2026-02-16.json")
        sys.exit(1)
    
    yesterday_file = sys.argv[1]
    today_file = sys.argv[2]
    
    # Load snapshots
    try:
        with open(yesterday_file) as f:
            yesterday_data = json.load(f)
            yesterday = yesterday_data.get('properties', yesterday_data) if isinstance(yesterday_data, dict) else yesterday_data
    except Exception as e:
        print(f"Error loading {yesterday_file}: {e}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(today_file) as f:
            today_data = json.load(f)
            today = today_data.get('properties', today_data) if isinstance(today_data, dict) else today_data
    except Exception as e:
        print(f"Error loading {today_file}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Compare
    result = compare_snapshots(yesterday, today)
    
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
