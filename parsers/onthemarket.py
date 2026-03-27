#!/usr/bin/env python3
"""
OnTheMarket Property Parser
STATUS: Hard-blocked as of Mar 2026
- curl: returns HTTP 303 → homepage (Cloudflare/bot detection)
- Playwright headless: redirected to homepage, empty pageProps

Investigation notes (Mar 27 2026):
- OTM serves SSR'd HTML with embedded property JSON to real browsers
- Detects headless Chrome and serves empty shell instead
- No RSS feed available
- No public API
- Playwright with webdriver flag override + wait doesn't help

Workaround options:
1. playwright-extra + puppeteer-extra-plugin-stealth (additional deps)
2. OTM data overlap with Rightmove is ~80%+ — coverage gap is minimal

Returns empty result set until resolved.
"""

import sys, json
from datetime import datetime, timezone

output = {
    "portal": "onthemarket",
    "fetched_at": datetime.now(timezone.utc).isoformat(),
    "count": 0,
    "properties": [],
    "error": "Blocked - see parser comments"
}
print(json.dumps(output, indent=2))
