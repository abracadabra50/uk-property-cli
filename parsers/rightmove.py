#!/usr/bin/env python3
"""
Rightmove Property Parser
Extracts property data from Rightmove Next.js embedded JSON
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
    # Edinburgh region ID: REGION^550, sortType=6 is newest first
    url = f"https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E475&minBedrooms={beds}&sortType=6"
    result = subprocess.run(
        ["curl", "-s", "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", url],
        capture_output=True,
        text=True,
        timeout=15
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

def extract_nextjs_data(html):
    """Extract Next.js JSON data from Rightmove page"""
    # Find script tags
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    
    # Look for the large script with property data (usually >500KB)
    for script in scripts:
        if len(script) > 500000 and 'property' in script.lower():
            try:
                data = json.loads(script)
                return data
            except json.JSONDecodeError:
                continue
    
    return None

def parse_properties(html):
    """Extract property data from Rightmove Next.js JSON"""
    properties = []
    
    # Extract Next.js data
    data = extract_nextjs_data(html)
    if not data:
        print("Could not extract Next.js data", file=sys.stderr)
        return properties
    
    # Navigate to properties
    try:
        search_results = data['props']['pageProps']['searchResults']
        raw_properties = search_results['properties']
        
        print(f"Found {len(raw_properties)} properties", file=sys.stderr)
        
        for prop in raw_properties:
            address = prop.get('displayAddress', '')
            
            # Skip bad areas
            if is_bad_area(address):
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
            
            # Extract postcode from address if present
            postcode = ""
            pc_match = re.search(r'(EH\d+\s*\d*\w*)', address.upper())
            if pc_match:
                postcode = pc_match.group(1)
            
            parsed = {
                "id": str(prop.get('id', '')),
                "title": prop.get('propertyTypeFullDescription', f"{beds}-bed property"),
                "price": price,
                "price_text": price_text,
                "beds": beds,
                "baths": baths,
                "property_type": prop.get('propertySubType', 'house').lower(),
                "address": address,
                "area": address.split(',')[-1].strip() if ',' in address else "",
                "postcode": postcode,
                "description": prop.get('summary', '')[:200],
                "url": f"https://www.rightmove.co.uk{prop.get('propertyUrl', '')}",
                "image_url": images[0] if images else "",
                "images": images,
                "features": prop.get('keyFeatures', []),
                "portal": "rightmove",
                "category": categorize(price, beds)
            }
            
            properties.append(parsed)
        
    except KeyError as e:
        print(f"Data structure error: {e}", file=sys.stderr)
    
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
