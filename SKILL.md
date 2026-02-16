---
name: edinburgh-property
description: UK-wide property search across Rightmove, Zoopla, ESPC. Provides tools for fetching, deduplicating, filtering, and comparing properties. Agent builds briefings using these tools.
---

# UK Property CLI Skill

## When to Use

Trigger this skill when the user:
- Asks about properties for sale anywhere in UK
- Wants investment opportunities or family homes
- Requests property market data
- Asks for daily property briefings
- Wants price drop alerts

## How It Works

**The CLI provides raw tools. Your agent builds the intelligence.**

```
CLI Tools:           Agent Builds:
├── fetch            → Daily briefings
├── dedupe           → Price alerts
├── filter           → Market analysis
└── compare          → Smart recommendations
```

## Tools Available

### 1. Fetch Properties

```bash
# Fetch from all portals (automatic parallel fetch)
{baseDir}/fetch.sh all 4

# Individual portals
python3 {baseDir}/parsers/espc.py 4        # Edinburgh
python3 {baseDir}/parsers/rightmove.py 4   # UK-wide
python3 {baseDir}/parsers/zoopla.py 4      # UK-wide + sold prices
```

**Output:** JSON with normalized property data

### 2. Deduplicate

```bash
# Merge properties across portals
python3 {baseDir}/dedupe.py cache/espc.json cache/rightmove.json cache/zoopla.json
```

**What it does:**
- Matches properties by address similarity (85% threshold)
- Merges data from multiple portals
- Takes best price, combines images
- Typical: 57 properties → 38 unique (33% duplicates)

**Output:** JSON with unique properties + deduplication stats

### 3. Filter

```bash
# Filter by preferences
python3 {baseDir}/filter.py properties.json \
  --areas "EH10,EH12,EH4" \
  --exclude "Niddrie,Moredun" \
  --max-price 600000 \
  --min-beds 4

# Use built-in Edinburgh presets
python3 {baseDir}/filter.py properties.json --use-defaults --max-price 600000
```

**Output:** JSON with filtered properties

### 4. Compare Snapshots

```bash
# Detect changes between snapshots
python3 {baseDir}/compare.py cache/2026-02-15.json cache/2026-02-16.json
```

**Output:** JSON with:
- `new_listings`: Properties not in yesterday
- `removed_listings`: Properties removed from market
- `price_changes`: Price reductions/increases

### 5. User Preferences

```bash
# Interactive setup (one-time)
python3 {baseDir}/setup.py

# Loads from preferences.json
cat {baseDir}/preferences.json
```

**Contains:**
- Search criteria (beds, price, types)
- Area preferences (desired, excluded, premium)
- Scoring weights
- Deduplication settings

---

## Agent Workflow Examples

### Daily Property Briefing

```bash
# 1. Fetch from all portals
{baseDir}/fetch.sh all 4 > /tmp/all-properties.json

# 2. Deduplicate
python3 {baseDir}/dedupe.py /tmp/all-properties.json > /tmp/deduped.json

# 3. Filter by preferences
python3 {baseDir}/filter.py /tmp/deduped.json \
  --use-defaults \
  --max-price 600000 > /tmp/filtered.json

# 4. Compare with yesterday
python3 {baseDir}/compare.py \
  {baseDir}/cache/2026-02-15.json \
  /tmp/filtered.json > /tmp/comparison.json

# 5. Parse results and build Block Kit briefing
python3 << 'EOF'
import json

with open('/tmp/comparison.json') as f:
    comp = json.load(f)

print(f"🏠 Daily Briefing")
print(f"New listings: {len(comp['new_listings'])}")
print(f"Price changes: {len(comp['price_changes'])}")

for prop in comp['new_listings'][:5]:
    print(f"- {prop['address']}: £{prop['price']:,}")
EOF

# 6. Send to Slack via Block Kit
# (Agent formats Block Kit message with images, buttons, etc)

# 7. Save today's snapshot for tomorrow
cp /tmp/filtered.json {baseDir}/cache/$(date +%Y-%m-%d).json
```

### Price Drop Alert

```bash
# User: "Alert me if any properties drop below £500k"

# 1. Fetch current properties
{baseDir}/fetch.sh all 4 > /tmp/current.json

# 2. Compare with saved snapshot
python3 {baseDir}/compare.py \
  {baseDir}/cache/saved-properties.json \
  /tmp/current.json > /tmp/changes.json

# 3. Parse price drops
python3 << 'EOF'
import json

with open('/tmp/changes.json') as f:
    changes = json.load(f)

for change in changes['price_changes']:
    if change['change'] < 0 and change['new_price'] < 500000:
        prop = change['property']
        print(f"🚨 Price Drop!")
        print(f"{prop['address']}")
        print(f"Was: £{change['old_price']:,}")
        print(f"Now: £{change['new_price']:,}")
        print(f"Saved: £{abs(change['change']):,}")
EOF
```

### Investment Opportunities

```bash
# User: "Find investment properties under £250k"

# 1. Fetch all properties
{baseDir}/fetch.sh all 1 > /tmp/all.json  # 1+ beds for investments

# 2. Dedupe
python3 {baseDir}/dedupe.py /tmp/all.json > /tmp/deduped.json

# 3. Filter to investment criteria
python3 {baseDir}/filter.py /tmp/deduped.json \
  --max-price 250000 \
  --category investment > /tmp/investments.json

# 4. Calculate rental yield
python3 << 'EOF'
import json

with open('/tmp/investments.json') as f:
    data = json.load(f)

# Edinburgh rental yields
rent_estimates = {1: 900, 2: 1200, 3: 1600}

for prop in data['properties']:
    monthly = rent_estimates.get(prop['beds'], 1000)
    annual = monthly * 12
    yield_pct = (annual / prop['price']) * 100
    
    prop['rental_yield'] = yield_pct
    prop['monthly_rent'] = monthly

# Sort by yield
sorted_props = sorted(data['properties'], 
                     key=lambda x: x.get('rental_yield', 0), 
                     reverse=True)

print(f"Top 5 Investment Opportunities:")
for prop in sorted_props[:5]:
    print(f"\n{prop['address']}")
    print(f"£{prop['price']:,} | {prop['beds']} bed")
    print(f"Yield: {prop['rental_yield']:.1f}%")
EOF
```

### Market Analysis

```bash
# User: "What's the average price in Morningside?"

# 1. Fetch Edinburgh properties
python3 {baseDir}/parsers/espc.py 4 > /tmp/espc.json

# 2. Filter to Morningside
python3 {baseDir}/filter.py /tmp/espc.json \
  --areas "Morningside,EH10" > /tmp/morningside.json

# 3. Calculate statistics
python3 << 'EOF'
import json
import statistics

with open('/tmp/morningside.json') as f:
    data = json.load(f)

prices = [p['price'] for p in data['properties'] if p['price'] > 0]

print(f"📊 Morningside Market Analysis")
print(f"Properties: {len(prices)}")
print(f"Average: £{sum(prices) // len(prices):,}")
print(f"Median: £{statistics.median(prices):,}")
print(f"Range: £{min(prices):,} - £{max(prices):,}")
EOF
```

---

## Loading User Preferences

```python
import json

# Load user's configured preferences
with open('{baseDir}/preferences.json') as f:
    prefs = json.load(f)

# Use in filtering
desired_areas = prefs['areas']['desired']
max_price = prefs['search']['max_price']
min_beds = prefs['search']['min_beds']

# Use in scoring
premium_areas = prefs['areas']['premium']
area_weights = prefs['scoring']['area_weights']
```

---

## File Structure

```
{baseDir}/
├── parsers/
│   ├── espc.py          # Edinburgh specialist
│   ├── rightmove.py     # UK-wide
│   └── zoopla.py        # UK-wide + sold prices
├── dedupe.py            # Deduplication engine
├── filter.py            # Filtering tool
├── compare.py           # Snapshot comparison
├── setup.py             # Interactive preferences setup
├── preferences.json     # User configuration
├── fetch.sh             # Unified dispatcher
└── cache/               # Snapshots for comparison
    ├── 2026-02-15.json
    └── 2026-02-16.json
```

---

## Coverage

- **UK**: 95%+ (Rightmove + Zoopla)
- **Scotland**: 99% (+ ESPC for Edinburgh)
- **Portals**: 3 working (ESPC, Rightmove, Zoopla)
- **Dependencies**: Zero for 2/3 parsers, Firecrawl for Zoopla (~£1/month)

---

## GitHub

Private repository: https://github.com/abracadabra50/uk-property-cli

Full documentation in README.md with examples, Block Kit templates, and agent integration patterns.
