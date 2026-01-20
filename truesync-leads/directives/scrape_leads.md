# TrueSync Lead Scraping & Enrichment

## Goal
Scrape and enrich leads using batched Apify actors, verify their relevance (ICP match > 80%), save to Neon Postgres database, and output to Excel/CSV for import to Google Sheets.

> **Related Directives:**
> - `directives/accounts_pipeline.md` - Company enrichment with title counts
> - `directives/buyer_personas.md` - Buyer knowledge base (who they are, what they care about)

## Key Principles

### BATCH EVERYTHING
All API calls should use batch processing to minimize execution time and API costs:
- **Google Search**: 20 queries per API call
- **Leads-finder**: All company domains in single call
- **Database**: Bulk inserts with session batching

### USE CENTRALIZED DATA SOURCES
All data definitions are in `data/` to avoid duplication:
- **Company domains**: `data/companies.py` → `get_domain_for_company()`
- **Market detection**: `data/markets.py` → `detect_market()`
- **Email patterns**: `data/companies.py` → `generate_email()`

### LEVERAGE BUILT-IN RELIABILITY
The pipeline has built-in protections:
- **Retry logic**: 3 retries with exponential backoff (5s, 10s, 20s delays)
- **API caching**: 24-hour TTL in `.cache/` directory
- **Input validation**: Required fields checked before processing
- **Structured logging**: Full audit trail in `output/pipeline_run_*.log`

## Inputs
- **Sales Navigator CSV/JSON**: Leads exported from LinkedIn Sales Navigator
- **Target Companies**: From `data/companies.py` (company domains/names)
- **ICP Roles**: From `config.yaml` (job titles to filter for)
- **Location**: Market region (UK, USA, Spain, Germany, France, Korea)

## Tools/Scripts

### Primary Pipeline (Recommended)
- Script: `execution/enrich_pipeline_v3.py` (batched, fastest)
- Actors: 
  - `apify/google-search-scraper` (LinkedIn URL discovery)
  - `code_crafter/leads-finder` (email + profile enrichment)

### Supporting Scripts
- `execution/parse_sales_nav_csv.py` - Parse Sales Navigator exports
- `execution/import_leads.py` - Database import
- `execution/update_sheet.py` - Google Sheets export

### Utility Modules
- `utils.py` - Logging, caching, retry logic, validation
- `data/companies.py` - Company domains, email patterns
- `data/markets.py` - Market detection from locations

### Dependencies
- `APIFY_TOKEN` in `.env`
- `DATABASE_URL` in `.env` (optional, for database push)

## Process

### 1. Prepare Input Data
```bash
# Parse Sales Navigator CSV export
python execution/parse_sales_nav_csv.py --input ~/Desktop/leads.csv --output .tmp/leads.json
```

### 2. Run Batched Pipeline
```bash
# Full pipeline with all enrichment
python execution/enrich_pipeline_v3.py --input .tmp/leads.json

# Skip database (for testing)
python execution/enrich_pipeline_v3.py --input .tmp/leads.json --skip-db

# Skip enrichment (just score and export)
python execution/enrich_pipeline_v3.py --input .tmp/leads.json --skip-enrich --skip-discovery

# Force fresh API calls (ignore cache)
python execution/enrich_pipeline_v3.py --input .tmp/leads.json --skip-cache

# Clear cache before running
python execution/enrich_pipeline_v3.py --input .tmp/leads.json --clear-cache
```

### 3. Pipeline Steps (Automated)

**INPUT: Validation & Setup**
- Load JSON file with leads
- Validate required fields (name, company, title)
- Detect markets from location strings
- Initialize logging to console and file

**PART 1: LinkedIn URL Discovery (Batched Google Search)**
- Batches 20 queries per API call
- Query format: `"Name" "Company" site:linkedin.com/in`
- Retry with exponential backoff on failure
- Results cached for 24 hours
- Expected success rate: 85-95%

**PART 2: Email Enrichment (Batched Domain Search)**
- All company domains in single API call
- Uses `code_crafter/leads-finder` actor
- Returns verified emails + LinkedIn URLs
- Fallback: company-specific email pattern generation
- Netflix uses `firstlast@netflix.com`, others use `first.last@domain.com`

**PART 3: Additional Lead Discovery**
- Finds leads at target companies not in Sales Navigator
- Matches ICP role criteria
- Deduplicates against existing leads
- Auto-detects market from location

**PART 4: Export & Database**
- Excel: Styled workbook with professional formatting
- CSV: For Google Sheets import
- Log: Full pipeline run audit trail
- Database: Bulk insert to Neon Postgres

### 4. Output
- Excel: `output/truesync_leads_v3_{timestamp}.xlsx`
- CSV: `output/truesync_leads_v3_{timestamp}.csv`
- Log: `output/pipeline_run_{timestamp}.log`

Output columns: Name, Title, Company, LinkedIn URL, Email, Location, Priority Score, Market

## Performance Expectations

| Leads | Execution Time | API Calls |
|-------|----------------|-----------|
| 50    | ~3-5 min       | ~5-8 calls |
| 100   | ~5-8 min       | ~8-12 calls |
| 200   | ~10-15 min     | ~15-20 calls |

## Target ICP Roles

### Primary ICPs (Real Buyers)

**#1 - International Acquisitions**
- Head of International Acquisitions
- VP International Acquisitions
- Director of Acquisitions
- Head of Content Acquisitions

**#2 - Content Partnerships**
- Head of International Content Partnerships
- VP Content Partnerships
- Head of International Content

**#3 - Global Distribution/Licensing**
- EVP Global Distribution
- SVP Global Licensing
- Head of International Sales
- VP International Distribution

### Secondary ICPs (Influencers)

**#4 - Content Strategy**
- Head of International Strategy
- VP Content Strategy
- Head of Portfolio Strategy

**#5 - AVOD/FAST Programming**
- Head of Programming
- VP Programming
- Director of Programming

**#6 - Consumer Insights / Data Science (Validation Partners)**
- Head of Consumer Insights
- VP Data Science
- Head of Content Analytics
- VP Consumer Research

**#7 - Studio Business Owners (Label/Franchise)**
- President of Studio
- Studio Head
- Head of Label
- EVP Franchise Development

**#8 - International Originals Leadership**
- Head of International Originals
- VP Local Originals
- Head of Local Content

**Specific Targets - Universal Pictures Content Group:**
- CFO / SVP Commercial Strategy (joint role)
- SVP Production, Programming & Operations (handles localization)

### Excluded Roles (NOT our ICP)
- Localization, Post-production
- Dubbing, Subtitling
- QC, Quality Control

## Company Targeting

### Tier 1 Markets (UK, USA, Spain)

| Market | Producers | Distributor | Platforms |
|--------|-----------|-------------|-----------|
| UK | BBC Studios, ITV Studios | All3Media | Sky, Channel 4 |
| USA | Lionsgate, Sony Pictures, Universal Pictures Content Group | Warner Bros. Discovery | Netflix US |
| Spain | Atresmedia, Mediapro | Beta Film | Netflix Spain |

### Tier 2 Markets (Germany, France, Korea)

| Market | Producers | Distributor | Platforms |
|--------|-----------|-------------|-----------|
| Germany | UFA, Constantin Film | Beta Film DE | RTL+ |
| France | Gaumont, StudioCanal | Newen | Canal+ |
| Korea | Studio Dragon, CJ ENM | SBS Contents Hub | Netflix Korea |

## Adding New Companies

To add a new company, update `data/companies.py`:

```python
# In get_company_domains() function:
'New Company': 'newcompany.com',

# If they use a non-standard email pattern, add to COMPANY_EMAIL_PATTERNS:
COMPANY_EMAIL_PATTERNS = {
    'newcompany.com': '{first}_{last}@{domain}',  # if they use underscores
}
```

## Adding New Markets/Locations

To add new location patterns, update `data/markets.py`:

```python
# In LOCATION_PATTERNS dict:
LOCATION_PATTERNS = {
    'new city': 'market_key',
    'new country': 'market_key',
}
```

## Apify Actor Configurations

### Google Search Scraper (Batched)
```python
{
    "queries": "query1\nquery2\nquery3",  # Newline-separated!
    "maxPagesPerQuery": 1,
    "resultsPerPage": 3,
}
```

### Leads-Finder (Batched Domains)
```python
{
    "contact_job_title": ["Head of Acquisitions", "VP Distribution"],
    "contact_location": ["united kingdom"],
    "contact_company_domain": [  # All domains at once!
        "bbcstudios.com",
        "sky.com",
        "channel4.com",
        "all3media.com",
        "itvstudios.com"
    ],
    "seniority_level": ["head", "director", "vp", "c_suite"],
    "fetch_count": 200
}
```

## Scoring Algorithm

| Factor | Points | Description |
|--------|--------|-------------|
| **Company** | +15-25 | Netflix/Amazon/WBD (+25), Lionsgate/BBC/Sky (+20), Pluto/Tubi/Roku (+15) |
| **Role** | +25-40 | Acquisitions/Distribution/Licensing (+40), Head of Content (+25) |
| **Seniority** | +12-25 | EVP/President (+25), SVP (+20), VP (+15), Director/Head (+12) |
| **Scope** | +8-15 | Global/Worldwide/International (+15), Group/Executive (+10), Regional (+8) |

**Score Ranges:**
- 🟢 75-100: High priority (hot leads)
- 🟡 50-74: Medium priority (qualified)
- 🔴 <50: Lower priority (nurture)

## Error Handling

### Built-in Protections
- **Retry logic**: Automatically retries failed API calls 3 times with exponential backoff
- **Caching**: Successful results cached for 24 hours to avoid redundant calls
- **Validation**: Input data validated before processing, skips invalid leads
- **Logging**: All errors logged to file for debugging

### Common Issues

| Error | Cause | Fix |
|-------|-------|-----|
| `APIFY_TOKEN not found` | Missing env var | Add to `.env` file |
| `Batch timeout` | Too many queries | Reduce batch size to 15 |
| `No LinkedIn URLs found` | Name/company mismatch | Check spelling, try variations |
| `Rate limit exceeded` | Too many API calls | Wait and retry (automatic) |
| `Stale cached data` | Old cache | Use `--clear-cache` flag |

### Checking Logs
```bash
# View latest log file
cat output/pipeline_run_*.log | tail -100

# Search for errors
grep -i "error\|failed" output/pipeline_run_*.log
```

### Self-Annealing Loop
When errors occur:
1. Check log file for error details
2. Fix the issue (script, input data, or API config)
3. Use `--skip-cache` to force fresh API calls
4. Update this directive with learnings
5. Run full pipeline

## Edge Cases

- **No leads found**: Broaden job titles or company domains
- **Low ICP match (<80%)**: Refine `contact_job_title` keywords
- **API Error**: Check `APIFY_TOKEN` and network connectivity
- **Duplicate leads**: Dedupe by name → email → LinkedIn URL
- **Empty LinkedIn URL**: Some people don't have public profiles - expected ~5-15% missing
- **Wrong market detected**: Add location patterns to `data/markets.py`
- **Missing company domain**: Add to `data/companies.py` (single source of truth)