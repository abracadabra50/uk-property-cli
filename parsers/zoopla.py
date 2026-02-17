#!/usr/bin/env python3
"""
Zoopla Property Parser
Uses Firecrawl API to bypass Cloudflare protection.

NOTE: Requires firecrawl CLI and API key (optional dependency).
"""

import hashlib
import re
import subprocess
import sys
from pathlib import Path

# Allow running as script from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import get_excluded_areas, get_zoopla_location
from parsers.base import (
    Property,
    build_result,
    categorize,
    extract_postcode,
    is_bad_area,
    parse_price,
    validate_beds,
)


def build_url(beds: int) -> str:
    """Build Zoopla search URL for configured location."""
    location = get_zoopla_location()
    if not location:
        return ""
    return f"https://www.zoopla.co.uk/for-sale/property/{location}/?beds_min={beds}&results_sort=newest_listings"


def stable_id(address: str) -> str:
    """Generate a stable, deterministic ID from an address using MD5."""
    return hashlib.md5(address.strip().lower().encode()).hexdigest()[:8]


def fetch_with_firecrawl(url: str) -> str | None:
    """Fetch URL using firecrawl to bypass Cloudflare."""
    # Check if firecrawl is available
    result = subprocess.run(["which", "firecrawl"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Error: firecrawl CLI not found. Install with: npm install -g @mendable/firecrawl-cli", file=sys.stderr)
        print("Also set FIRECRAWL_API_KEY environment variable", file=sys.stderr)
        return None

    try:
        result = subprocess.run(
            ["firecrawl", "scrape", url, "--format", "markdown"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
        print(f"Firecrawl failed: exit code {result.returncode}", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        print("Firecrawl timed out after 30s", file=sys.stderr)
        return None


def parse_properties(markdown: str, excluded_areas: list[str]) -> list[Property]:
    """Extract property data from Zoopla markdown."""
    properties = []

    property_pattern = r'\[£([\d,]+).*?(\d+)\s+beds.*?(\d+)\s+baths.*?\n(.*?)\n(.*?)\]'
    matches = re.findall(property_pattern, markdown, re.DOTALL)

    for price_text, beds_str, baths_str, address, description in matches:
        address = address.strip()

        if is_bad_area(address, excluded_areas):
            continue

        price = parse_price(price_text)
        beds = int(beds_str)
        baths = int(baths_str)
        postcode = extract_postcode(address)
        prop_id = stable_id(address)

        prop = Property(
            id=prop_id,
            title=f"{beds}-bed property",
            price=price,
            price_text=f"Offers over £{price_text}",
            beds=beds,
            baths=baths,
            property_type="house",
            address=address,
            area=address.split(',')[-1].strip() if ',' in address else "",
            postcode=postcode,
            description=description.strip()[:200],
            url=f"https://www.zoopla.co.uk/for-sale/details/{prop_id}/",
            image_url="",
            images=[],
            features=[],
            portal="zoopla",
            category=categorize(price, beds),
        )
        properties.append(prop)

    return properties


def main():
    beds = validate_beds(sys.argv[1] if len(sys.argv) > 1 else None)
    excluded = get_excluded_areas()

    url = build_url(beds)
    if not url:
        result = build_result("zoopla", [], error="No Zoopla location configured")
        print(result.to_json())
        return

    markdown = fetch_with_firecrawl(url)
    if not markdown:
        result = build_result("zoopla", [], error="Firecrawl not available or API key not set")
        print(result.to_json())
        return

    properties = parse_properties(markdown, excluded)
    result = build_result("zoopla", properties, note="Uses Firecrawl API (requires API key, ~$1/1000 requests)")
    print(result.to_json())


if __name__ == "__main__":
    main()
