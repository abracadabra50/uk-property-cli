# uk-property-cli

Edinburgh property search CLI — zero external API dependencies.

Fetches 4-bed+ listings from ESPC, Rightmove, and Zoopla. Filters to Edinburgh postcodes (EH1–EH55), deduplicates by address similarity, and detects genuinely new listings across days.

## Portals

| Portal | Status | Props/day | Method | Notes |
|--------|--------|-----------|--------|-------|
| ESPC | ✅ Working | 10–12 | curl + regex | Scotland's solicitor portal |
| Rightmove | ✅ Working | 24 | curl + JSON parse | Region 475 = Edinburgh |
| Zoopla | ✅ Working | 20 | Playwright (headless Chrome) | Cloudflare-protected |
| OnTheMarket | ⛔ Blocked | 0 | — | 303 redirect + empty headless response |

## Requirements

- Python 3.x (stdlib only for ESPC + Rightmove)
- Node.js + Playwright (`npm i playwright` in working dir for Zoopla)
- Chromium browsers installed: `npx playwright install chromium`

Playwright working dir expected at `/Users/zish/gaffer-test` (has `playwright` in node_modules).

## Parsers

```bash
# Each parser outputs normalized JSON to stdout
python3 parsers/espc.py 4               # min 4 beds
python3 parsers/rightmove.py 4          # min 4 beds
python3 parsers/zoopla.py 4 700000      # min 4 beds, max price
```

## Pipeline

```bash
# 1. Fetch all portals
python3 parsers/espc.py 4      > /tmp/espc.json
python3 parsers/rightmove.py 4 > /tmp/rm.json
python3 parsers/zoopla.py 4    > /tmp/zoopla.json

# 2. Merge, EH-filter, dedupe, compare vs yesterday
# (Agent handles this — see new_listings.py for address fingerprint logic)
```

## Output Format

```json
{
  "portal": "espc|rightmove|zoopla",
  "fetched_at": "2026-03-27T09:00:00Z",
  "count": 10,
  "properties": [{
    "id": "...",
    "price": 450000,
    "price_text": "Offers Over £450,000",
    "beds": 4,
    "address": "1 Example Street, Edinburgh EH12",
    "postcode": "EH12 5XX",
    "norm_addr": "1 example st edinburgh eh12 5xx",
    "url": "...",
    "image_url": "...",
    "images": ["..."],
    "portal": "espc",
    "category": "family|investment|other"
  }]
}
```

## Key Files

- `parsers/` — one file per portal
- `new_listings.py` — cross-day new-listing detection (address similarity, 0.82 threshold)
- `dedupe.py` — within-day address dedup (0.85 threshold)
- `filter.py` — EH postcode + area filtering
- `preferences.json` — search config (postcodes, budget, excluded areas)

## Architecture

The CLI is tools only — it outputs JSON. The agent (Pal) orchestrates fetch → filter → dedupe → compare → format and posts to Slack.

New portal = new file in `parsers/`. Match the output schema above.
