# TrueSync Lead Generation System

Automated lead generation and enrichment system for Flawless AI's TrueSync product, targeting distribution, licensing, acquisitions, and executive roles at major studios, distributors, and platforms across **global markets**.

## Overview

This system discovers, enriches, scores, and exports leads from target companies to help the Flawless AI sales team identify and prioritize outreach for TrueSync.

### Key Features

- **Multi-Market Support** - USA, UK, France, Spain, Germany, South Korea (auto-detected from locations)
- **Batch Processing** - All API calls use batching for 5-10x faster execution
- **Retry Logic** - Exponential backoff for transient API failures
- **API Caching** - 24-hour cache to avoid redundant API calls
- **Input Validation** - Validates lead data before processing
- **Structured Logging** - Full audit trail with log files
- **Google Search LinkedIn Lookup** - Finds LinkedIn URLs via batched Google searches
- **Verified Emails** - Uses Apify's leads-finder for verified business emails
- **Company-Specific Email Patterns** - Uses correct email formats per company
- **Sales Navigator CSV Parser** - Imports messy LinkedIn Sales Navigator exports
- **Market-Specific Exports** - Generates separate CSVs per market
- **Professional Excel Output** - Styled workbooks with color-coded priority scores
- **Database Integration** - Optional persistence to Neon Postgres
- **Automated Scoring** - ICP-based scoring (1-100) for lead prioritization

---

## Latest Results (January 20, 2026)

| Metric | Result |
|--------|--------|
| **LinkedIn URL Rate** | ~90% |
| **Verified Emails** | Via Apify leads-finder |
| **Pattern-Based Emails** | Company-specific formats |
| **Markets Covered** | USA, UK, France, Germany, Spain, South Korea |
| **Target Companies** | 31 companies across 6 markets |
| **Database** | Neon Postgres (PostgreSQL 17.7) |

## New: Two-Pipeline Architecture

| Pipeline | Script | Output |
|----------|--------|--------|
| **Lead Enrichment** | `enrich_pipeline_v3.py` | Contacts: Name, Title, Email, LinkedIn, Score |
| **Accounts Enrichment** | `accounts_pipeline.py` | Companies: Title counts, Contact counts |

---

## Architecture

The system follows a **3-layer DOE architecture** (Directive-Orchestration-Execution):

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        LAYER 1: DIRECTIVE (SOPs)                            │
│                        directives/scrape_leads.md                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                    ↓                                        │
│                        LAYER 2: ORCHESTRATION                               │
│                        (AI Agent Decision Making)                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                    ↓                                        │
│                        LAYER 3: EXECUTION                                   │
│                        execution/enrich_pipeline_v3.py                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        TRUESYNC LEAD PIPELINE v3                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  INPUT: Sales Navigator CSV/JSON                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Validation and cleaning                                           │   │
│  │ • Market detection from location                                    │   │
│  │ • Initial ICP scoring                                               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  PART 1: LinkedIn URL Discovery (Batched Google Search)                    │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • 20 queries per API call (vs 1 at a time)                          │   │
│  │ • Query: "Name" "Company" site:linkedin.com/in                      │   │
│  │ • Retry with exponential backoff on failure                         │   │
│  │ • Results cached for 24 hours                                       │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  PART 2: Email Enrichment (Batched Domain Search)                          │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • All company domains in single API call                            │   │
│  │ • Uses code_crafter/leads-finder actor                              │   │
│  │ • Returns verified emails + LinkedIn URLs                           │   │
│  │ • Fallback: company-specific email pattern generation               │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    ↓                                        │
│  PART 3: Export & Database                                                 │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ • Styled Excel workbook (dark blue headers, color-coded scores)     │   │
│  │ • CSV export for Google Sheets import                               │   │
│  │ • Database push to Neon Postgres                                    │   │
│  │ • Full run log saved to output/                                     │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Performance Comparison

| Leads | Old (Sequential) | New (Batched) | Speedup |
|-------|-----------------|---------------|---------|
| 55    | ~20 minutes     | ~3-5 minutes  | **4-7x** |
| 100   | ~35 minutes     | ~5-8 minutes  | **4-7x** |
| 200   | ~70 minutes     | ~10-15 min    | **5-7x** |

---

## Installation

```bash
# Clone/navigate to project
cd "truesync-leads"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys
```

---

## Configuration

### Environment Variables

| Variable | Status | Purpose |
|----------|--------|---------|
| `APIFY_TOKEN` | ✅ Required | LinkedIn scraping & email finding |
| `DATABASE_URL` | ✅ Required | Neon Postgres connection |
| `HUBSPOT_API_KEY` | ⚠️ Optional | CRM integration |
| `TMDB_ACCESS_TOKEN` | ⚠️ Optional | Catalog data enrichment |

---

## Usage

### Quick Start - From Sales Navigator CSV

```bash
# 1. Parse Sales Navigator export to JSON
python execution/parse_sales_nav_csv.py "/path/to/sales_nav_export.csv"
# Output: .tmp/uk_leads_raw.json

# 2. Run the lead enrichment pipeline
python execution/enrich_pipeline_v3.py --input .tmp/uk_leads_raw.json --market Global --skip-db

# 3. Run the accounts enrichment pipeline
python execution/accounts_pipeline.py --skip-db

# Results:
# - Leads: output/truesync_leads_v3_{timestamp}.xlsx
# - Accounts: output/accounts_{timestamp}.xlsx
```

### Accounts Pipeline

Enriches all 31 target companies with catalog data:

```bash
python execution/accounts_pipeline.py           # Full pipeline
python execution/accounts_pipeline.py --skip-db # Excel only
python execution/accounts_pipeline.py --skip-cache # Force fresh API calls
```

**Output Schema:**
| Accounts | Region | No. of titles | Type of company | No. of contacts |
|----------|--------|---------------|-----------------|-----------------|
| BBC Studios | UK | 2,500 | Producer | 12 |
| Netflix US | USA | 15,000 | Platform | 24 |

### Pipeline Options

```bash
python execution/enrich_pipeline_v3.py \
  --input .tmp/leads.json \    # Input JSON file
  --market Global \            # Market name (auto-detects from locations)
  --skip-enrich \              # Skip LinkedIn/email enrichment
  --skip-db \                  # Skip database push
  --skip-cache \               # Skip API result caching (force fresh calls)
  --clear-cache \              # Clear cache before running
  --filter-companies           # Only include predefined target companies
```

### Input Format

Input JSON should be a list of leads:

```json
[
  {
    "name": "Matt Perry",
    "title": "SVP, Head of Global Content Sales",
    "company": "BBC Studios",
    "location": "London, UK"
  }
]
```

### Output

The pipeline generates:

- **Excel**: `output/truesync_leads_v3_{timestamp}.xlsx`
- **CSV**: `output/truesync_leads_v3_{timestamp}.csv`
- **Log**: `output/pipeline_run_{timestamp}.log`
- **Market CSVs**: `output/by_market/leads_{market}.csv` (when split by market)

Output columns:
- Name, Title, Company, LinkedIn URL, Email, Location, Priority Score, Market

---

## Apify Actors Used

| Actor | Purpose | Batching |
|-------|---------|----------|
| `apify/google-search-scraper` | Find LinkedIn URLs via Google | ✅ 20 queries/call |
| `code_crafter/leads-finder` | Find verified emails + profiles | ✅ All domains/call |

---

## Target ICP Roles

### Primary ICPs (Direct Buyers)
- **Acquisitions**: Head of International Acquisitions, VP Acquisitions, Director of Acquisitions
- **Distribution**: Head of Global Distribution, Head/VP/SVP International Sales, VP Distribution
- **Licensing**: Head of Licensing, VP/SVP International Licensing, Director of Licensing
- **Content Sales**: Head of Content Sales, Director of Content Sales, VP Content Partnerships

### Secondary ICPs (Influencers/Champions)
- **Content Leadership**: Head of Content, SVP/EVP Content, Chief Content Officer
- **Programming**: Head of Programming, SVP Programming (Tubi, Pluto, Roku)
- **Consumer Insights**: Head of Consumer Insights, VP Data Science, Head of Content Analytics
- **Studio Owners**: President of Studio, Studio Head, Head of Label, EVP Franchise Development
- **International Originals**: Head of International Originals, VP Local Originals, Head of Local Content

### Emerging Roles
- **Localization**: Head/VP/SVP/Director of Localization
- **AI & Technology**: Head/VP/SVP/Chief AI Officer, Head of AI Strategy

### Operations & Strategy
- **Universal Pictures Content Group**: CFO, SVP Commercial Strategy, SVP Production/Programming/Operations
- **General**: Head/VP Operations, Head/VP Commercial Strategy

See `directives/buyer_personas.md` for full buyer knowledge base.

---

## Scoring Algorithm

Leads are scored 1-100 based on:

| Factor | Points | Description |
|--------|--------|-------------|
| **Company Tier** | +10 to +25 | Tier 1: Netflix/Amazon/WBD/Sony (+25), Tier 2: Lionsgate/Sky/BBC (+20), Tier 3: Pluto/Tubi/Roku (+15), Other (+10) |
| **Role Relevance** | +25 to +40 | Acquisitions/Distribution/Licensing/Programming (+40), Head of Content (+25) |
| **Seniority** | +10 to +25 | EVP/President (+25), SVP (+20), VP (+15), Director/Head (+12), Sr. Manager (+10) |
| **Scope** | +8 to +15 | Global/Worldwide/International (+15), Group/Executive (+10), Regional/EMEA/APAC (+8) |

**Score Ranges:**
- 🟢 75-100: High priority (hot leads)
- 🟡 50-74: Medium priority (qualified)
- 🔴 <50: Lower priority (nurture)

**Supported Companies (31 total, Auto-detected):**
- Major Studios: Warner Bros. Discovery, Sony Pictures, Lionsgate, Netflix, Amazon/Prime Video, Universal Pictures Content Group
- Streaming/FAST: Pluto TV, Tubi, Roku, Freevee
- European: Studiocanal, Canal+, Gaumont, Beta Film, UFA, Constantin Film
- UK: BBC Studios, Sky, Channel 4, ITV Studios, All3Media
- Korea: Studio Dragon, CJ ENM, SBS Contents Hub
- Spain: Atresmedia Studios, Mediapro

---

## Project Structure

```
truesync-leads/
├── AGENTS.md                   # DOE framework documentation
├── README.md                   # This file
├── config.yaml                 # ICP roles, scoring config
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (gitignored)
│
├── directives/                 # SOPs for agent operations
│   ├── scrape_leads.md         # Lead scraping directive
│   ├── accounts_pipeline.md    # Accounts enrichment directive
│   └── buyer_personas.md       # Buyer knowledge base (Wet Cement)
│
├── execution/                  # Pipeline scripts
│   ├── enrich_pipeline_v3.py   # Main batched leads pipeline ⭐
│   ├── accounts_pipeline.py    # Accounts enrichment pipeline ⭐
│   ├── enrich_pipeline_v2.py   # Previous version
│   ├── enrich_pipeline.py      # Original version
│   ├── scrape_apify.py         # Apify lead discovery
│   ├── parse_sales_nav_csv.py  # Sales Navigator CSV parser
│   ├── import_leads.py         # Database import
│   └── update_sheet.py         # Google Sheets export
│
├── data/
│   ├── companies.py            # Target company definitions & domain mappings
│   └── markets.py              # Market configurations & location detection
│
├── db/
│   ├── connection.py           # Database connection
│   └── models.py               # SQLAlchemy ORM models
│
├── scrapers/
│   ├── apify.py                # Apify integration
│   └── catalog.py              # TMDb catalog lookup
│
├── enrichers/
│   ├── email.py                # Email enrichment
│   └── context.py              # Catalog context
│
├── utils.py                    # Shared utilities (logging, caching, retry, validation)
├── scoring.py                  # Lead scoring engine
├── output.py                   # Excel generation
│
├── .cache/                     # API result cache (gitignored)
│
└── output/                     # Generated files
    ├── truesync_leads_v3_*.xlsx
    ├── truesync_leads_v3_*.csv
    ├── pipeline_run_*.log
    └── by_market/
        └── leads_*.csv
```

---

## Utilities Module (`utils.py`)

The centralized utilities module provides:

### Logging
```python
from utils import setup_logging, get_logger

logger = setup_logging(output_dir='output', log_to_file=True)
logger.info("Pipeline started")
```

### Retry Logic
```python
from utils import retry_with_backoff

@retry_with_backoff(max_retries=3, base_delay=5.0)
def call_api():
    # API call that might fail
    pass
```

### API Caching
```python
from utils import APICache

cache = APICache(cache_dir='.cache', ttl_hours=24)
result = cache.get_or_fetch('my_key', api_call_function, arg1, arg2)
```

### Input Validation
```python
from utils import validate_json_file, validate_leads

leads = validate_json_file('input.json')  # Validates and loads
leads = validate_leads(raw_data)  # Validates list of dicts
```

---

## Data Sources (`data/`)

### Company Domains (`data/companies.py`)
Single source of truth for company→domain mappings:
```python
from data.companies import get_domain_for_company, generate_email

domain = get_domain_for_company("Warner Bros. Discovery")  # "wbd.com"
email = generate_email("John", "Smith", "netflix.com")  # "johnsmith@netflix.com"
```

### Market Detection (`data/markets.py`)
Robust location→market detection:
```python
from data.markets import detect_market, detect_markets_from_leads

market = detect_market("Los Angeles, California")  # "usa"
markets = detect_markets_from_leads(leads)  # {"usa", "uk", "france"}
```

---

## Troubleshooting

### "APIFY_TOKEN not set" error
```bash
export APIFY_TOKEN="apify_api_xxxxx"
# Or add to .env file
```

### Low LinkedIn URL rate
- Ensure names and companies are spelled correctly
- Some people may not have public LinkedIn profiles
- Check that company names match the target companies in `data/companies.py`

### Batch search timing out
- Reduce batch size in `google_search_linkedin_urls_batch()` (default: 20)
- Increase timeout in API calls

### Database connection errors
- Check `DATABASE_URL` format: `postgresql://user:pass@host/db`
- Ensure Neon Postgres is running
- Check network connectivity

### API calls failing repeatedly
- Check your Apify credits/quota
- Use `--skip-cache` to force fresh API calls
- Use `--clear-cache` to clear expired cache entries
- Check log files in `output/pipeline_run_*.log` for details

---

## Recent Improvements (v3.3 - January 2026)

### Changes (v3.3)
1. **Removed Lead Discovery** - Pipeline now only processes leads from Sales Navigator export (no additional leads discovered)
2. **Expanded ICP Roles** - Added AI, Localization, International Sales/Licensing, Chief Content Officer
3. **Simplified Pipeline** - 3 steps: LinkedIn URLs → Email Enrichment → Export

### Features (v3.2)
1. **Accounts Pipeline** - Separate pipeline for company enrichment with title counts
2. **Expanded ICP Roles** - Consumer Insights, Studio Owners, International Originals
3. **Universal Pictures Content Group** - Added with specific target roles
4. **Buyer Personas Knowledge Base** - Wet Cement doc integrated into directives

### Infrastructure (v3.1)
1. **Retry Logic** - Exponential backoff (3 retries, 5s base delay)
2. **API Caching** - 24-hour TTL, stored in `.cache/`
3. **Structured Logging** - Console + file logging with timestamps
4. **Input Validation** - Required field checks, data cleaning
5. **Centralized Domain Mappings** - Single source in `data/companies.py`
6. **Robust Market Detection** - Comprehensive location patterns
7. **Company-Specific Email Patterns** - Netflix uses `firstlast@`, others use `first.last@`
8. **New CLI Options** - `--skip-cache`, `--clear-cache`

### Database Tables
- `companies` - 31 target companies
- `leads` - Contact records with scoring
- `accounts` - Company enrichment data (title counts, contact counts)
- `enrichment_history` - API call tracking
- `scrape_runs` - Session logs

---

## License

Internal use only - Flawless AI
