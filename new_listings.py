#!/usr/bin/env python3
"""
new_listings.py - Cross-day new listing detection using address fingerprints.

Solves the Zoopla ID-churn problem: Zoopla generates new IDs for the same
property on each scrape. Using address similarity means we correctly identify
only genuinely new properties, regardless of portal ID instability.

Usage:
    python3 new_listings.py <today_snapshot> <yesterday_snapshot>

Output: JSON list of genuinely new properties
"""
import json, sys, re
from difflib import SequenceMatcher

SIMILARITY_THRESHOLD = 0.82

def norm(a):
    a = (a or '').lower()
    for x, y in [(',',''),('.',''),(' road',' rd'),(' street',' st'),
                 (' avenue',' ave'),(' drive',' dr'),('\\\\',''),('  ',' ')]:
        a = a.replace(x, y)
    return ' '.join(a.split())

def is_same_address(a, b, threshold=SIMILARITY_THRESHOLD):
    return SequenceMatcher(None, a, b).ratio() >= threshold

def find_new_listings(today_props, prev_props):
    """Return props in today that don't appear in prev (by ID or address)."""
    prev_ids    = {p['id'] for p in prev_props}
    prev_addrs  = [norm(p['address']) for p in prev_props]

    new = []
    for p in today_props:
        if p['id'] in prev_ids:
            continue
        an = norm(p['address'])
        if any(is_same_address(an, pa) for pa in prev_addrs):
            continue
        new.append(p)
    return new

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: new_listings.py <today.json> <yesterday.json>")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        today = json.load(f)['properties']
    with open(sys.argv[2]) as f:
        prev  = json.load(f)['properties']

    new = find_new_listings(today, prev)
    print(json.dumps(new, indent=2))
