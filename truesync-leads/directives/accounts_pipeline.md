# TrueSync Accounts Pipeline

## Goal

Enrich all target companies from `data/companies.py` with catalog data (title counts, top shows) and contact counts. Output to database and styled Excel workbook.

## Output Schema

| Column | Description | Source |
|--------|-------------|--------|
| Accounts | Company name | data/companies.py |
| Region | Market (UK, USA, Spain, etc.) | data/companies.py |
| No. of titles | Catalog size | TMDb or Google Search |
| Type of company | Producer/Distributor/Platform | data/companies.py |
| No. of contacts | Count of leads at company | Leads database |

## Data Sources (Priority Order)

1. **TMDb API** (primary) - Title counts, top shows, popularity scores
2. **Google Search Apify** (fallback) - If TMDb returns insufficient data
3. **Catalog Notes** (fallback) - Extract numbers from catalog_size field in companies.py
4. **Leads Database** - Contact counts per company

## Process

### 1. Load Companies

Load all target companies from `data/companies.py`:
- ~30 companies across 6 markets (UK, USA, Spain, Germany, France, Korea)
- Includes company type, LinkedIn URL, catalog notes

### 2. TMDb Enrichment

For each company, query TMDb API:
```python
from scrapers.catalog import TMDbClient
tmdb = TMDbClient()
show_data = tmdb.get_top_shows_formatted(company_name, market)
```

Returns:
- `total_catalog`: Number of titles
- `top_shows`: Comma-separated list of notable shows
- `show_details`: List with popularity scores

### 3. Google Search Fallback

If TMDb returns no data, use Google Search:
```
Query: "{company name}" production company catalog titles films TV shows
```

Parse results for:
- Numbers near "titles", "films", "shows", "hours"
- Catalog/library size mentions

### 4. Count Contacts

Query leads database:
```sql
SELECT company_name, COUNT(*) as contact_count
FROM leads
LEFT JOIN companies ON leads.company_id = companies.id
GROUP BY company_name
```

### 5. Export

- **Database**: Insert/update `accounts` table
- **Excel**: `output/accounts_{timestamp}.xlsx`
- **CSV**: `output/accounts_{timestamp}.csv`

## Usage

```bash
# Full pipeline
python execution/accounts_pipeline.py

# Skip database push (Excel only)
python execution/accounts_pipeline.py --skip-db

# Force fresh API calls (ignore cache)
python execution/accounts_pipeline.py --skip-cache

# Clear cache before running
python execution/accounts_pipeline.py --clear-cache
```

## Dependencies

| Variable | Required | Purpose |
|----------|----------|---------|
| `TMDB_ACCESS_TOKEN` | ⚠️ Recommended | TMDb catalog data |
| `APIFY_TOKEN` | ⚠️ Optional | Google Search fallback |
| `DATABASE_URL` | ⚠️ Optional | Contact counts + DB export |

## Output Files

| File | Description |
|------|-------------|
| `output/accounts_{timestamp}.xlsx` | Styled Excel with "Accounts" and "Show Details" sheets |
| `output/accounts_{timestamp}.csv` | Plain CSV for Google Sheets import |
| `output/pipeline_run_{timestamp}.log` | Full run log |

## Excel Sheets

### Sheet 1: "Accounts" (Main)

| Accounts | Region | No. of titles | Type of company | No. of contacts |
|----------|--------|---------------|-----------------|-----------------|
| BBC Studios | UK | 2,500 | Producer | 12 |
| Netflix US | USA | 15,000 | Platform | 24 |
| Gaumont | France | 1,600 | Producer | 8 |

### Sheet 2: "Show Details"

| Account | Top Shows | Popularity Score | Data Source |
|---------|-----------|------------------|-------------|
| BBC Studios | Doctor Who (2005, EN), Top Gear... | 85 | tmdb |
| Gaumont | Lupin (2021, FR), Narcos... | 72 | tmdb |

## Database Schema

Table: `accounts`

```sql
CREATE TABLE accounts (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    region VARCHAR(50) NOT NULL,
    num_titles INTEGER DEFAULT 0,
    company_type VARCHAR(50) NOT NULL,
    num_contacts INTEGER DEFAULT 0,
    top_shows TEXT,
    tmdb_id INTEGER,
    popularity_score INTEGER DEFAULT 0,
    data_source VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Caching

- API results cached for 24 hours in `.cache/`
- Cache keys: `tmdb_company_{name}`, `google_catalog_{name}`
- Use `--skip-cache` to force fresh calls
- Use `--clear-cache` to clear all cached data

## Error Handling

| Error | Cause | Fix |
|-------|-------|-----|
| `TMDB credentials not configured` | Missing env var | Set `TMDB_ACCESS_TOKEN` or `TMDB_API_KEY` |
| `APIFY_TOKEN not found` | Missing env var | Set `APIFY_TOKEN` for Google Search fallback |
| `DATABASE_URL not found` | Missing env var | Set `DATABASE_URL` or use `--skip-db` |
| `No title count found` | Company not in TMDb | Will use catalog_notes as fallback |

## Integration with Leads Pipeline

The accounts pipeline complements `enrich_pipeline_v3.py`:

| Pipeline | Output | Focus |
|----------|--------|-------|
| `enrich_pipeline_v3.py` | Leads (contacts) | People: names, titles, emails, scores |
| `accounts_pipeline.py` | Accounts (companies) | Companies: title counts, contact counts |

Run both to get complete picture:
```bash
# 1. Enrich leads
python execution/enrich_pipeline_v3.py --input .tmp/leads.json

# 2. Enrich accounts
python execution/accounts_pipeline.py
```

## Adding New Companies

To add a company, update `data/companies.py`:

```python
{
    'name': 'New Company',
    'type': 'Producer',  # or Distributor/Platform
    'market': 'usa',     # or uk/spain/germany/france/korea
    'catalog_size': '500+ titles',
    'catalog_notes': 'Key titles: Show A, Show B...'
}
```

The accounts pipeline will automatically pick it up on next run.
