---
name: edinburgh-property
description: Fetch property listings from Edinburgh portals (ESPC, Rightmove, Zoopla). Returns structured JSON for investment opportunities and family homes. Filters out undesirable areas automatically.
---

# Edinburgh Property Search Skill

Fetch property listings from multiple UK property portals with Edinburgh area filtering built in.

## Usage

```bash
# Fetch from single portal
bash {baseDir}/fetch.sh espc 4

# Fetch from all portals
bash {baseDir}/fetch.sh all 4

# Get formatted briefing
bash {baseDir}/briefing.sh
```

## Output Format

```json
{
  "portal": "espc",
  "fetched_at": "2026-02-16T01:48:00Z",
  "count": 12,
  "properties": [
    {
      "id": "36362802",
      "portal": "espc",
      "title": "End Terraced House",
      "price": 450000,
      "price_text": "Offers Over £450,000",
      "beds": 4,
      "baths": 2,
      "property_type": "terraced",
      "address": "1 Buckstone Circle",
      "area": "Buckstone",
      "postcode": "EH10 6XB",
      "description": "Located within the sought after Buckstone area...",
      "url": "https://espc.com/property/...",
      "image_url": "https://...",
      "images": ["https://..."],
      "features": ["Garden", "Parking"],
      "category": "family"
    }
  ]
}
```

## Supported Portals

### ESPC (Edinburgh Specialist)
- Status: ✅ Implemented
- Data Source: Native curl + Python parsing (zero dependencies)
- Coverage: Edinburgh & Lothians
- Update Frequency: Real-time
- Future: Extract embedded JSON for faster parsing

### Rightmove
- Status: ⚠️ Stub (ready to implement)
- Data Source: TBD (HTML or API)
- Coverage: UK-wide
- Future: Reverse engineer internal API

### Zoopla  
- Status: ⚠️ Stub (ready to implement)
- Data Source: TBD (HTML or API)
- Coverage: UK-wide
- Future: Reverse engineer internal API

## Area Filtering

Automatically excludes:
- Moredun, Niddrie, Wester Hailes
- Sighthill, Muirhouse, Pilton
- Kirkliston (not Edinburgh proper)
- Musselburgh, Dalkeith (outlying)
- Granton, Liberton

Includes desirable areas:
- City Centre, Stockbridge, Marchmont
- Morningside, Bruntsfield, Colinton
- Corstorphine, Cramond, Blackhall
- Trinity, Portobello, Leith (waterfront)

## Categories

Properties are auto-categorized:

**Investment:**
- Price < £250k
- Needs renovation
- Auction properties
- High rental yield potential

**Family:**
- 4+ bedrooms
- Garden space
- Good school catchment
- Office/study room

## Integration

### Daily Briefing
```bash
# Called by periodic event at 9am
bash {baseDir}/briefing.sh
```

### Manual Search
```bash
# Get all 4-bed properties
bash {baseDir}/fetch.sh all 4 | jq '.properties[] | {price, address, url}'
```

## Future Enhancements

### Phase 1 (Current)
- ✅ ESPC HTML scraping
- ✅ Area filtering
- ✅ JSON output format
- ⚠️ Rightmove/Zoopla stubs

### Phase 2 (Next)
- Extract ESPC embedded JSON (faster)
- Implement Rightmove fetcher
- Implement Zoopla fetcher
- Cache results (1 hour TTL)

### Phase 3 (Future)
- Reverse engineer portal APIs
- Real-time alerts on new listings
- Price tracking & history
- Investment analysis (yield, ROI)
- School catchment data
- Commute time calculations

## Files

```
{baseDir}/
├── SKILL.md           # This file
├── fetch.sh           # Main fetcher script
├── briefing.sh        # Daily briefing formatter
├── parsers/
│   ├── espc.py       # ESPC parser
│   ├── rightmove.py  # Rightmove parser (TODO)
│   └── zoopla.py     # Zoopla parser (TODO)
└── cache/            # Cached results
```

## Dependencies

**Zero external dependencies!**

- `curl` - Built-in HTTP client
- `python3` - Built-in (for parsing)
- `jq` - Optional (JSON formatting only)

All tools are standard on macOS/Linux. No npm packages, no API keys, no costs.

## Notes

This skill is designed to be extended. Each portal fetcher is isolated, making it easy to:
1. Add new portals
2. Switch from HTML scraping to API calls
3. Improve parsers without affecting others

Perfect foundation for `uk-property-cli` if we decide to build it as a product.
