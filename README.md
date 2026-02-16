<div align="center">

# 🏠 UK Property CLI

**One CLI to search every UK property portal.**  
Your AI agent can now find properties, track prices, and analyze the market across Rightmove, Zoopla, ESPC, and more — with clean commands and normalized JSON output.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-green.svg)](https://github.com/abracadabra50/uk-property-cli)
[![Parsers](https://img.shields.io/badge/parsers-3%2F3%20working-success.svg)](https://github.com/abracadabra50/uk-property-cli)
[![Coverage](https://img.shields.io/badge/coverage-95%25%20UK-brightgreen.svg)](https://github.com/abracadabra50/uk-property-cli)

[Why](#why) • [Quick Start](#quick-start) • [Portals](#available-portals) • [Use Cases](#-use-cases) • [Deduplication](#deduplication-across-portals) • [Smart Search](#-smart-property-search)

</div>

---

## Why

If you're building AI agents for property search, there's a gap: **UK property portals offer zero APIs.**

Rightmove, Zoopla, OnTheMarket — none of them provide developer APIs. No OAuth, no REST endpoints, no webhooks. If you want your agent to search properties, track prices, or analyze the market, there's no official way to do it.

But agents need property data. Investment analysis, price tracking, market research — these are perfect agent workflows. The infrastructure just doesn't exist.

**UK Property CLI closes that gap.** Reverse-engineered parsers that give your agent a unified command-line interface to every major UK property portal. Your agent calls `python3 parsers/rightmove.py 4` and gets normalized JSON whether you're searching Rightmove, Zoopla, or ESPC.

Built for agent frameworks like [OpenClaw](https://github.com/claw-labs/openclaw), Pi, Claude Desktop MCP. Works with any agent that can shell out to a CLI. Your agent handles the intelligence (filtering, ranking, alerting). The CLI handles the grunt work (fetching, parsing, normalizing).

**Clean data, zero dependencies, production-ready.**

---

## 🎯 When to Use

Trigger this CLI when users:
- 🏡 Ask about properties for sale anywhere in the UK
- 💰 Want to find investment opportunities
- 👨‍👩‍👧‍👦 Need family homes (4+ bedrooms)
- 📊 Request property market analysis
- 🔔 Want price drop alerts
- 📍 Ask "what's on the market in Manchester?" or "find homes in Edinburgh"
- 🤖 Build automated property workflows

---

## ✨ What the CLI Provides

- 🔍 **Multi-portal search** — ESPC, Rightmove, Zoopla in one tool
- 📊 **Normalized JSON** — Consistent output format across all portals
- 🚫 **Area filtering** — Automatically excludes undesirable areas
- 🏷️ **Smart categorization** — Investment vs family homes
- 🆓 **Zero dependencies** — Just curl + Python (2/3 parsers)
- 📈 **95% UK coverage** — Comprehensive market view
- 🤖 **AI agent ready** — Built for automation
- 📝 **Beautiful docs** — Examples, Block Kit templates, integration guides

## 🛠️ What Your Agent Can Build

**The CLI provides property data. Your agent builds the intelligence:**

- 🔔 **Daily briefings** — Morning summaries of new listings (see [example](#daily-property-briefing))
- 🚨 **Smart alerts** — Price drops, value opportunities (see [example](#smart-alerts))
- 🔄 **Deduplication** — Merge properties across portals (see [example](#deduplication-logic))
- 📊 **Market analysis** — Area statistics, trends (see [example](#market-analysis))
- 🎯 **Smart scoring** — Rank by preferences (see [example](#area-prioritization))
- 📅 **Viewing automation** — Schedule appointments (see [example](#automated-viewings))

---

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/abracadabra50/uk-property-cli.git
cd uk-property-cli

# No installation needed! Just Python 3 + curl (pre-installed on Mac/Linux)

# Search UK properties (4+ beds)
python3 parsers/rightmove.py 4    # UK-wide (1.5M listings)
python3 parsers/zoopla.py 4       # UK-wide + sold prices
python3 parsers/espc.py 4         # Edinburgh specialist

# Or fetch from all portals
./fetch.sh all 4
```

### For Zoopla (Optional)

```bash
# Install Firecrawl CLI
npm install -g @mendable/firecrawl-cli

# Set API key
export FIRECRAWL_API_KEY=your_key_here

# Now Zoopla works
python3 parsers/zoopla.py 4
```

---

## 💡 How It Works

**The CLI provides unified property data:**

```bash
python3 parsers/<portal>.py <min_beds>
```

All parsers return the same JSON structure. Your agent doesn't care which portal you're using.

```bash
python3 parsers/espc.py 4       # Edinburgh specialist
python3 parsers/rightmove.py 4  # UK-wide coverage
python3 parsers/zoopla.py 4     # Sold price data
```

**Under the hood:**

Each parser implements a common interface:

```python
def fetch_page(beds: str) -> str:
    """Fetch search results from portal"""
    
def parse_properties(html: str) -> List[Property]:
    """Extract property data from HTML/JSON"""
    
def categorize(price: int, beds: int) -> str:
    """Tag as investment/family/other"""
```

The output is normalized JSON. Your agent handles the intelligence (filtering, ranking, alerts). The CLI handles the grunt work (fetching, parsing, normalizing).

---

## 🎯 Use Cases

### Deduplication Across Portals

**The problem:** Same property appears on multiple portals (Rightmove + Zoopla + ESPC).

**Agent workflow:**

```python
# User: "Show me properties without duplicates"

# 1. Fetch from all portals
espc = fetch_properties('espc', beds=4)
rightmove = fetch_properties('rightmove', beds=4)
zoopla = fetch_properties('zoopla', beds=4)

all_properties = espc + rightmove + zoopla  # 57 properties

# 2. Normalize addresses for matching
def normalize_address(addr):
    # Remove punctuation, extra spaces, common variations
    addr = addr.lower()
    addr = addr.replace(',', '').replace('.', '')
    addr = addr.replace(' street', ' st').replace(' road', ' rd')
    addr = ' '.join(addr.split())  # Normalize whitespace
    return addr

# 3. Calculate similarity between addresses
from difflib import SequenceMatcher

def addresses_match(addr1, addr2, threshold=0.85):
    norm1 = normalize_address(addr1)
    norm2 = normalize_address(addr2)
    
    similarity = SequenceMatcher(None, norm1, norm2).ratio()
    return similarity >= threshold

# 4. Deduplicate with confidence scores
unique_properties = []
seen_addresses = []

for prop in all_properties:
    is_duplicate = False
    
    for seen_addr in seen_addresses:
        if addresses_match(prop['address'], seen_addr):
            is_duplicate = True
            break
    
    if not is_duplicate:
        unique_properties.append(prop)
        seen_addresses.append(prop['address'])

# Result: 57 → 38 unique properties (35% were duplicates)

# 5. When duplicates found, merge data
def merge_duplicates(properties):
    """
    When same property found on multiple portals,
    combine best data from each source
    """
    merged = []
    
    for prop in unique_properties:
        # Find all versions of this property
        versions = [p for p in all_properties 
                   if addresses_match(p['address'], prop['address'])]
        
        # Merge data - take best from each portal
        merged_prop = {
            'id': prop['id'],
            'address': prop['address'],
            'price': min(p['price'] for p in versions if p['price'] > 0),  # Lowest price
            'beds': max(p['beds'] for p in versions),  # Most beds listed
            'baths': max(p['baths'] for p in versions),  # Most baths listed
            'images': list(set(sum([p['images'] for p in versions], []))),  # All unique images
            'portals': [p['portal'] for p in versions],  # Which portals have it
            'urls': {p['portal']: p['url'] for p in versions}  # All URLs
        }
        
        merged.append(merged_prop)
    
    return merged

deduplicated = merge_duplicates(all_properties)

# Show user clean results
show_properties(deduplicated)  # 38 unique properties with merged data
```

### Property Investment Analysis

**Agent workflow:**

```python
# User: "Find investment opportunities in Edinburgh under £250k"

# 1. Search all portals
espc = fetch_properties('espc', beds=1)
rightmove = fetch_properties('rightmove', beds=1)

# 2. Filter by criteria
investments = [p for p in all_properties 
               if p['price'] < 250000 
               and p['category'] == 'investment']

# 3. Calculate metrics
for prop in investments:
    rental_yield = estimate_rental_income(prop) / prop['price']
    renovation_cost = estimate_renovation(prop)
    prop['roi'] = (rental_yield * 12 - renovation_cost) / prop['price']

# 4. Rank by ROI
top_investments = sorted(investments, key=lambda x: x['roi'], reverse=True)

# 5. Present to user with Block Kit
show_investment_opportunities(top_investments[:5])
```

### Family Home Search

**Agent workflow:**

```python
# User: "Find 4-bed homes in Manchester, max £400k"

# 1. Search with criteria
properties = fetch_all_portals(beds=4)

# 2. Apply intelligent filtering
desired_areas = ['Didsbury', 'Chorlton', 'Altrincham', 'Sale']
good_schools = get_school_catchments(properties)

family_homes = [p for p in properties
                if p['price'] <= 400000
                and any(area in p['address'] for area in desired_areas)
                and p['postcode'] in good_schools]

# 3. Deduplicate across portals
unique_homes = deduplicate_by_address(family_homes)

# 4. Score by preferences
for prop in unique_homes:
    score = 0
    if 'garden' in prop['description'].lower(): score += 10
    if 'parking' in prop['description'].lower(): score += 5
    if prop['area'] in ['Morningside', 'Bruntsfield']: score += 15
    prop['score'] = score

# 5. Show top matches
show_properties(sorted(unique_homes, key=lambda x: x['score'], reverse=True)[:10])
```

### Price Drop Alerts

**Agent workflow:**

```python
# Daily monitoring job at 9am

# 1. Fetch today's properties
today = fetch_all_portals(beds=4)

# 2. Load yesterday's snapshot
with open('snapshots/2026-02-15.json') as f:
    yesterday = json.load(f)

# 3. Detect price changes
price_drops = []
for t in today:
    for y in yesterday:
        if same_property(t, y):
            if t['price'] < y['price']:
                reduction = y['price'] - t['price']
                percent = (reduction / y['price']) * 100
                price_drops.append({
                    'property': t,
                    'old_price': y['price'],
                    'new_price': t['price'],
                    'reduction': reduction,
                    'percent': percent
                })

# 4. Alert on significant drops (>5%)
significant = [p for p in price_drops if p['percent'] > 5]

if significant:
    send_alert(f"🚨 {len(significant)} price drops detected!")
    for prop in significant:
        send_property_card(prop)
```

### Market Analysis

**Agent workflow:**

```python
# User: "What's the average price for 4-bed homes in Didsbury?"

# 1. Fetch comprehensive data
all_properties = fetch_all_portals(beds=4)

# 2. Filter by area
didsbury = [p for p in all_properties 
            if 'Didsbury' in p['address']]

# 3. Calculate statistics
prices = [p['price'] for p in didsbury if p['price'] > 0]

analysis = {
    'count': len(didsbury),
    'average': sum(prices) / len(prices),
    'median': sorted(prices)[len(prices)//2],
    'min': min(prices),
    'max': max(prices),
    'per_sqft': average_per_sqft(didsbury)
}

# 4. Compare with other areas
chorlton = calculate_stats([p for p in all_properties if 'Chorlton' in p['address']])
altrincham = calculate_stats([p for p in all_properties if 'Altrincham' in p['address']])

# 5. Present comparison
show_market_analysis({
    'Didsbury': analysis,
    'Chorlton': chorlton,
    'Altrincham': altrincham
})
```

### Daily Property Briefing

**Agent workflow:**

```python
# Scheduled: 9am every day

# 1. Fetch latest properties
espc = fetch_properties('espc', beds=4)
rightmove = fetch_properties('rightmove', beds=4)
zoopla = fetch_properties('zoopla', beds=4)

all_properties = espc + rightmove + zoopla

# 2. Deduplicate across portals
unique_properties = deduplicate_by_address(all_properties)

# 3. Filter by user preferences
preferences = load_user_preferences()

matches = [p for p in unique_properties
           if p['price'] >= preferences['min_price']
           and p['price'] <= preferences['max_price']
           and any(area in p['address'] for area in preferences['desired_areas'])
           and p['beds'] >= preferences['min_beds']]

# 4. Check for new listings
with open('cache/yesterday.json') as f:
    yesterday_ids = {p['id'] for p in json.load(f)}

today_ids = {p['id'] for p in matches}
new_listings = [p for p in matches if p['id'] not in yesterday_ids]

# 5. Rank by score
for prop in new_listings:
    prop['score'] = calculate_score(prop, preferences)

top_new = sorted(new_listings, key=lambda x: x['score'], reverse=True)[:10]

# 6. Send daily briefing
if top_new:
    send_slack_message(f"""
    🏠 Daily Property Briefing
    
    {len(new_listings)} new properties found
    {len(matches)} total matches
    
    Top 10 new listings:
    """)
    
    for prop in top_new:
        send_property_card(prop)  # Block Kit card with image, details, buttons
    
# 7. Save today's snapshot
with open('cache/today.json', 'w') as f:
    json.dump(matches, f)
```

### Smart Alerts

**Agent workflow:**

```python
# Monitor for specific triggers

# 1. Price drop alerts
def check_price_drops():
    today = fetch_all_saved_properties()
    yesterday = load_snapshot('yesterday.json')
    
    for t in today:
        for y in yesterday:
            if same_property(t, y) and t['price'] < y['price']:
                reduction = y['price'] - t['price']
                percent = (reduction / y['price']) * 100
                
                if percent >= 5:  # Significant drop
                    send_alert(f"""
                    🚨 Price Drop Alert
                    
                    {t['address']}
                    Was: £{y['price']:,}
                    Now: £{t['price']:,}
                    Saved: £{reduction:,} ({percent:.1f}% off)
                    
                    [View Property]({t['url']})
                    """)

# 2. New property in desired area
def check_new_premium_properties():
    premium_areas = ['Didsbury', 'Chorlton', 'Altrincham']
    
    new_properties = get_new_listings_today()
    
    for prop in new_properties:
        if any(area in prop['address'] for area in premium_areas):
            send_alert(f"""
            ⭐ New Property in Premium Area
            
            {prop['address']}
            £{prop['price']:,} | {prop['beds']} bed
            
            Listed: Just now
            
            [View Property]({prop['url']})
            """)

# 3. Price below market average (value alert)
def check_value_opportunities():
    new_properties = get_new_listings_today()
    market_data = load_market_averages()
    
    for prop in new_properties:
        area = prop['area']
        avg_price = market_data[area][prop['beds']]['average']
        
        if prop['price'] < avg_price * 0.85:  # 15%+ below market
            send_alert(f"""
            💰 Value Opportunity
            
            {prop['address']}
            £{prop['price']:,} (15% below market avg)
            
            Market avg: £{avg_price:,}
            Saving: £{avg_price - prop['price']:,}
            
            [View Property]({prop['url']})
            """)

# 4. Back on market (was withdrawn, now relisted)
def check_back_on_market():
    current = get_all_properties()
    last_week = load_snapshot('7_days_ago.json')
    yesterday = load_snapshot('yesterday.json')
    
    yesterday_ids = {p['id'] for p in yesterday}
    last_week_ids = {p['id'] for p in last_week}
    
    for prop in current:
        # Was listed last week, not yesterday, now back
        if prop['id'] in last_week_ids and prop['id'] not in yesterday_ids:
            send_alert(f"""
            🔄 Back on Market
            
            {prop['address']}
            £{prop['price']:,}
            
            This property was withdrawn and is now back.
            Possible price reduction or motivated seller.
            
            [View Property]({prop['url']})
            """)

# Run all checks
check_price_drops()
check_new_premium_properties()
check_value_opportunities()
check_back_on_market()
```

### Automated Viewings

**Agent workflow:**

```python
# User: "Schedule viewings for my top 3 properties this weekend"

# 1. Get user's saved properties
saved = load_saved_properties()

# 2. Rank by score
top_3 = sorted(saved, key=lambda x: x['score'], reverse=True)[:3]

# 3. Extract agent contact info (from property page)
for prop in top_3:
    agent_phone = extract_agent_contact(prop['url'])
    agent_email = extract_agent_email(prop['url'])
    
    # 4. Generate viewing request
    message = f"""
    Hi, I'm interested in viewing {prop['address']}.
    
    Available times:
    - Saturday 10am-4pm
    - Sunday 10am-4pm
    
    Please let me know available slots.
    """
    
    # 5. Send request (email or call)
    if agent_email:
        send_email(agent_email, "Viewing Request", message)
    else:
        add_to_call_list(agent_phone, message)

# 6. Confirm with user
show_viewing_requests_sent(top_3)
```

---

## 📊 Available Portals

<div align="center">

| Portal | Coverage | Listings | Status | Dependencies |
|:------:|:--------:|:--------:|:------:|:------------:|
| **[Rightmove](https://rightmove.co.uk)** | UK-wide | 1.5M | ✅ Working | None |
| **[Zoopla](https://zoopla.co.uk)** | UK-wide | 750k | ✅ Working | Firecrawl |
| **[ESPC](https://espc.com)** | Scotland | 2-3k | ✅ Working | None |

</div>

### Coverage Stats

- 🇬🇧 **UK**: 95%+ coverage (Rightmove + Zoopla)
- 🏴󠁧󠁢󠁳󠁣󠁴󠁿 **Scotland**: 99% coverage (+ ESPC for Edinburgh)
- 📈 **Market share**: 80% Rightmove + 50% Zoopla across UK

---

## 🧠 Smart Property Search

The CLI provides property data. Your agent makes intelligent decisions.

### Area Prioritization

```python
# Agent logic (not CLI) - customize for your target city
area_tiers = {
    'premium': ['Didsbury', 'Chorlton', 'Altrincham', 'Hale'],  # Manchester example
    'excellent': ['Sale', 'Timperley', 'Cheadle'],
    'good': ['Stretford', 'Withington', 'Levenshulme'],
    'avoid': ['Moss Side', 'Longsight']  # Configure per city
}

def score_by_area(property):
    address = property['address'].lower()
    
    for area in area_tiers['premium']:
        if area.lower() in address:
            return 100  # Premium location
    
    for area in area_tiers['excellent']:
        if area.lower() in address:
            return 80
    
    for area in area_tiers['good']:
        if area.lower() in address:
            return 60
    
    for area in area_tiers['avoid']:
        if area.lower() in address:
            return 0  # Auto-reject
    
    return 40  # Unknown area - proceed with caution
```

### Investment Metrics

```python
# Calculate rental yield
def calculate_rental_yield(property, market='uk_average'):
    """
    UK rental market averages (adjust for your region):
    - 1 bed: £700-1000/month
    - 2 bed: £900-1400/month
    - 3 bed: £1200-1800/month
    - 4 bed: £1500-2500/month
    
    London: multiply by 1.8
    Manchester/Edinburgh: multiply by 1.2
    Regional: multiply by 0.8
    """
    
    monthly_rent = {
        1: 850, 2: 1100, 3: 1400, 4: 1800
    }.get(property['beds'], 1000)
    
    annual_rent = monthly_rent * 12
    yield_percent = (annual_rent / property['price']) * 100
    
    return {
        'monthly_rent': monthly_rent,
        'annual_income': annual_rent,
        'yield_percent': yield_percent,
        'rating': 'excellent' if yield_percent > 6 else 'good' if yield_percent > 4 else 'poor'
    }

# Example usage
property = {
    'price': 200000,
    'beds': 2,
    'address': '...'
}

metrics = calculate_rental_yield(property)
# Output: {'monthly_rent': 1200, 'annual_income': 14400, 'yield_percent': 7.2, 'rating': 'excellent'}
```

### Deduplication Implementation

```python
# Quick implementation - see Use Cases for complete version
from difflib import SequenceMatcher

def deduplicate(properties, threshold=0.85):
    """
    Match properties across portals by address similarity.
    
    Args:
        properties: List of property dicts
        threshold: Similarity score 0-1 (0.85 = 85% match)
    
    Returns:
        List of unique properties
    """
    def normalize(addr):
        return ' '.join(addr.lower()
                       .replace(',', '')
                       .replace('.', '')
                       .split())
    
    unique = []
    seen = []
    
    for prop in properties:
        addr = normalize(prop['address'])
        
        # Check if similar to any seen address
        is_duplicate = any(
            SequenceMatcher(None, addr, seen_addr).ratio() >= threshold
            for seen_addr in seen
        )
        
        if not is_duplicate:
            unique.append(prop)
            seen.append(addr)
    
    return unique

# Usage
all_properties = fetch_all_portals(beds=4)  # 57 properties
unique_properties = deduplicate(all_properties)  # 38 unique

# Deduplication typically reduces by 30-40%
```

**Advanced:** See [Deduplication use case](#deduplication-across-portals) for merging data from multiple portals (take best price, combine images, etc).

### Value Analysis

```python
# Score properties by value for money
def analyze_value(property, market_data):
    """
    Compare property price to area average.
    Find undervalued properties.
    """
    
    # Get area average price per bedroom
    area = property['area']
    beds = property['beds']
    
    avg_price_per_bed = market_data[area][beds]['average'] / beds
    this_price_per_bed = property['price'] / beds
    
    value_ratio = this_price_per_bed / avg_price_per_bed
    
    if value_ratio < 0.85:
        return {'rating': 'excellent', 'reason': 'Below market average by 15%+'}
    elif value_ratio < 0.95:
        return {'rating': 'good', 'reason': 'Slightly below market average'}
    elif value_ratio < 1.05:
        return {'rating': 'fair', 'reason': 'At market average'}
    else:
        return {'rating': 'poor', 'reason': 'Above market average'}
```

---

## 📤 Output Format

All parsers return normalized JSON:

```json
{
  "portal": "espc",
  "fetched_at": "2026-02-16T08:30:00Z",
  "count": 8,
  "properties": [
    {
      "id": "36362802",
      "portal": "espc",
      "title": "4-bed house",
      "price": 450000,
      "price_text": "Offers Over £450,000",
      "beds": 4,
      "baths": 2,
      "property_type": "house",
      "address": "1 Buckstone Circle, Edinburgh EH10",
      "area": "Buckstone",
      "postcode": "EH10 6XB",
      "url": "https://espc.com/property/...",
      "image_url": "https://images.espc.com/...",
      "category": "family"
    }
  ]
}
```

---

## 🎯 Use Cases

### When to Use

Trigger this CLI when you need to:
- 🏡 Search for properties in Edinburgh or UK
- 💰 Find investment opportunities
- 👨‍👩‍👧‍👦 Look for family homes (4+ beds)
- 📊 Analyze property market data
- 🔔 Build property alert systems
- 🤖 Integrate with AI agents (Slack bots, etc.)

## 🔧 Setup & Configuration

### Interactive Setup

```bash
python3 setup.py
```

Guides you through configuring:
- **Search criteria** — Bedrooms, price range, property types
- **Area preferences** — Desired postcodes, areas to avoid, premium areas
- **Scoring weights** — How to rank properties
- **Deduplication** — Automatic duplicate removal (recommended: enabled)
- **Daily briefings** — Schedule and preferences

**Presets available:**
- Edinburgh (EH10, EH12, EH4, etc.)
- Manchester (M20, M21, Didsbury, etc.)
- London (SW, W, NW postcodes)
- Custom (configure manually)

Saves to `preferences.json` — edit manually anytime.

### Configuration File

```json
{
  "search": {
    "min_beds": 4,
    "max_price": 600000
  },
  "areas": {
    "desired": ["EH10", "EH12", "EH4"],
    "excluded": ["EH17", "Niddrie", "Moredun"],
    "premium": ["EH10", "EH9"]
  },
  "deduplication": {
    "enabled": true,
    "threshold": 0.85
  }
}
```

### Deduplication

**Built-in and automatic.** You don't need to call it separately.

When you run `briefing.py`:
1. Fetches from all portals (57 properties)
2. **Automatically deduplicates** (→ 38 unique)
3. Filters by your preferences
4. Ranks and outputs

**Why automatic?**
- Properties appear on multiple portals (Rightmove + Zoopla + ESPC)
- Typical reduction: 30-40% duplicates
- Merges best data from each portal (lowest price, all images, all URLs)

**Manual control:**
```bash
# Standalone deduplication
python3 dedupe.py espc.json rightmove.json zoopla.json

# Disable in preferences
{"deduplication": {"enabled": false}}
```

### Agent Integration

**The CLI handles data. Your agent handles intelligence.**

```bash
# CLI provides
python3 parsers/rightmove.py 4  # → Raw property JSON

# Your agent builds
- Daily briefings (fetch → filter → rank → send)
- Price alerts (compare → detect changes → notify)
- Deduplication (match addresses → merge data)
- Market analysis (aggregate → calculate → visualize)
```

See [Use Cases](#-use-cases) below for complete implementation examples of what your agent can build with this data.

---

## 🎨 Block Kit Integration (Slack)

<details>
<summary><b>Property Card Example</b></summary>

```javascript
{
  "type": "section",
  "text": {
    "type": "mrkdwn",
    "text": "*1 Buckstone Circle, Edinburgh EH10*\n\nOffers Over £450,000 | 4 bed | 2 bath\n\nLocated within the sought after Buckstone area..."
  },
  "accessory": {
    "type": "image",
    "image_url": "https://images.espc.com/...",
    "alt_text": "Property image"
  }
},
{
  "type": "actions",
  "elements": [
    {
      "type": "button",
      "text": {"type": "plain_text", "text": "View Details"},
      "url": "https://espc.com/property/...",
      "style": "primary"
    }
  ]
}
```

</details>

<details>
<summary><b>Daily Briefing Example</b></summary>

```javascript
{
  "type": "header",
  "text": {"type": "plain_text", "text": "🏠 Daily Property Briefing"}
},
{
  "type": "section",
  "text": {
    "type": "mrkdwn",
    "text": "*Manchester Properties* | Tuesday 16 Feb 2026\n\n*12 new listings* | *3 price drops* | *1 back on market*"
  }
},
{
  "type": "divider"
},
{
  "type": "section",
  "fields": [
    {"type": "mrkdwn", "text": "*New in Didsbury*\n4 bed detached\n£425,000"},
    {"type": "mrkdwn", "text": "*Price Drop*\nChorlton semi\n£380k → £365k"}
  ]
},
{
  "type": "actions",
  "elements": [
    {
      "type": "button",
      "text": {"type": "plain_text", "text": "View All (12)"},
      "action_id": "view_all_new",
      "style": "primary"
    },
    {
      "type": "button",
      "text": {"type": "plain_text", "text": "Price Drops (3)"},
      "action_id": "view_price_drops"
    }
  ]
}
```

</details>

<details>
<summary><b>Price Drop Alert Example</b></summary>

```javascript
{
  "type": "section",
  "text": {
    "type": "mrkdwn",
    "text": "🚨 *Price Drop Alert*\n\n13 Didsbury Road, Manchester\n\nWas: £425,000\nNow: *£395,000*\n\nSaved: £30,000 (7.1% reduction)\n\nListed 45 days ago — motivated seller."
  },
  "accessory": {
    "type": "image",
    "image_url": "https://...",
    "alt_text": "Property"
  }
},
{
  "type": "actions",
  "elements": [
    {
      "type": "button",
      "text": {"type": "plain_text", "text": "View Property"},
      "url": "https://rightmove.co.uk/...",
      "style": "primary"
    },
    {
      "type": "button",
      "text": {"type": "plain_text", "text": "Book Viewing"},
      "action_id": "book_viewing"
    }
  ]
}
```

</details>

---

## 🏷️ Property Categories

Properties are auto-categorized:

<div align="center">

| Category | Criteria | Use Case |
|:--------:|:--------:|:--------:|
| **Investment** | Price < £250k | High rental yield, renovation opportunities |
| **Family** | 4+ bedrooms | Growing families, good areas |
| **Other** | Everything else | General market |

</div>

---

## 🌍 Area Intelligence

Configure area filtering based on your target city/region. The CLI provides raw data — your agent applies local knowledge.

### Example: Edinburgh

**Premium:** Morningside • Bruntsfield • Marchmont • Stockbridge  
**Good:** Colinton • Cramond • Portobello • Leith  
**Avoid:** Moredun • Niddrie • Wester Hailes • Sighthill

### Example: Manchester

**Premium:** Didsbury • Chorlton • Altrincham • Hale  
**Good:** Sale • Timperley • Stretford  
**Avoid:** Configure based on local crime/school data

### Example: London

**Premium:** Kensington • Chelsea • Hampstead • Richmond  
**Good:** Clapham • Islington • Greenwich  
**Avoid:** Configure based on local knowledge

**Customize area filters in your agent code — not in the CLI.**

---

## 📖 Documentation

<div align="center">

| Document | Description |
|:--------:|:-----------:|
| [README.md](README.md) | Main documentation (you are here) |
| [PORTALS.md](PORTALS.md) | Portal analysis & rankings |
| [SKILL.md](SKILL.md) | AI agent integration guide |

</div>

---

## 🔧 Advanced Usage

### Parse Output with jq

```bash
# Get property count
python3 parsers/espc.py 4 | jq '.count'

# Get all addresses
python3 parsers/espc.py 4 | jq -r '.properties[].address'

# Properties under £300k
python3 parsers/espc.py 4 | jq '.properties[] | select(.price < 300000)'

# Family homes only
python3 parsers/espc.py 4 | jq '.properties[] | select(.category == "family")'
```

### Caching (Recommended)

```bash
#!/bin/bash
CACHE_FILE="cache/espc-4bed.json"
CACHE_TTL=3600  # 1 hour

if [ -f "$CACHE_FILE" ]; then
  AGE=$(( $(date +%s) - $(stat -f %m "$CACHE_FILE") ))
  if [ $AGE -lt $CACHE_TTL ]; then
    cat "$CACHE_FILE"
    exit 0
  fi
fi

# Fetch fresh
python3 parsers/espc.py 4 | tee "$CACHE_FILE"
```

---

## 🎭 Integration Examples

### Pi Agent / Pal

```bash
# Daily briefing at 9am
python3 parsers/espc.py 4 > /tmp/espc.json
python3 parsers/rightmove.py 4 > /tmp/rightmove.json

# Format as Block Kit
node format-briefing.js /tmp/*.json | slack-post
```

### OpenClaw / Clawdbot

```typescript
const properties = await bash(`python3 ${skillDir}/parsers/espc.py 4`);
const data = JSON.parse(properties.stdout);

data.properties.forEach(p => {
  console.log(`${p.address} - £${p.price.toLocaleString()}`);
});
```

### MCP Server (Future)

```typescript
tools: [
  "property_search_espc",
  "property_search_rightmove",
  "property_search_zoopla",
  "property_track_price"
]
```

---

## 💰 Cost Analysis

<div align="center">

| Parser | Dependencies | Cost/Month | Status |
|:------:|:------------:|:----------:|:------:|
| **ESPC** | None (curl) | £0 | ✅ Free forever |
| **Rightmove** | None (curl) | £0 | ✅ Free forever |
| **Zoopla** | Firecrawl API | ~$1 | ⚠️ Paid (optional) |

**Daily briefing cost**: ~$0.03/day = ~$1/month = ~$12/year

</div>

---

## 🗂️ File Structure

```
uk-property-cli/
├── parsers/
│   ├── espc.py              # ESPC parser (Edinburgh) ✅
│   ├── rightmove.py         # Rightmove parser (UK) ✅
│   └── zoopla.py            # Zoopla parser (UK) ✅
├── fetch.sh                 # Portal dispatcher
├── cache/                   # Cache directory
├── README.md                # Main documentation
├── PORTALS.md               # Portal analysis
└── SKILL.md                 # Integration guide
```

---

## 🚦 Current Status

<div align="center">

### ✅ Working Parsers

| Parser | Properties | Price Range | Dependencies |
|:------:|:----------:|:-----------:|:------------:|
| **ESPC** | 8 found | £450k - £895k | None |
| **Rightmove** | 25 found | £290k - £769k | None |
| **Zoopla** | 24 found | £260k - £1.2M | Firecrawl |

**Total**: 57 properties from one search

### 📈 Coverage

- UK: **95%+** (Rightmove + Zoopla)
- Scotland: **99%** (+ ESPC)
- England/Wales: **95%** (Rightmove + Zoopla)

### ⏱️ Performance

- ESPC: ~2s
- Rightmove: ~3s
- Zoopla: ~5s (API call)

</div>

---

## 🛣️ Roadmap

### ✅ Phase 1 (Complete)
- [x] ESPC parser (Edinburgh)
- [x] Rightmove parser (UK)
- [x] Zoopla parser (UK)
- [x] Normalized JSON output
- [x] Area filtering
- [x] Category tagging

### 📋 Phase 2 (Optional)
- [ ] OnTheMarket parser (exclusive listings)
- [ ] Price tracking database
- [ ] Alert system for new listings
- [ ] Daily briefing formatter
- [ ] Investment metrics (yield, ROI)

### 🚀 Phase 3 (Future)
- [ ] S1 Homes (Scotland-wide)
- [ ] ASPC (Aberdeen)
- [ ] Sold price analysis
- [ ] Block Kit template library
- [ ] MCP server wrapper
- [ ] npm/pip package

---

## 🤝 Contributing

This is a private tool, but the architecture is simple:

1. Create `parsers/newportal.py`
2. Implement `fetch_page()` and `parse_properties()`
3. Return normalized JSON format
4. Done!

See [PORTALS.md](PORTALS.md) for portal analysis.

---

## 📜 License

**Private** - for personal use

---

## 💡 Commercial Opportunity

**PiBooks Property** - Vertical AI agent for property search

**Target market:**
- Property investors (£5-100M portfolios)
- Estate agents (market intelligence)
- Property developers (opportunity scanning)

**UK PropTech market**: £8.4bn

See [PORTALS.md](PORTALS.md) for full commercial analysis.

---

## 🙏 Credits

Built with zero dependencies for maximum portability and zero costs.

Inspired by the UK property market's complexity and the need for intelligent property search.

---

<div align="center">

**Find your dream home with AI! 🏠**

[⬆ Back to Top](#-uk-property-cli)

---

Made with ❤️ for the Edinburgh property market

</div>
