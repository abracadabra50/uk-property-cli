#!/usr/bin/env python3
"""
Zoopla Property Parser
Uses Firecrawl API to bypass Cloudflare protection
NOTE: Requires firecrawl CLI and API key (breaks zero-dependency principle)
"""

import sys, json, subprocess, re
from datetime import datetime

BEDS = sys.argv[1] if len(sys.argv) > 1 else "4"

# Bad areas to exclude
BAD_AREAS = [
    "Moredun", "Niddrie", "Wester Hailes", "Sighthill", 
    "Muirhouse", "Pilton", "Kirkliston", "Musselburgh", 
    "Dalkeith", "Granton", "Liberton"
]

def fetch_page(beds):
    """Fetch Zoopla search page using firecrawl (bypasses Cloudflare)"""
    url = f"https://www.zoopla.co.uk/for-sale/property/edinburgh/?beds_min={beds}&results_sort=newest_listings"
    
    # Check if firecrawl is available
    result = subprocess.run(
        ["which", "firecrawl"],
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print("Error: firecrawl CLI not found. Install with: npm install -g @mendable/firecrawl-cli", file=sys.stderr)
        print("Also set FIRECRAWL_API_KEY environment variable", file=sys.stderr)
        return ""
    
    # Fetch with firecrawl
    result = subprocess.run(
        ["firecrawl", "scrape", url, "--format", "markdown"],
        capture_output=True,
        text=True,
        timeout=30
    )
    
    return result.stdout

def is_bad_area(address):
    """Check if property is in excluded area"""
    return any(bad.lower() in address.lower() for bad in BAD_AREAS)

def categorize(price, beds):
    """Categorize as investment or family"""
    if price < 250000:
        return "investment"
    elif beds >= 4:
        return "family"
    else:
        return "other"

def parse_price(price_text):
    """Extract numeric price from text like '£550,000'"""
    if not price_text:
        return 0
    # Remove everything except digits
    digits = re.sub(r'[^\d]', '', price_text)
    return int(digits) if digits else 0

def parse_properties(markdown):
    """Extract property data from Zoopla markdown"""
    properties = []
    
    # Pattern: [£price ... beds ... baths ... address ... description ...]
    # Look for property blocks in markdown
    property_pattern = r'\[£([\d,]+).*?(\d+)\s+beds.*?(\d+)\s+baths.*?\n(.*?)\n(.*?)\]'
    
    matches = re.findall(property_pattern, markdown, re.DOTALL)
    
    for price_text, beds, baths, address, description in matches:
        # Skip bad areas
        if is_bad_area(address):
            continue
        
        price = parse_price(price_text)
        
        # Extract postcode
        postcode = ""
        pc_match = re.search(r'(EH\d+\s*\d*\w*)', address.upper())
        if pc_match:
            postcode = pc_match.group(1)
        
        # Extract Zoopla ID from URL (would need to capture URL separately)
        # For now, use a hash of address as ID
        prop_id = str(abs(hash(address)) % 100000000)
        
        prop = {
            "id": prop_id,
            "title": f"{beds}-bed property",
            "price": price,
            "price_text": f"Offers over £{price_text}",
            "beds": int(beds),
            "baths": int(baths),
            "property_type": "house",
            "address": address.strip(),
            "area": address.split(',')[-1].strip() if ',' in address else "",
            "postcode": postcode,
            "description": description.strip()[:200],
            "url": f"https://www.zoopla.co.uk/for-sale/details/{prop_id}/",  # Approximate
            "image_url": "",
            "images": [],
            "features": [],
            "portal": "zoopla",
            "category": categorize(price, int(beds))
        }
        
        properties.append(prop)
    
    return properties

def main():
    markdown = fetch_page(BEDS)
    
    if not markdown:
        output = {
            "portal": "zoopla",
            "fetched_at": datetime.utcnow().isoformat() + "Z",
            "count": 0,
            "properties": [],
            "error": "Firecrawl not available or API key not set"
        }
        print(json.dumps(output, indent=2))
        return
    
    properties = parse_properties(markdown)
    
    output = {
        "portal": "zoopla",
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "count": len(properties),
        "properties": properties,
        "note": "Uses Firecrawl API (requires API key, ~$1/1000 requests)"
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
