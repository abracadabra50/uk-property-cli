#!/usr/bin/env python3
"""
ESPC Property Parser
Extracts property data from ESPC HTML DOM
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
    """Fetch ESPC search page using curl"""
    url = f"https://espc.com/property-for-sale/edinburgh/houses/{beds}-bed?sort=date-desc"
    result = subprocess.run(
        ["curl", "-s", "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)", url],
        capture_output=True,
        text=True
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

def parse_price(text):
    """Extract price from text"""
    match = re.search(r'£([\d,]+)', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0

def parse_properties(html):
    """Extract property data from ESPC HTML"""
    properties = []
    
    # Find all property IDs
    property_ids = re.findall(r'id="property-(\d+)-', html)
    unique_ids = list(dict.fromkeys(property_ids))  # Remove duplicates
    
    print(f"Found {len(unique_ids)} properties", file=sys.stderr)
    
    for prop_id in unique_ids[:20]:  # Limit to 20
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
        address_slug = url_match.group(2).split('/')[0]  # e.g., "1-buckstone-circle-edinburgh-eh10-6xb"
        
        # Parse address from slug
        address = address_slug.replace('-', ' ').title()
        address = re.sub(r' Eh(\d+)', r', EH\1', address)  # Fix postcode
        
        # Skip bad areas
        if is_bad_area(address):
            continue
        
        # Extract price
        price = 0
        price_text = "Price on application"
        price_match = re.search(r'(Offers Over|Fixed Price|Offers From)\s*£([\d,]+)', section)
        if price_match:
            price_text = f"{price_match.group(1)} £{price_match.group(2)}"
            price = parse_price(price_match.group(2))
        
        # Extract beds/baths
        beds = int(BEDS)  # Default to search parameter
        beds_match = re.search(r'(\d+)\s+bed', section, re.IGNORECASE)
        if beds_match:
            beds = int(beds_match.group(1))
        
        baths = 0
        baths_match = re.search(r'(\d+)\s+bath', section, re.IGNORECASE)
        if baths_match:
            baths = int(baths_match.group(1))
        
        # Extract first image
        img_match = re.search(r'data-src="([^"]+)"', section)
        image_url = img_match.group(1) if img_match else ""
        
        # Extract postcode
        postcode = ""
        pc_match = re.search(r'(EH\d+\s*\d*\w*)', address.upper())
        if pc_match:
            postcode = pc_match.group(1)
        
        prop = {
            "id": prop_id,
            "title": f"{beds}-bed house" if beds else "Property",
            "price": price,
            "price_text": price_text,
            "beds": beds,
            "baths": baths,
            "property_type": "house",
            "address": address,
            "area": address.split(',')[-1].strip() if ',' in address else address.split()[-1],
            "postcode": postcode,
            "description": "",
            "url": f"https://espc.com{url_path.split('?')[0]}",
            "image_url": image_url,
            "images": [image_url] if image_url else [],
            "features": [],
            "portal": "espc",
            "category": categorize(price, beds)
        }
        
        properties.append(prop)
    
    return properties

def main():
    html = fetch_page(BEDS)
    properties = parse_properties(html)
    
    output = {
        "portal": "espc",
        "fetched_at": datetime.utcnow().isoformat() + "Z",
        "count": len(properties),
        "properties": properties
    }
    
    print(json.dumps(output, indent=2))

if __name__ == "__main__":
    main()
