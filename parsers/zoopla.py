#!/usr/bin/env python3
"""
Zoopla Property Parser — Playwright-based (no external API dependencies)
Uses headless Chromium to bypass Cloudflare, extracts listings from rendered DOM.
Requires: playwright installed in /Users/zish/gaffer-test/
"""

import sys, json, subprocess, re, os
from datetime import datetime, timezone

BEDS      = sys.argv[1] if len(sys.argv) > 1 else "4"
MAX_PRICE = sys.argv[2] if len(sys.argv) > 2 else "700000"
PLAYWRIGHT_DIR = "/Users/zish/gaffer-test"

BAD_AREAS = [
    "Moredun", "Niddrie", "Wester Hailes", "Sighthill",
    "Muirhouse", "Pilton", "Kirkliston", "Granton"
]

JS = r"""
async () => {
  const rows = document.querySelectorAll('[id^="listing_"]');
  const results = [];
  
  for (const row of rows) {
    const id = row.id.replace('listing_', '');
    
    // Address
    const textEls = row.querySelectorAll('address, h2, h3, [class*="address"], [class*="Address"]');
    let address = '';
    for (const el of textEls) {
      const t = el.textContent.trim();
      if (t.match(/EH\d+/) || t.match(/Edinburgh/i)) { address = t; break; }
    }
    if (!address) {
      const link = row.querySelector('a[aria-label]');
      address = link?.getAttribute('aria-label') || '';
    }
    
    // Price — clean "See monthly cost" etc
    const priceEl = row.querySelector('[class*="price"], [class*="Price"]');
    let priceRaw = (priceEl?.textContent || '').replace(/See monthly cost.*/gi, '').trim();
    priceRaw = priceRaw.replace(/\s+/g, ' ').trim();
    const priceNum = parseInt((priceRaw.match(/[\d,]+/) || ['0'])[0].replace(/,/g, ''));
    let qualifier = '';
    if (/Offers over/i.test(priceRaw)) qualifier = 'Offers over';
    else if (/Fixed price/i.test(priceRaw)) qualifier = 'Fixed price';
    else if (/Offers in excess/i.test(priceRaw)) qualifier = 'Offers in excess';
    else if (/Guide price/i.test(priceRaw)) qualifier = 'Guide price';
    const priceText = qualifier ? `${qualifier} £${priceNum.toLocaleString('en-GB')}` : `£${priceNum.toLocaleString('en-GB')}`;
    
    // Beds/baths
    const txt = row.textContent;
    const bedsM = txt.match(/(\d+)\s*bed/);
    const bathsM = txt.match(/(\d+)\s*bath/);
    const beds = bedsM ? parseInt(bedsM[1]) : 0;
    const baths = bathsM ? parseInt(bathsM[1]) : 0;
    
    // URL
    const linkEl = row.querySelector('a[href*="details"]');
    const url = linkEl ? 'https://www.zoopla.co.uk' + linkEl.getAttribute('href') : '';
    
    // Image — prefer JPEG source (not WebP :p variant)
    const sources = row.querySelectorAll('source[srcset*="lid.zoocdn"]');
    let imgUrl = '';
    for (const src of sources) {
      const srcset = src.getAttribute('srcset') || '';
      const type = src.getAttribute('type') || '';
      if (type.includes('jpeg') || !type.includes('webp')) {
        const match = srcset.match(/(https:\/\/lid\.zoocdn\.com\/645\/430\/[^\s,]+\.jpg)/);
        if (match) { imgUrl = match[1]; break; }
      }
    }
    if (!imgUrl) {
      // Fallback: any zoocdn URL
      const m = row.innerHTML.match(/https:\/\/lid\.zoocdn\.com\/645\/430\/[^"':]+\.jpg/);
      if (m) imgUrl = m[0];
    }
    
    // Postcode
    const pcM = address.match(/\b(EH\d+\s*\d*[A-Z]*)\b/i);
    const postcode = pcM ? pcM[1].toUpperCase() : '';
    
    if (id && beds >= 1) {
      results.push({ id, address, price: priceNum, priceRaw, priceText, beds, baths, postcode, url, image_url: imgUrl });
    }
  }
  
  // Dedupe by ID
  const seen = new Set();
  return results.filter(p => {
    if (seen.has(p.id)) return false;
    seen.add(p.id);
    return true;
  });
}
"""

JS_SCRIPT = f"""
const {{ chromium }} = require('playwright');
const BEDS = '{BEDS}';
const MAX_PRICE = '{MAX_PRICE}';
const BAD_AREAS = {json.dumps(BAD_AREAS)};

(async () => {{
  const browser = await chromium.launch({{ headless: true }});
  const ctx = await browser.newContext({{
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    locale: 'en-GB',
    viewport: {{ width: 1280, height: 800 }}
  }});
  const page = await ctx.newPage();
  
  const url = `https://www.zoopla.co.uk/for-sale/property/edinburgh/?beds_min=${{BEDS}}&results_sort=newest_listings`;
  
  try {{
    await page.goto(url, {{ waitUntil: 'networkidle', timeout: 45000 }});
  }} catch(e) {{
    // networkidle may timeout on heavy pages — content is usually there
  }}
  
  const raw = await page.evaluate({JS});
  
  // Filter + categorize in JS before returning
  const filtered = raw.filter(p => {{
    if (p.price > parseInt(MAX_PRICE)) return false;
    if (BAD_AREAS.some(b => p.address.toLowerCase().includes(b.toLowerCase()))) return false;
    const isEH = /\\bEH\\d+\\b/i.test(p.address);
    return isEH;
  }}).map(p => ({{
    ...p,
    title: `${{p.beds}}-bed property`,
    price_text: p.priceText || p.priceRaw,
    property_type: 'property',
    features: [],
    images: p.image_url ? [p.image_url] : [],
    portal: 'zoopla',
    category: p.price < 250000 ? 'investment' : (p.beds >= 4 ? 'family' : 'other')
  }}));
  
  const output = {{
    portal: 'zoopla',
    fetched_at: new Date().toISOString(),
    count: filtered.length,
    properties: filtered
  }};
  
  console.log(JSON.stringify(output));
  await browser.close();
}})().catch(e => {{
  console.error(JSON.stringify({{ portal: 'zoopla', error: e.message, properties: [] }}));
  process.exit(1);
}});
"""

# Write temp JS file and run it
tmp_js = "/Users/zish/gaffer-test/zoopla_parser.js"
with open(tmp_js, 'w') as f:
    f.write(JS_SCRIPT)

result = subprocess.run(
    ["node", tmp_js],
    capture_output=True, text=True,
    cwd=PLAYWRIGHT_DIR,
    timeout=90
)

if result.returncode != 0:
    sys.stderr.write(result.stderr)
    print(json.dumps({"portal": "zoopla", "error": result.stderr[-200:], "properties": []}))
else:
    # Print the JSON output
    output = result.stdout.strip()
    print(output)
