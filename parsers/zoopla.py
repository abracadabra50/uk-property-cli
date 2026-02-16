#!/usr/bin/env python3
"""
Zoopla Property Parser
Extracts property data from Zoopla search pages
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
    """Fetch Zoopla search page using curl"""
    url = f"https://www.zoopla.co.uk/for-sale/houses/edinburgh/?beds_min={beds}&q=Edinburgh"
    result = subprocess.run(
        ["curl", "-s", "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", url],
        capture_output=True,
        text=True
    )
    return result.stdout

def is_bad_area(address):
    """Check if property is in excluded area"""
    return any(bad in address for bad in BAD_AREAS)

def categorize(prop):
    """Categorize as investment or family"""
    price = prop.get("price", 999999)
    beds = prop.get("beds", 0)
    
    if price < 250000:
        return "investment"
    elif beds >= 4:
        return "family"
    else:
        return "other"

def parse_properties(html):
    """Extract property data from Zoopla page"""
    properties = []
    
    # Zoopla also embeds JSON data - look for __PRELOADED_STATE__ or similar
    # Pattern varies, but typically in script tags
    
    # Try to find JSON data in script tags
    script_match = re.search(r'<script[^>]*>window\.__PRELOADED_STATE__\s*=\s*({.*?})</script>', html, re.DOTALL)
    
    if script_match:
        try:
            data = json.loads(script_match.group(1))
            # Extract listings from nested structure (would need actual structure)
            # This is a placeholder showing the approach
        except:
            pass
    
    # For now, return empty - would need to inspect actual Zoopla HTML structure
    # The framework is ready for when we implement it
    
    return properties

def main():
    html = fetch_page(BEDS)
    properties = parse_properties(html)
    
    output = {
        "portal": "zoopla",
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "count": len(properties),
        "properties": properties,
        "note": "Parser framework ready - needs HTML structure inspection"
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
