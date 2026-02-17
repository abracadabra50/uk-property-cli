#!/usr/bin/env python3
"""
ESPC Property Parser
Extracts property data from ESPC HTML DOM.

ESPC covers Edinburgh and Lothians only.
"""

import re
import sys
from pathlib import Path

# Allow running as script from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import get_espc_location, get_excluded_areas
from parsers.base import (
    Property,
    build_result,
    categorize,
    extract_postcode,
    fetch_url,
    is_bad_area,
    parse_price,
    validate_beds,
)


def build_url(beds: int) -> str:
    """Build ESPC search URL."""
    location = get_espc_location()
    if not location:
        return ""
    return f"https://espc.com/property-for-sale/{location}/houses/{beds}-bed?sort=date-desc"


def parse_properties(html: str, beds: int, excluded_areas: list[str]) -> list[Property]:
    """Extract property data from ESPC HTML."""
    properties = []

    # Find all property IDs
    property_ids = re.findall(r'id="property-(\d+)-', html)
    unique_ids = list(dict.fromkeys(property_ids))

    print(f"Found {len(unique_ids)} properties", file=sys.stderr)

    for prop_id in unique_ids:
        # Find the property section
        pattern = rf'id="property-{prop_id}-.*?(?=id="property-\d+|class="pageWrap"|$)'
        match = re.search(pattern, html, re.DOTALL)
        if not match:
            continue

        section = match.group(0)

        # Extract URL and address
        url_match = re.search(r'href="(/property/([^"]+))"', section)
        if not url_match:
            continue

        url_path = url_match.group(1)
        address_slug = url_match.group(2).split('/')[0]

        # Parse address from slug
        address = address_slug.replace('-', ' ').title()
        address = re.sub(r' Eh(\d+)', r', EH\1', address)

        if is_bad_area(address, excluded_areas):
            continue

        # Extract price
        price = 0
        price_text = "Price on application"
        price_match = re.search(r'(Offers Over|Fixed Price|Offers From).*?£([\d,]+)', section, re.DOTALL)
        if price_match:
            price_text = f"{price_match.group(1)} £{price_match.group(2)}"
            price = parse_price(price_match.group(2))

        # Extract beds/baths
        actual_beds = beds
        beds_match = re.search(r'(\d+)\s+bed', section, re.IGNORECASE)
        if beds_match:
            actual_beds = int(beds_match.group(1))

        baths = 0
        baths_match = re.search(r'(\d+)\s+bath', section, re.IGNORECASE)
        if baths_match:
            baths = int(baths_match.group(1))

        # Extract first image
        img_match = re.search(r'data-src="([^"]+)"', section)
        image_url = img_match.group(1) if img_match else ""

        postcode = extract_postcode(address)

        prop = Property(
            id=prop_id,
            title=f"{actual_beds}-bed house" if actual_beds else "Property",
            price=price,
            price_text=price_text,
            beds=actual_beds,
            baths=baths,
            property_type="house",
            address=address,
            area=address.split(',')[-1].strip() if ',' in address else "",
            postcode=postcode,
            description="",
            url=f"https://espc.com{url_path.split('?')[0]}",
            image_url=image_url,
            images=[image_url] if image_url else [],
            features=[],
            portal="espc",
            category=categorize(price, actual_beds),
        )
        properties.append(prop)

    return properties


def main():
    beds = validate_beds(sys.argv[1] if len(sys.argv) > 1 else None)
    excluded = get_excluded_areas()

    url = build_url(beds)
    if not url:
        result = build_result("espc", [], error="ESPC only available for Edinburgh")
        print(result.to_json())
        return

    html = fetch_url(url)
    if not html:
        result = build_result("espc", [], error="Failed to fetch ESPC")
        print(result.to_json())
        return

    properties = parse_properties(html, beds, excluded)
    result = build_result("espc", properties)
    print(result.to_json())


if __name__ == "__main__":
    main()
