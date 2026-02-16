#!/usr/bin/env python3
"""
Deduplicate properties across portals.

Usage:
    python3 dedupe.py <file1.json> <file2.json> ...
    
Output:
    Unique properties with merged data
"""

import json
import sys
from difflib import SequenceMatcher
from typing import List, Dict, Any


def normalize_address(addr: str) -> str:
    """Normalize address for matching."""
    addr = addr.lower()
    addr = addr.replace(',', '').replace('.', '')
    addr = addr.replace(' street', ' st').replace(' road', ' rd')
    addr = addr.replace(' avenue', ' ave').replace(' drive', ' dr')
    addr = ' '.join(addr.split())  # Normalize whitespace
    return addr


def addresses_match(addr1: str, addr2: str, threshold: float = 0.85) -> bool:
    """Check if two addresses match based on similarity."""
    norm1 = normalize_address(addr1)
    norm2 = normalize_address(addr2)
    
    similarity = SequenceMatcher(None, norm1, norm2).ratio()
    return similarity >= threshold


def merge_property_data(duplicates: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge data from duplicate properties across portals."""
    # Start with first property as base
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
    merged['portals'] = [p['portal'] for p in duplicates]
    
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
    
    Args:
        properties: List of property dicts
        threshold: Similarity score 0-1 (default 0.85 = 85% match)
    
    Returns:
        List of unique properties with merged data
    """
    unique = []
    processed_indices = set()
    
    for i, prop in enumerate(properties):
        if i in processed_indices:
            continue
        
        # Find all duplicates of this property
        duplicates = [prop]
        processed_indices.add(i)
        
        for j, other in enumerate(properties[i+1:], start=i+1):
            if j in processed_indices:
                continue
            
            if addresses_match(prop['address'], other['address'], threshold):
                duplicates.append(other)
                processed_indices.add(j)
        
        # Merge duplicate data
        if len(duplicates) > 1:
            merged = merge_property_data(duplicates)
            unique.append(merged)
        else:
            unique.append(prop)
    
    return unique


def main():
    if len(sys.argv) < 2:
        print("Usage: python3 dedupe.py <file1.json> <file2.json> ...")
        print("\nExample:")
        print("  python3 dedupe.py cache/espc.json cache/rightmove.json cache/zoopla.json")
        sys.exit(1)
    
    # Load all properties from input files
    all_properties = []
    for filename in sys.argv[1:]:
        try:
            with open(filename) as f:
                data = json.load(f)
                properties = data.get('properties', data) if isinstance(data, dict) else data
                all_properties.extend(properties)
        except Exception as e:
            print(f"Error loading {filename}: {e}", file=sys.stderr)
            continue
    
    # Deduplicate
    original_count = len(all_properties)
    unique = deduplicate(all_properties)
    duplicate_count = original_count - len(unique)
    
    # Output
    result = {
        'deduplication': {
            'original_count': original_count,
            'unique_count': len(unique),
            'duplicate_count': duplicate_count,
            'duplicate_percentage': round((duplicate_count / original_count) * 100, 1) if original_count > 0 else 0
        },
        'properties': unique
    }
    
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
