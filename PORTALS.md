# UK Property Portals - Implementation Analysis

**Date:** 2026-02-16  
**Purpose:** Rank property portals for parser implementation  
**Criteria:** Traffic/usage × difficulty × data quality

---

## Portal Rankings

### Tier 1 - Essential (High Traffic, Worth Doing)

#### 1. Rightmove 🥇
- **Monthly visitors:** ~135 million (UK's largest property portal)
- **Market share:** ~80% of UK property listings
- **Listings:** ~1.5 million properties
- **Coverage:** Nationwide, all property types
- **Data quality:** Excellent (detailed specs, multiple photos, floor plans)
- **Implementation difficulty:** Medium
  - Embeds JSON in HTML (found in our test)
  - No official API for public use
  - Some anti-scraping (rate limits likely)
- **Worth it?** **ABSOLUTELY** - Dominates UK market
- **Status:** Framework ready, needs JSON extraction refinement

#### 2. Zoopla 🥈
- **Monthly visitors:** ~60 million
- **Market share:** ~50% of UK listings (overlap with Rightmove)
- **Listings:** ~750k properties
- **Coverage:** Nationwide, strong in London
- **Data quality:** Excellent (price history, sold prices, area stats)
- **Unique features:** 
  - Sold price data
  - Area statistics (average prices, trends)
  - Rental yield estimates
- **Implementation difficulty:** Medium
  - Similar to Rightmove (embedded data)
  - Used to have API (now deprecated)
- **Worth it?** **YES** - 2nd largest, unique data (sold prices)
- **Status:** Framework ready, needs implementation

#### 3. OnTheMarket 🥉
- **Monthly visitors:** ~14 million
- **Market share:** ~10-15% of UK listings
- **Listings:** ~150k properties
- **Coverage:** Nationwide, premium/high-end focus
- **Data quality:** Good (fewer photos than Rightmove/Zoopla)
- **Unique angle:** Agent-owned, some exclusive listings
- **Implementation difficulty:** Medium
- **Worth it?** **MAYBE** - Smaller but has exclusive listings
- **Status:** Not started

---

### Tier 2 - Regional Specialists (High Value for Specific Areas)

#### 4. ESPC (Edinburgh Solicitors Property Centre)
- **Monthly visitors:** ~1-2 million
- **Market share:** Dominates Edinburgh & Lothians (~70% local)
- **Listings:** ~2-3k properties (Edinburgh focus)
- **Coverage:** Edinburgh, East Lothian, Midlothian, West Lothian
- **Data quality:** Excellent (legal pack links, detailed specs)
- **Unique features:**
  - Scottish Home Reports included
  - Legal pack downloads
  - Edinburgh-specific area knowledge
- **Implementation difficulty:** Medium (HTML parsing)
- **Worth it?** **YES** - Best for Edinburgh
- **Status:** ✅ **DONE** - 100% functional

#### 5. S1 Homes (Scotland)
- **Monthly visitors:** ~800k
- **Market share:** Strong in Scotland (outside Edinburgh)
- **Listings:** ~15k properties (Scotland-wide)
- **Coverage:** Scotland (Glasgow, Aberdeen, Dundee, Highlands)
- **Data quality:** Good
- **Implementation difficulty:** Medium
- **Worth it?** **IF** expanding beyond Edinburgh
- **Status:** Not started

#### 6. ASPC (Aberdeen Solicitors Property Centre)
- **Monthly visitors:** ~500k
- **Market share:** Dominates Aberdeen & Aberdeenshire (~60% local)
- **Listings:** ~1-2k properties (Aberdeen focus)
- **Coverage:** Aberdeen, Aberdeenshire, North East Scotland
- **Platform:** Different from ESPC (not reusable)
- **Implementation difficulty:** Medium (separate parser needed)
- **Worth it?** **ONLY IF** expanding to Aberdeen
- **Status:** Not started

#### 7. SLPC (Scottish Borders Property Centre)
- **Monthly visitors:** ~200k
- **Market share:** Scottish Borders region
- **Platform:** Different from ESPC (not reusable)
- **Worth it?** **NO** - Too niche
- **Status:** Skip

#### 8. Nethouseprice.com / Property.scot
- **Monthly visitors:** Low
- **Market share:** Niche (Scottish property data)
- **Unique features:** Scottish sold price data, market trends
- **Worth it?** **MAYBE** - For data enrichment only
- **Status:** Not started

---

### Tier 3 - Niche/Specialist (Lower Priority)

#### 7. PrimeLocation
- **Monthly visitors:** ~5 million
- **Market share:** ~5% (merged with Zoopla in 2018)
- **Coverage:** Overlaps heavily with Zoopla
- **Worth it?** **NO** - Redundant with Zoopla
- **Status:** Skip

#### 8. Boomin
- **Monthly visitors:** ~2 million (declining)
- **Market share:** ~2-3%
- **Status:** Struggling, may shut down
- **Worth it?** **NO** - Unstable platform
- **Status:** Skip

#### 9. Purplebricks
- **Monthly visitors:** ~3 million
- **Coverage:** Online estate agent, lists on Rightmove/Zoopla
- **Worth it?** **NO** - Redundant (listings appear on R/Z)
- **Status:** Skip

#### 10. Propertypal (Northern Ireland)
- **Monthly visitors:** ~1 million
- **Coverage:** Northern Ireland only
- **Worth it?** **NO** - Out of scope (we're Edinburgh-focused)
- **Status:** Skip

---

## Recommended Implementation Order

### Phase 1: Core Coverage (Done ✅)
1. ✅ **ESPC** - Edinburgh specialist (DONE)
2. ⚠️ **Rightmove** - UK coverage (Framework ready, needs 1-2 hours)
3. ⚠️ **Zoopla** - UK coverage + sold prices (Framework ready, needs 1-2 hours)

### Phase 2: Enrich Data (Future)
4. **OnTheMarket** - Exclusive listings
5. **S1 Homes** - Scotland beyond Edinburgh

### Phase 3: Data Enrichment (Future)
6. **Zoopla sold prices API** (if accessible)
7. **Property.scot** - Scottish market data

---

## Difficulty Assessment

### Easy (1-2 hours each)
- ESPC ✅ (Done)
- S1 Homes (similar to ESPC)

### Medium (2-4 hours each)
- Rightmove (JSON extraction, testing, edge cases)
- Zoopla (similar to Rightmove)
- OnTheMarket (HTML structure analysis needed)

### Hard (4-8 hours each)
- Building anti-scraping bypasses (if needed)
- Reverse engineering private APIs
- Handling CAPTCHAs or bot detection

---

## Traffic Sources (Estimated Monthly)

| Portal | Monthly Visits | Market Share | Listings |
|--------|---------------|--------------|----------|
| Rightmove | 135M | 80% | 1.5M |
| Zoopla | 60M | 50% | 750k |
| OnTheMarket | 14M | 15% | 150k |
| PrimeLocation | 5M | 5% | (Zoopla) |
| Boomin | 2M | 2% | 40k |
| ESPC | 1-2M | 70% (Edin) | 2-3k |
| S1 Homes | 800k | 30% (Scot) | 15k |

---

## ROI Analysis

**For Edinburgh property search:**
- **ESPC**: ✅ Essential (done)
- **Rightmove**: ✅ Essential (80% UK coverage)
- **Zoopla**: ✅ High value (sold prices, trends)
- **OnTheMarket**: ⚠️ Nice to have (exclusive listings)
- **S1 Homes**: ❌ Skip (ESPC covers Edinburgh)

**Time investment:**
- Phase 1 (ESPC + Rightmove + Zoopla): 4-6 hours total
  - ESPC: ✅ Done (2 hours)
  - Rightmove: 1-2 hours
  - Zoopla: 1-2 hours

**Return:**
- Coverage of 90%+ of UK property market
- Edinburgh specialist coverage (ESPC)
- Sold price data (Zoopla)
- 3 independent sources for cross-validation

---

## Technical Approach

### Rightmove Implementation
**Status:** Framework ready (parser stub exists)

**Data extraction:**
- Embedded JSON in HTML (confirmed)
- Pattern: `window.__PRELOADED_STATE__` or similar
- Extract property array from JSON blob

**Estimated time:** 1-2 hours

**Steps:**
1. Fetch page with curl
2. Extract JSON blob from HTML
3. Parse properties array
4. Map to normalized format
5. Apply area filtering
6. Test with multiple searches

---

### Zoopla Implementation
**Status:** Framework ready (parser stub exists)

**Data extraction:**
- Similar to Rightmove (React app with embedded data)
- Pattern analysis needed

**Unique features to extract:**
- Sold prices (if available)
- Area statistics
- Rental yield estimates

**Estimated time:** 1-2 hours

**Steps:**
1. Analyze HTML structure (curl page)
2. Find embedded JSON pattern
3. Extract properties + sold price data
4. Map to normalized format
5. Test

---

## Commercial Opportunity

**If building uk-property-cli as a product:**

**Most valuable portals:**
1. Rightmove (must-have for credibility)
2. Zoopla (sold prices = competitive advantage)
3. OnTheMarket (exclusive listings)
4. Regional specialists (ESPC, S1, etc) for local credibility

**Differentiators:**
- Multi-portal aggregation
- Normalized data format
- Area filtering/intelligence
- Investment metrics (yield, ROI)
- Alert system (new properties matching criteria)

**Potential pricing:**
- Free tier: ESPC only (Edinburgh)
- Pro tier: All major portals (Rightmove, Zoopla, OnTheMarket)
- Enterprise: API access, custom integrations

---

## Recommendation

**Next steps:**

1. **Implement Rightmove parser** (1-2 hours)
   - Highest ROI: 80% UK market
   - Framework already exists
   - JSON extraction is straightforward

2. **Implement Zoopla parser** (1-2 hours)
   - Second highest ROI: sold prices
   - Similar difficulty to Rightmove
   - Adds cross-validation

3. **Ship Phase 1** (ESPC + Rightmove + Zoopla)
   - 90%+ UK coverage
   - Edinburgh specialist (ESPC)
   - Sold price data (Zoopla)
   - Multiple sources for validation

4. **Monitor usage** before building more
   - See which portals users actually care about
   - Measure data quality differences
   - Identify gaps (exclusive listings, etc)

**Total time to Phase 1 completion:** 2-4 hours (Rightmove + Zoopla)

**Value unlocked:**
- Comprehensive UK property search
- Edinburgh specialist coverage
- Multi-source validation
- Foundation for commercial product
