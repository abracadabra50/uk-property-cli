# Edinburgh Property Search

Multi-portal property search for Edinburgh with area filtering and categorization.

**Zero dependencies** - uses only `curl` and `python3` (built-in tools).

## Features

- ✅ Multi-portal support (ESPC, Rightmove, Zoopla)
- ✅ Normalized JSON output
- ✅ Edinburgh area filtering (excludes bad areas automatically)
- ✅ Property categorization (investment vs family)
- ✅ Zero external dependencies
- ✅ Modular parser design (easy to extend)

## Usage

```bash
# Fetch from single portal
./fetch.sh espc 4

# Fetch from all portals
./fetch.sh all 4
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
      "url": "https://espc.com/property/...",
      "image_url": "https://...",
      "category": "family"
    }
  ]
}
```

## Supported Portals

### ESPC (Edinburgh Specialist)
- Status: ✅ **Working**
- Data Source: curl + Python HTML parsing
- Coverage: Edinburgh & Lothians

### Rightmove
- Status: ⚠️ **Framework ready**
- Data Source: curl + Python (JSON extraction needs refinement)
- Coverage: UK-wide

### Zoopla  
- Status: ⚠️ **Framework ready**
- Data Source: curl + Python (needs implementation)
- Coverage: UK-wide

## Area Filtering

Automatically excludes undesirable areas:
- Moredun, Niddrie, Wester Hailes
- Sighthill, Muirhouse, Pilton
- Kirkliston, Musselburgh, Dalkeith

Focuses on desirable Edinburgh areas:
- City Centre, Stockbridge, Marchmont
- Morningside, Bruntsfield, Colinton
- Corstorphine, Cramond, Portobello

## Architecture

```
edinburgh-property/
├── fetch.sh          # Main fetcher (portal dispatcher)
├── parsers/
│   ├── espc.py      # ESPC implementation ✅
│   ├── rightmove.py # Rightmove framework ⚠️
│   └── zoopla.py    # Zoopla framework ⚠️
└── cache/           # Cache directory
```

Each parser is isolated - add new portals by creating new parser files.

## Dependencies

**None!** Only uses standard tools:
- `curl` - Built-in HTTP client
- `python3` - Built-in (for parsing)
- `bash` - Built-in (orchestration)

Works on any Mac/Linux system out of the box.

## Categories

Properties are auto-categorized:

**Investment:**
- Price < £250k
- Needs renovation
- High rental yield potential

**Family:**
- 4+ bedrooms
- Garden space
- Good areas

## Extending

To add a new portal:

1. Create `parsers/newportal.py`
2. Implement `fetch_page()` and `parse_properties()`
3. Return normalized JSON format
4. Done! `fetch.sh all` will include it

## Future Improvements

- [ ] Improve Rightmove JSON extraction
- [ ] Implement Zoopla parser
- [ ] Add caching layer
- [ ] Reverse engineer portal APIs
- [ ] Add price tracking
- [ ] Add investment metrics (yield, ROI)

## Use Cases

- Daily property briefings
- Investment opportunity scanning
- Market analysis
- Price tracking
- Foundation for larger property CLI tool

## License

Private - for personal use

---

Built with zero dependencies for maximum portability and zero costs.
