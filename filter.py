#!/usr/bin/env python3
"""
Filter properties by area, price, beds, etc.

Usage:
    python3 filter.py <properties.json> [options]
    
Options:
    --areas EH10,EH12,EH4      Desired postcodes/areas
    --exclude EH17,Niddrie     Areas to exclude
    --min-price 300000         Minimum price
    --max-price 600000         Maximum price
    --min-beds 4               Minimum bedrooms
    --category family          Category filter
"""

import json
import sys
import argparse
from typing import List, Dict, Any


# Edinburgh area configuration
DESIRED_AREAS = [
    'EH10',  # Morningside
    'EH12',  # Corstorphine
    'EH13',  # Oxgangs, Colinton
    'EH14',  # Juniper Green, Colinton
    'EH4',   # Davidson's Mains, Cramond
    'EH5',   # Leith
    'EH6',   # Leith
    'EH15',  # Portobello, Joppa
    'EH3',   # Stockbridge
    'EH9',   # Marchmont, Bruntsfield
]

EXCLUDED_AREAS = [
    'EH17',  # Liberton (some areas)
    'Moredun',
    'Niddrie',
    'Wester Hailes',
    'Sighthill',
    'Muirhouse',
    'Pilton',
    'Granton',
    'EH29',  # Kirkliston
]


def filter_properties(
    properties: List[Dict[str, Any]],
    areas: List[str] = None,
    exclude: List[str] = None,
    min_price: int = None,
    max_price: int = None,
    min_beds: int = None,
    category: str = None
) -> List[Dict[str, Any]]:
    """
    Filter properties by criteria.
    
    Args:
        properties: List of property dicts
        areas: Desired areas/postcodes (case-insensitive partial match)
        exclude: Areas to exclude (case-insensitive partial match)
        min_price: Minimum price
        max_price: Maximum price
        min_beds: Minimum bedrooms
        category: Category filter (investment, family, other)
    
    Returns:
        Filtered list of properties
    """
    filtered = properties
    
    # Area filtering
    if areas:
        areas_lower = [a.lower() for a in areas]
        filtered = [
            p for p in filtered
            if any(area in p.get('address', '').lower() or area in p.get('postcode', '').lower() 
                   for area in areas_lower)
        ]
    
    # Exclude areas
    if exclude:
        exclude_lower = [e.lower() for e in exclude]
        filtered = [
            p for p in filtered
            if not any(excl in p.get('address', '').lower() or excl in p.get('postcode', '').lower()
                      for excl in exclude_lower)
        ]
    
    # Price filtering
    if min_price is not None:
        filtered = [p for p in filtered if p.get('price', 0) >= min_price]
    
    if max_price is not None:
        filtered = [p for p in filtered if p.get('price', 0) <= max_price]
    
    # Bedroom filtering
    if min_beds is not None:
        filtered = [p for p in filtered if p.get('beds', 0) >= min_beds]
    
    # Category filtering
    if category:
        filtered = [p for p in filtered if p.get('category') == category]
    
    return filtered


def main():
    parser = argparse.ArgumentParser(description='Filter properties')
    parser.add_argument('input_file', help='Input JSON file')
    parser.add_argument('--areas', help='Desired areas (comma-separated)')
    parser.add_argument('--exclude', help='Areas to exclude (comma-separated)')
    parser.add_argument('--min-price', type=int, help='Minimum price')
    parser.add_argument('--max-price', type=int, help='Maximum price')
    parser.add_argument('--min-beds', type=int, help='Minimum bedrooms')
    parser.add_argument('--category', choices=['investment', 'family', 'other'], help='Category filter')
    parser.add_argument('--use-defaults', action='store_true', help='Use default Edinburgh areas')
    
    args = parser.parse_args()
    
    # Load properties
    try:
        with open(args.input_file) as f:
            data = json.load(f)
            properties = data.get('properties', data) if isinstance(data, dict) else data
    except Exception as e:
        print(f"Error loading {args.input_file}: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Parse areas
    areas = None
    if args.use_defaults:
        areas = DESIRED_AREAS
    elif args.areas:
        areas = [a.strip() for a in args.areas.split(',')]
    
    exclude = None
    if args.use_defaults:
        exclude = EXCLUDED_AREAS
    elif args.exclude:
        exclude = [e.strip() for e in args.exclude.split(',')]
    
    # Filter
    original_count = len(properties)
    filtered = filter_properties(
        properties,
        areas=areas,
        exclude=exclude,
        min_price=args.min_price,
        max_price=args.max_price,
        min_beds=args.min_beds,
        category=args.category
    )
    
    # Output
    result = {
        'filtering': {
            'original_count': original_count,
            'filtered_count': len(filtered),
            'removed_count': original_count - len(filtered),
            'criteria': {
                'areas': areas,
                'exclude': exclude,
                'min_price': args.min_price,
                'max_price': args.max_price,
                'min_beds': args.min_beds,
                'category': args.category
            }
        },
        'properties': filtered
    }
    
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
