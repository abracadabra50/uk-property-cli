# UK Property CLI - Audit & 10x Improvement Plan

## Part 1: Code Audit Findings

### Critical Issues

#### 1. Massive Code Duplication Across Parsers
**Files:** `parsers/espc.py`, `parsers/rightmove.py`, `parsers/zoopla.py`

All three parsers copy-paste identical code:
- `BAD_AREAS` list (11 items, duplicated 3x)
- `is_bad_area()` function (duplicated 3x)
- `categorize()` function (duplicated 3x)
- `parse_price()` function (duplicated in espc.py and zoopla.py)
- `BEDS = sys.argv[1]` global state (duplicated 3x)
- Postcode regex `(EH\d+\s*\d*\w*)` (duplicated 3x)
- Output JSON envelope construction (duplicated 3x)

This is the single biggest maintainability problem. Changing excluded areas means editing 3 files.

#### 2. preferences.json Is Created But Never Used
`setup.py` writes a full configuration file with areas, price ranges, scoring weights, etc. - but **no parser, filter, or tool ever reads it**. The preferences system is completely disconnected from the actual tools. All configuration is hardcoded in each script independently.

#### 3. Hardcoded to Edinburgh
- Postcode regex only matches `EH\d+` (Edinburgh postcodes)
- BAD_AREAS only lists Edinburgh neighborhoods
- DESIRED_AREAS in filter.py only has Edinburgh postcodes
- Rightmove uses `REGION^550` (Edinburgh) hardcoded
- ESPC URL is Edinburgh-specific
- Zoopla URL is Edinburgh-specific
- The README advertises "UK-wide" but the tool only works for Edinburgh

#### 4. Unstable Zoopla Property IDs
`zoopla.py:92` uses `hash(address)` for IDs. Python's `hash()` is **not deterministic across runs** (randomized by default since Python 3.3). This means:
- `compare.py` will never find matching IDs between runs
- Deduplication by ID is broken for Zoopla
- Daily comparisons are meaningless for Zoopla properties

#### 5. No Error Handling for Network Failures
- `curl` failures return empty strings, silently parsed as "0 properties found"
- No HTTP status code checking
- No retry logic
- No timeout on ESPC parser (Rightmove has 15s, Zoopla 30s, ESPC has none)
- `fetch.sh` uses `2>/dev/null` which **swallows all error messages**

### Major Issues

#### 6. O(n^2) Deduplication Algorithm
`dedupe.py` compares every property against every other property using `SequenceMatcher`. For 100 properties: 4,950 comparisons. For 500: 124,750. For 1000: 499,500. Each comparison runs the full SequenceMatcher algorithm. This will not scale.

#### 7. No Input Validation
- `BEDS` from argv is passed directly to URLs without validation (potential injection in shell via fetch.sh)
- No numeric range checking on prices
- No validation that JSON files have expected structure
- `setup.py` accepts arbitrary float for threshold with no bounds checking

#### 8. Deprecated API Usage
All parsers use `datetime.utcnow()` which is deprecated since Python 3.12. Should use `datetime.now(timezone.utc)`.

#### 9. Global Mutable State
`BEDS = sys.argv[1]` at module level in all parsers means:
- Can't import parsers as libraries
- Can't run multiple searches with different params
- Testing requires monkeypatching sys.argv

### Minor Issues

#### 10. Inconsistent Type Annotations
- `dedupe.py`, `filter.py`, `compare.py` use type hints
- All three parsers have zero type hints
- No runtime type checking anywhere

#### 11. Single Page Only
All parsers fetch only the first page of results. For 4-bed Edinburgh searches this might be fine (~25 results), but for broader searches or more common configurations (2-bed flats), this misses most results.

#### 12. No Logging
All diagnostic output goes to `stderr` via `print()`. No log levels, no ability to enable/disable debug output, no structured logging.

#### 13. fetch.sh Combines JSON Unsafely
`fetch.sh` lines 70-78 use inline Python to combine files. If any portal fails and produces invalid JSON, the entire `all` command fails silently.

---

## Part 2: 10x Improvement Plan

### Phase 1: Foundation - Eliminate Duplication & Wire Up Config
**Goal:** DRY code, make preferences.json actually work, fix critical bugs

#### Step 1.1: Create shared module `parsers/base.py`
- Extract `BAD_AREAS`, `is_bad_area()`, `categorize()`, `parse_price()` into shared module
- Create `Property` dataclass with all fields
- Create `PortalResult` dataclass for the JSON envelope
- Create `BaseParser` abstract class with `fetch()`, `parse()`, `to_json()` methods
- Add shared `build_output()` function for consistent JSON envelope

#### Step 1.2: Refactor all parsers to use shared module
- `espc.py`: Import from base, remove duplicated code (~40% reduction)
- `rightmove.py`: Import from base, remove duplicated code (~40% reduction)
- `zoopla.py`: Import from base, remove duplicated code (~40% reduction)
- Each parser only contains portal-specific fetch + parse logic

#### Step 1.3: Wire up preferences.json
- Create `config.py` module that loads preferences.json
- Make parsers read excluded areas from preferences (not hardcoded)
- Make filter.py read desired/excluded areas from preferences
- Make categorize() thresholds configurable
- Make search URLs use location from preferences (not hardcoded Edinburgh)
- Fall back to sensible defaults when preferences.json doesn't exist

#### Step 1.4: Fix Zoopla ID stability
- Replace `hash()` with `hashlib.md5(address.encode()).hexdigest()[:8]`
- Deterministic across Python versions and runs

#### Step 1.5: Fix deprecated datetime usage
- Replace `datetime.utcnow()` with `datetime.now(timezone.utc)` everywhere

### Phase 2: Robustness - Error Handling & Resilience
**Goal:** Graceful failures, retries, validation

#### Step 2.1: Add HTTP error handling to parsers
- Check curl exit codes and HTTP status codes
- Add retry logic (3 attempts with exponential backoff)
- Add configurable timeout to all parsers (ESPC currently has none)
- Return structured error info instead of empty results

#### Step 2.2: Graceful degradation in fetch.sh
- Remove `2>/dev/null` - show parser errors
- If one portal fails, still combine results from the others
- Report which portals succeeded/failed in output
- Validate JSON before combining

#### Step 2.3: Input validation
- Validate BEDS is a positive integer
- Validate price ranges are sensible
- Validate JSON structure on load (check required fields exist)
- Sanitize all user inputs before using in URLs

#### Step 2.4: Make parsers importable as libraries
- Move `sys.argv` parsing into `main()` only
- Accept parameters as function arguments
- Enable `from parsers.rightmove import RightmoveParser` usage

### Phase 3: Performance & Scale
**Goal:** Handle larger datasets, add pagination, optimize dedup

#### Step 3.1: Optimize deduplication
- First pass: group by postcode (O(n) bucketing)
- Only run SequenceMatcher within same postcode bucket
- Reduces comparisons dramatically (e.g., 500 properties / 20 postcodes = ~25 per bucket)
- Add postcode normalization for consistent bucketing

#### Step 3.2: Add pagination support
- ESPC: Fetch pages until no more results (page=1, page=2...)
- Rightmove: Follow `pagination.next` in JSON data
- Zoopla: Increment page parameter
- Add `--max-pages` flag to limit API calls
- Default to page 1 for backward compatibility

#### Step 3.3: Add location configurability to URLs
- Rightmove: Map city names to REGION IDs (Edinburgh=550, Manchester=904, London=87490...)
- ESPC: Only works for Edinburgh/Scotland - skip for other locations
- Zoopla: Use city name in URL path
- Read location from preferences.json

### Phase 4: Testing & Quality
**Goal:** Confidence in changes, catch regressions

#### Step 4.1: Add unit tests
- Test `normalize_address()` with edge cases
- Test `addresses_match()` with known duplicates and non-duplicates
- Test `categorize()` with boundary values
- Test `parse_price()` with various formats (£550,000 / 550000 / "POA")
- Test `filter_properties()` with various filter combinations
- Test `compare_snapshots()` with known diffs
- Test Zoopla ID generation is deterministic

#### Step 4.2: Add parser tests with fixtures
- Save sample HTML responses as test fixtures
- Test each parser against fixture data (no network required)
- Test graceful handling of malformed/changed HTML
- Test empty response handling

#### Step 4.3: Add integration test
- End-to-end test: fetch -> dedupe -> filter -> compare pipeline
- Use mock HTTP responses
- Verify output JSON schema

#### Step 4.4: Add code quality tooling
- Add `pyproject.toml` with project metadata
- Configure `ruff` for linting + formatting
- Add type hints to all functions
- Run `mypy` for type checking

### Phase 5: Feature Completions - Actually 10x the Value
**Goal:** Implement the features that make this genuinely powerful

#### Step 5.1: Property scoring engine
- Implement the scoring system that preferences.json already defines weights for
- Score by: area (premium/excellent/good), price (distance from ideal range), features (beds, baths, images), multi-portal presence
- Add `score.py` tool: `./fetch.sh score cache/all.json` -> sorted + scored properties
- Rank properties by composite score

#### Step 5.2: SQLite persistence layer
- Store fetched properties in SQLite database
- Track price history over time (not just yesterday vs today)
- Enable queries like "show me all price drops in the last 30 days"
- Store fetch metadata (when, which portal, how many)
- Enable `compare.py` to work without manual file management

#### Step 5.3: Multi-location support
- Remove Edinburgh hardcoding throughout
- Add location registry mapping city names to portal-specific IDs/URLs
- Support multiple saved searches (Edinburgh 4-bed houses + Glasgow 2-bed flats)
- ESPC: Edinburgh/Lothians only (skip gracefully for other cities)

#### Step 5.4: Postcode regex generalization
- Replace `EH\d+` with UK-wide postcode regex
- Pattern: `[A-Z]{1,2}\d[A-Z\d]?\s*\d[A-Z]{2}`
- Works for all UK postcodes (EH, G, M, SW, EC, etc.)

#### Step 5.5: Proper Python packaging
- Create `pyproject.toml` with dependencies, entry points, metadata
- Add `__init__.py` files for proper package structure
- Create CLI entry point: `uk-property fetch all --beds 4`
- Enable `pip install .` for local development
- Enable future PyPI publishing

---

## Implementation Order & Dependencies

```
Phase 1 (Foundation) - must be done first
  1.1 -> 1.2 (shared module before refactor)
  1.3 (can parallel with 1.2)
  1.4, 1.5 (independent, can parallel)

Phase 2 (Robustness) - after Phase 1
  2.1 -> 2.2 (parser errors before fetch.sh)
  2.3, 2.4 (independent)

Phase 3 (Performance) - after Phase 2
  3.1, 3.2, 3.3 (all independent)

Phase 4 (Testing) - can start after Phase 1
  4.1 -> 4.2 -> 4.3 (build up test coverage)
  4.4 (independent)

Phase 5 (Features) - after Phase 1-2
  5.1 (independent)
  5.2 (independent)
  5.3 depends on 1.3
  5.4 (independent, small)
  5.5 depends on most other work being done
```

## Summary of Impact

| What | Before | After |
|------|--------|-------|
| Duplicated code | ~120 lines across 3 parsers | 0 (shared module) |
| Config usage | preferences.json never read | Drives all behavior |
| Location support | Edinburgh only | Any UK city |
| Error handling | Silent failures | Retries + graceful degradation |
| Zoopla IDs | Non-deterministic | Stable (hashlib) |
| Dedup performance | O(n^2) | O(n) bucketed |
| Test coverage | 0% | Core logic covered |
| Property scoring | Weights defined, never used | Full scoring engine |
| Data persistence | Flat JSON files | SQLite with history |
| Pagination | First page only | All pages |
| Packaging | Loose scripts | pip-installable package |
