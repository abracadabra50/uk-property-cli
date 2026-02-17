#!/usr/bin/env python3
"""
Rightmove Property Parser
Extracts property data from Rightmove Next.js embedded JSON.

Rightmove covers the entire UK (~80% market share).
"""

import json
import re
import sys
from pathlib import Path

# Allow running as script from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import get_excluded_areas, get_rightmove_region
from parsers.base import (
    Property,
    build_result,
    categorize,
    extract_postcode,
    fetch_url,
    is_bad_area,
    validate_beds,
)


def build_url(beds: int) -> str:
    """Build Rightmove search URL for configured location."""
    region = get_rightmove_region()
    if not region:
        return ""
    return f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier={region}&minBedrooms={beds}&sortType=6"


def extract_nextjs_data(html: str) -> dict | None:
    """Extract Next.js JSON data from Rightmove page."""
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)

    for script in scripts:
        if len(script) > 500000 and 'property' in script.lower():
            try:
                return json.loads(script)
            except json.JSONDecodeError:
                continue

    return None


def parse_properties(html: str, excluded_areas: list[str]) -> list[Property]:
    """Extract property data from Rightmove Next.js JSON."""
    properties = []

    data = extract_nextjs_data(html)
    if not data:
        print("Could not extract Next.js data", file=sys.stderr)
        return properties

    try:
        search_results = data['props']['pageProps']['searchResults']
        raw_properties = search_results['properties']

        print(f"Found {len(raw_properties)} properties", file=sys.stderr)

        for prop in raw_properties:
            address = prop.get('displayAddress', '')

            if is_bad_area(address, excluded_areas):
                continue

            # Extract price
            price = 0
            price_text = "Price on application"
            if 'price' in prop and prop['price']:
                price = prop['price'].get('amount', 0)
                if 'displayPrices' in prop['price'] and prop['price']['displayPrices']:
                    display_price = prop['price']['displayPrices'][0]
                    price_text = f"{display_price.get('displayPriceQualifier', '')} {display_price.get('displayPrice', '')}".strip()

            # Extract images
            images = []
            if 'propertyImages' in prop and 'images' in prop['propertyImages']:
                images = [img['srcUrl'] for img in prop['propertyImages']['images'][:5]]
            elif 'images' in prop:
                images = [img['srcUrl'] for img in prop['images'][:5]]

            beds = prop.get('bedrooms', 0)
            baths = prop.get('bathrooms', 0)
            postcode = extract_postcode(address)

            parsed = Property(
                id=str(prop.get('id', '')),
                title=prop.get('propertyTypeFullDescription', f"{beds}-bed property"),
                price=price,
                price_text=price_text,
                beds=beds,
                baths=baths,
                property_type=prop.get('propertySubType', 'house').lower(),
                address=address,
                area=address.split(',')[-1].strip() if ',' in address else "",
                postcode=postcode,
                description=prop.get('summary', '')[:200],
                url=f"https://www.rightmove.co.uk{prop.get('propertyUrl', '')}",
                image_url=images[0] if images else "",
                images=images,
                features=prop.get('keyFeatures', []),
                portal="rightmove",
                category=categorize(price, beds),
            )
            properties.append(parsed)

    except KeyError as e:
        print(f"Data structure error: {e}", file=sys.stderr)

    return properties


def main():
    beds = validate_beds(sys.argv[1] if len(sys.argv) > 1 else None)
    excluded = get_excluded_areas()

    url = build_url(beds)
    if not url:
        result = build_result("rightmove", [], error="No Rightmove region configured for this location")
        print(result.to_json())
        return

    html = fetch_url(url)
    if not html:
        result = build_result("rightmove", [], error="Failed to fetch Rightmove")
        print(result.to_json())
        return

    properties = parse_properties(html, excluded)
    result = build_result("rightmove", properties)
    print(result.to_json())


if __name__ == "__main__":
    main()
