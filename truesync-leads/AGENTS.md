# Agent Instructions

> This file is mirrored across CLAUDE.md, AGENTS.md, and GEMINI.md so the same instructions load in any AI environment.

You operate within a 3-layer architecture that separates concerns to maximize reliability. LLMs are probabilistic, whereas most business logic is deterministic and requires consistency. This system fixes that mismatch.

## The 3-Layer Architecture

**Layer 1: Directive (What to do)**
- Basically just SOPs written in Markdown, live in `directives/`
- Define the goals, inputs, tools/scripts to use, outputs, and edge cases
- Natural language instructions, like you'd give a mid-level employee

**Layer 2: Orchestration (Decision making)**
- This is you. Your job: intelligent routing.
- Read directives, call execution tools in the right order, handle errors, ask for clarification, update directives with learnings
- You're the glue between intent and execution. E.g you don't try scraping websites yourself—you read `directives/scrape_leads.md` and come up with inputs/outputs and then run `execution/scrape_apify.py`

**Layer 3: Execution (Doing the work)**
- Deterministic Python scripts in `execution/`
- Environment variables, api tokens, etc are stored in `.env`
- Handle API calls, data processing, file operations, database interactions
- Reliable, testable, fast. Use scripts instead of manual work.

**Why this works:** if you do everything yourself, errors compound. 90% accuracy per step = 59% success over 5 steps. The solution is push complexity into deterministic code. That way you just focus on decision-making.

## Operating Principles

**1. Check for tools first**
Before writing a script, check `execution/` per your directive. Only create new scripts if none exist.

**2. Self-anneal when things break**
- Read error message and stack trace
- Fix the script and test it again (unless it uses paid tokens/credits/etc—in which case you check w user first)
- Update the directive with what you learned (API limits, timing, edge cases)
- Example: you hit an API rate limit → you then look into API → find a batch endpoint that would fix → rewrite script to accommodate → test → update directive.

**3. Update directives as you learn**
Directives are living documents. When you discover API constraints, better approaches, common errors, or timing expectations—update the directive. But don't create or overwrite directives without asking unless explicitly told to. Directives are your instruction set and must be preserved (and improved upon over time, not extemporaneously used and then discarded).

## Self-annealing loop

Errors are learning opportunities. When something breaks:
1. Fix it
2. Update the tool
3. Test tool, make sure it works
4. Update directive to include new flow
5. System is now stronger

## File Organization

**Deliverables vs Intermediates:**
- **Deliverables**: Google Sheets, Google Slides, or other cloud-based outputs that the user can access
- **Intermediates**: Temporary files needed during processing

**Directory structure:**
- `.tmp/` - All intermediate files (dossiers, scraped data, temp exports). Never commit, always regenerated.
- `.cache/` - API result cache (24h TTL). Can be cleared with `--clear-cache` flag.
- `execution/` - Python scripts (the deterministic tools)
- `directives/` - SOPs in Markdown (the instruction set)
- `data/` - Centralized data definitions (companies, markets, domains)
- `.env` - Environment variables and API keys
- `credentials.json`, `token.json` - Google OAuth credentials (required files, in `.gitignore`)

**Key principle:** Local files are only for processing. Deliverables live in cloud services (Google Sheets, Slides, etc.) where the user can access them. Everything in `.tmp/` can be deleted and regenerated.

## Summary

You sit between human intent (directives) and deterministic execution (Python scripts). Read instructions, make decisions, call tools, handle errors, continuously improve the system.

Be pragmatic. Be reliable. Self-anneal.

---

## TrueSync Lead Pipeline - Specific Tools

### Main Pipeline: `execution/enrich_pipeline_v3.py`

The primary lead enrichment pipeline. Uses **batch processing** for all API calls. Supports **multi-market** leads (USA, UK, France, Spain, Germany, South Korea).

**Key Features (v3.2):**
- Retry logic with exponential backoff (3 retries, 5s base delay)
- API result caching (24h TTL) in `.cache/`
- Structured logging to console and file
- Input validation and cleaning
- Company-specific email patterns
- **Target company filtering**: Discovered leads only include contacts from companies in `data/companies.py`
- **Expanded job titles**: Discovery searches for 25+ ICP-aligned roles (see buyer_personas.md)

```bash
# Full workflow from Sales Navigator export:
python execution/parse_sales_nav_csv.py "/path/to/export.csv"  # Step 1: Parse CSV
python execution/enrich_pipeline_v3.py --input .tmp/uk_leads_raw.json --market Global --skip-db  # Step 2: Enrich

# Options:
#   --input            Input JSON file with leads
#   --market           Market name (Global, UK, USA, etc.)
#   --skip-enrich      Skip LinkedIn/email enrichment
#   --skip-discovery   Skip additional lead discovery
#   --skip-db          Skip database push
#   --skip-cache       Disable API result caching (force fresh calls)
#   --clear-cache      Clear cache before running
#   --filter-companies Only process leads from predefined target companies
```

### Batch Processing Strategy

| Task | Old Approach | New Approach | Speedup |
|------|-------------|--------------|---------|
| LinkedIn URL lookup | 1 Google search per lead | 20 queries per API call | 20x fewer calls |
| Email enrichment | 1 Apify call per domain | All domains in 1 call | 5x fewer calls |
| Lead discovery | Manual | Auto-discovers similar roles at target companies only | New feature |

**Lead Discovery Filtering**: The pipeline only adds discovered leads from companies in `data/companies.py`. This prevents contacts from non-target companies (e.g. random companies returned by Apify) from polluting the output.

### Centralized Data Sources

| Module | Purpose |
|--------|---------|
| `data/companies.py` | Company definitions, domain mappings, email patterns |
| `data/markets.py` | Market definitions, location→market detection |
| `utils.py` | Logging, caching, retry logic, validation |
| `directives/buyer_personas.md` | ICP definitions, role titles, objection handling |

### Discovery Job Titles

The pipeline searches for leads with these ICP-aligned roles (defined in `enrich_pipeline_v3.py`):

| Category | Example Titles |
|----------|---------------|
| Acquisitions | Head of Acquisitions, VP Acquisitions, Director of Acquisitions |
| Distribution | Head of Distribution, VP Distribution |
| Licensing & Sales | Head of Licensing, Head of Content Sales, VP Content Partnerships |
| Programming & Content | Head of Programming, Head of Content, SVP/EVP Content |
| Consumer Insights | Head of Consumer Insights, VP Data Science, Head of Content Analytics |
| Studio Business | President of Studio, Studio Head, EVP Franchise Development |
| International Originals | Head of International Originals, VP Local Originals, Head of Local Content |
| Universal-specific | CFO, SVP Commercial Strategy, SVP Production, SVP Programming |

```python
# Use centralized functions instead of duplicating logic:
from data.companies import get_domain_for_company, generate_email
from data.markets import detect_market
from utils import setup_logging, retry_with_backoff, APICache

domain = get_domain_for_company("Netflix")  # "netflix.com"
email = generate_email("John", "Smith", "netflix.com")  # "johnsmith@netflix.com"
market = detect_market("Los Angeles, California")  # "usa"
```

### Available Execution Scripts

| Script | Purpose |
|--------|---------|
| `enrich_pipeline_v3.py` | Main batched leads pipeline (recommended) |
| `accounts_pipeline.py` | Company enrichment with title counts and contact counts |
| `parse_sales_nav_csv.py` | Parse messy LinkedIn Sales Navigator CSV exports |
| `scrape_apify.py` | Direct Apify actor calls |
| `import_leads.py` | Import leads to database |
| `update_sheet.py` | Export to Google Sheets |

### Accounts Pipeline: `execution/accounts_pipeline.py`

Enriches all target companies from `data/companies.py` with catalog data and contact counts.

**Output Schema:** Accounts, Region, No. of titles, Type of company, No. of contacts

```bash
# Full pipeline
python execution/accounts_pipeline.py

# Skip database push (Excel only)
python execution/accounts_pipeline.py --skip-db

# Force fresh API calls
python execution/accounts_pipeline.py --skip-cache
```

**Data Sources:**
1. TMDb API (primary) - Title counts, top shows
2. Google Search Apify (fallback) - If TMDb insufficient
3. Leads database - Contact counts per company

### Apify Actors

| Actor | Purpose | Batch Support |
|-------|---------|---------------|
| `apify/google-search-scraper` | LinkedIn URL discovery | ✅ 20 queries/call |
| `code_crafter/leads-finder` | Email + profile enrichment + lead discovery | ✅ All domains/call |

### Output Format

Pipeline outputs to `output/` directory:
- **Excel**: Styled workbook with dark blue headers, color-coded priority scores
- **CSV**: Plain CSV for Google Sheets import
- **Log**: Full run log with timestamps (`pipeline_run_*.log`)
- **Market CSVs**: `output/by_market/leads_{market}.csv` - separate files per market

Columns: Name, Title, Company, LinkedIn URL, Email, Location, Priority Score, Market

### Supported Markets & Companies

**Markets (auto-detected from location):**
- USA, UK, France, Germany, Spain, South Korea

**Companies (auto-detected domains):**
- Major Studios: Warner Bros. Discovery, Sony Pictures, Lionsgate, Netflix, Amazon/Prime Video
- Streaming/FAST: Pluto TV, Tubi, Roku
- European: Studiocanal, Canal+, Gaumont, Beta Film
- UK: BBC Studios, Sky, Channel 4, ITV Studios, All3Media

### Troubleshooting

| Issue | Solution |
|-------|----------|
| API calls failing | Check logs in `output/pipeline_run_*.log`, retry logic will attempt 3 times |
| Stale cached data | Use `--clear-cache` or `--skip-cache` |
| Missing domains | Add to `data/companies.py` - single source of truth |
| Wrong market detected | Update patterns in `data/markets.py` |
