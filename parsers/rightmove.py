#!/usr/bin/env python3
"""
Rightmove Property Parser
Extracts embedded JSON from Rightmove search pages
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
    """Fetch Rightmove search page using curl"""
    # Edinburgh region ID: REGION^550
    url = f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E550&minBedrooms={beds}&sortType=6"
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

def extract_price(price_data):
    """Extract price from Rightmove price object"""
    if isinstance(price_data, dict):
        return price_data.get("amount", 0)
    return 0

def parse_properties(html):
    """Extract property data from Rightmove embedded JSON"""
    properties = []
    
    # Rightmove embeds property data as JSON in the page
    # Look for the properties array more carefully
    # It's in a larger JSON blob, so let's extract that first
    
    # Find window.__PRELOADED_STATE__ or similar
    match = re.search(r'"properties":\s*\[((?:\{[^}]+\},?)+)\]', html)
    
    if not match:
        return properties
    
    try:
        # Clean up the JSON string
        json_str = '[' + match.group(1).rstrip(',') + ']'
        raw_props = json.loads(json_str)
        
        for prop in raw_props:
            address = prop.get("displayAddress", "")
            
            if is_bad_area(address):
                continue
            
            # Extract first image
            images = prop.get("images", [])
            image_url = images[0]["srcUrl"] if images else ""
            
            # Parse property data
            parsed = {
                "id": str(prop.get("id", "")),
                "title": prop.get("propertyTypeFullDescription", "Property"),
                "price": extract_price(prop.get("price", {})),
                "price_text": f"£{extract_price(prop.get('price', {})):,}",
                "beds": prop.get("bedrooms", 0),
                "baths": prop.get("bathrooms", 0),
                "property_type": prop.get("propertySubType", "").lower(),
                "address": address,
                "area": address.split(",")[-1].strip() if "," in address else "",
                "postcode": "",  # Not in summary data
                "description": prop.get("summary", ""),
                "url": f"https://www.rightmove.co.uk/properties/{prop.get('id')}",
                "image_url": image_url,
                "images": [img["srcUrl"] for img in images[:5]],
                "features": [],
                "portal": "rightmove",
                "category": categorize({"price": extract_price(prop.get("price", {})), "beds": prop.get("bedrooms", 0)})
            }
            
            properties.append(parsed)
            
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
    
    return properties

def main():
    html = fetch_page(BEDS)
    properties = parse_properties(html)
    
    output = {
        "portal": "rightmove",
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "count": len(properties),
        "properties": properties
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
