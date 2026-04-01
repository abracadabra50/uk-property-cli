#!/usr/bin/env python3
"""
Rightmove Property Parser
Zero-dependency: curl + Python stdlib
Edinburgh region: REGION^475, sortType=6 = newest first
Paginates until results stop or MAX_PAGES reached.
"""

import sys, json, subprocess, re
from datetime import datetime, timezone

BEDS      = sys.argv[1] if len(sys.argv) > 1 else "4"
MAX_PAGES = int(sys.argv[2]) if len(sys.argv) > 2 else 3   # 25 per page → up to 75 results

BAD_AREAS = [
    "Moredun", "Niddrie", "Wester Hailes", "Sighthill",
    "Muirhouse", "Pilton", "Kirkliston", "Granton", "Dalkeith", "Musselburgh"
]

def fetch_page(beds, index=0):
    url = (
        f"https://www.rightmove.co.uk/property-for-sale/find.html"
        f"?locationIdentifier=REGION%5E475&minBedrooms={beds}&sortType=6&index={index}"
    )
    result = subprocess.run(
        ["curl", "-s", "--max-time", "15",
         "-H", "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
         "-H", "Accept-Language: en-GB,en;q=0.9",
         url],
        capture_output=True, text=True, timeout=20
    )
    return result.stdout

def extract_props_from_html(html):
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    for s in scripts:
        if len(s) > 100000 and 'searchResults' in s:
            try:
                d = json.loads(s)
                sr = d['props']['pageProps']['searchResults']
                return sr.get('properties', []), sr.get('resultCount', 0)
            except Exception:
                continue
    return [], 0

def parse_property(prop):
    address = prop.get('displayAddress', '')
    if any(b.lower() in address.lower() for b in BAD_AREAS):
        return None

    price = 0
    price_text = ''
    p = prop.get('price', {}) or {}
    price = p.get('amount', 0) or 0
    dp = (p.get('displayPrices') or [{}])[0]
    qualifier = (dp.get('displayPriceQualifier') or '').strip()
    raw_price = (dp.get('displayPrice') or '').strip()
    if qualifier and raw_price:
        price_text = f"{qualifier} {raw_price}"
    elif raw_price:
        price_text = raw_price
    elif price:
        price_text = f"£{price:,}"

    images = []
    pi = prop.get('propertyImages') or {}
    for img in (pi.get('images') or [])[:5]:
        src = img.get('srcUrl', '')
        if src:
            images.append(src)

    beds  = prop.get('bedrooms', 0) or 0
    baths = prop.get('bathrooms', 0) or 0

    pc_match = re.search(r'\b(EH\d+\s*\d*\w*)\b', address, re.I)
    postcode = pc_match.group(1).upper() if pc_match else ''

    category = 'investment' if price < 250000 else ('family' if beds >= 4 else 'other')

    return {
        "id":            str(prop.get('id', '')),
        "title":         prop.get('propertyTypeFullDescription', f"{beds}-bed property"),
        "price":         price,
        "price_text":    price_text,
        "beds":          beds,
        "baths":         baths,
        "property_type": (prop.get('propertySubType') or 'property').lower(),
        "address":       address,
        "postcode":      postcode,
        "description":   (prop.get('summary') or '')[:200],
        "url":           f"https://www.rightmove.co.uk{prop.get('propertyUrl', '')}",
        "image_url":     images[0] if images else '',
        "images":        images,
        "features":      prop.get('keyFeatures') or [],
        "portal":        "rightmove",
        "category":      category,
    }

all_props = []
seen_ids  = set()

for page_num in range(MAX_PAGES):
    index = page_num * 24
    html = fetch_page(BEDS, index)
    if not html:
        break

    raw, total = extract_props_from_html(html)
    if not raw:
        break

    new_this_page = 0
    for prop in raw:
        parsed = parse_property(prop)
        if parsed and parsed['id'] and parsed['id'] not in seen_ids:
            seen_ids.add(parsed['id'])
            all_props.append(parsed)
            new_this_page += 1

    # Stop early if nothing new (duplicate page or end of results)
    if new_this_page == 0:
        break

print(json.dumps({
    "portal":     "rightmove",
    "fetched_at": datetime.now(timezone.utc).isoformat(),
    "count":      len(all_props),
    "properties": all_props
}))
