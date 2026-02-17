#!/usr/bin/env python3
"""
Deduplicate properties across portals.

Usage:
    python3 dedupe.py <file1.json> <file2.json> ...

Output:
    Unique properties with merged data.

Optimized with postcode bucketing to avoid O(n^2) comparisons.
"""

import json
import sys
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Any, Dict, List

from config import get_dedup_threshold
from parsers.base import UK_POSTCODE_AREA_RE


def normalize_address(addr: str) -> str:
    """Normalize address for matching."""
    addr = addr.lower()
    addr = addr.replace(',', '').replace('.', '')
    addr = addr.replace(' street', ' st').replace(' road', ' rd')
    addr = addr.replace(' avenue', ' ave').replace(' drive', ' dr')
    addr = addr.replace(' lane', ' ln').replace(' place', ' pl')
    addr = addr.replace(' crescent', ' cr').replace(' terrace', ' ter')
    addr = ' '.join(addr.split())
    return addr


def extract_postcode_area(addr: str) -> str:
    """Extract postcode area (e.g. 'EH10') for bucketing."""
    match = UK_POSTCODE_AREA_RE.search(addr.upper())
    return match.group(1) if match else ""


def addresses_match(addr1: str, addr2: str, threshold: float = 0.85) -> bool:
    """Check if two addresses match based on similarity."""
    norm1 = normalize_address(addr1)
    norm2 = normalize_address(addr2)
    return SequenceMatcher(None, norm1, norm2).ratio() >= threshold


def merge_property_data(duplicates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge data from duplicate properties across portals."""
    merged = duplicates[0].copy()

    # Collect all unique images
    all_images = []
    for prop in duplicates:
        all_images.extend(prop.get('images', []))
    merged['images'] = list(set(filter(None, all_images)))

    # Take best price (lowest non-zero)
    prices = [p['price'] for p in duplicates if p.get('price', 0) > 0]
    if prices:
        merged['price'] = min(prices)

    # Take highest bed/bath counts
    merged['beds'] = max(p.get('beds', 0) for p in duplicates)
    merged['baths'] = max(p.get('baths', 0) for p in duplicates)

    # Track which portals have this property
    merged['portals'] = list(set(p['portal'] for p in duplicates))

    # Keep all URLs
    merged['urls'] = {p['portal']: p['url'] for p in duplicates}

    # Use best image URL
    image_urls = [p.get('image_url', '') for p in duplicates if p.get('image_url')]
    if image_urls:
        merged['image_url'] = image_urls[0]

    # Combine features
    all_features = []
    for prop in duplicates:
        all_features.extend(prop.get('features', []))
    merged['features'] = list(set(all_features))

    # Use longest description
    descriptions = [p.get('description', '') for p in duplicates]
    merged['description'] = max(descriptions, key=len) if descriptions else ''

    return merged


def deduplicate(properties: List[Dict[str, Any]], threshold: float = 0.85) -> List[Dict[str, Any]]:
    """
    Deduplicate properties by address similarity.

    Uses postcode bucketing to reduce comparisons from O(n^2) to roughly O(n).
    Properties are only compared within the same postcode area.
    """
    # Bucket by postcode area
    buckets: Dict[str, List[int]] = defaultdict(list)
    for i, prop in enumerate(properties):
        area = extract_postcode_area(prop.get('address', '') + ' ' + prop.get('postcode', ''))
        buckets[area].append(i)

    unique = []
    processed_indices = set()

    for indices in buckets.values():
        for idx_pos, i in enumerate(indices):
            if i in processed_indices:
                continue

            duplicates = [properties[i]]
            processed_indices.add(i)

            # Only compare within the same postcode bucket
            for j in indices[idx_pos + 1:]:
                if j in processed_indices:
                    continue
                if addresses_match(properties[i]['address'], properties[j]['address'], threshold):
                    duplicates.append(properties[j])
                    processed_indices.add(j)

            if len(duplicates) > 1:
                unique.append(merge_property_data(duplicates))
            else:
                unique.append(properties[i])

    return unique


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 dedupe.py <file1.json> <file2.json> ...")
        print("\nExample:")
        print("  python3 dedupe.py cache/espc.json cache/rightmove.json cache/zoopla.json")
        sys.exit(1)

    threshold = get_dedup_threshold()

    # Load all properties from input files
    all_properties = []
    for filename in sys.argv[1:]:
        try:
            with open(filename) as f:
                data = json.load(f)
                props = data.get('properties', data) if isinstance(data, dict) else data
                all_properties.extend(props)
        except Exception as e:
            print(f"Error loading {filename}: {e}", file=sys.stderr)
            continue

    # Deduplicate
    original_count = len(all_properties)
    unique = deduplicate(all_properties, threshold)
    duplicate_count = original_count - len(unique)

    result = {
        'deduplication': {
            'original_count': original_count,
            'unique_count': len(unique),
            'duplicate_count': duplicate_count,
            'duplicate_percentage': round((duplicate_count / original_count) * 100, 1) if original_count > 0 else 0,
            'threshold': threshold,
        },
        'properties': unique,
    }

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
