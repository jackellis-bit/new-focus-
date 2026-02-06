# VFX Lead Scraping & Enrichment

## Goal
Scrape and enrich VFX leads from Sales Navigator exports, classify by persona tier, score, and export. **Only process leads from the 208 target VFX companies.**

> **Related Directives:**
> - `directives/vfx_personas.md` - Buyer personas and deal qualification

## Key Principles

### STRICT COMPANY FILTER
Only leads from companies in `data/companies.py` are processed. All others are rejected. No exceptions. No company discovery.

### BATCH EVERYTHING
All API calls use batch processing:
- **Google Search**: 20 queries per API call
- **Leads-finder**: All company domains in single call

### USE CENTRALIZED DATA
- **Target companies**: `data/companies.py`
- **Persona tiers**: `data/roles.py`
- **Market detection**: `data/markets.py`

## Inputs
- **Sales Navigator CSV**: Leads exported from LinkedIn Sales Navigator
- **Target Companies**: Strictly from `data/companies.py` (208 VFX houses)
- **Persona Tiers**: From `data/roles.py`

## Tools/Scripts

### Primary Pipeline
- Script: `execution/enrich_pipeline.py`
- Actors:
  - `apify/google-search-scraper` (LinkedIn URL discovery)
  - `code_crafter/leads-finder` (email enrichment)

### Supporting Scripts
- `execution/parse_sales_nav_csv.py` - Parse Sales Navigator exports

## Process

### 1. Export from Sales Navigator
Run 4 separate searches (one per persona tier) in Sales Navigator.
See "Sales Navigator Search Specifications" section below.

### 2. Parse CSV(s)
```bash
# All 4 tier exports at once (recommended)
python execution/parse_sales_nav_csv.py tier1_eb.csv tier2_tc.csv tier3_users.csv tier4_proc.csv

# Or one at a time using --append
python execution/parse_sales_nav_csv.py tier1_eb.csv
python execution/parse_sales_nav_csv.py tier2_tc.csv --append
python execution/parse_sales_nav_csv.py tier3_users.csv --append
python execution/parse_sales_nav_csv.py tier4_proc.csv --append

# Custom output path
python execution/parse_sales_nav_csv.py export.csv --output .tmp/vfx_leads_raw.json
```

### 3. Run Pipeline
```bash
# Dry-run first: validate classification + company filter (no API credits)
python execution/enrich_pipeline.py --input .tmp/vfx_leads_raw.json --skip-enrich --skip-db

# Full enrichment (LinkedIn URLs + emails)
python execution/enrich_pipeline.py --input .tmp/vfx_leads_raw.json --skip-db --drop-unclassified

# Full pipeline with database push
python execution/enrich_pipeline.py --input .tmp/vfx_leads_raw.json --drop-unclassified
```

### 4. Output
- Excel: `output/vfx_leads_{timestamp}.xlsx`
- CSV: `output/vfx_leads_{timestamp}.csv`
- Log: `output/pipeline_run_{timestamp}.log`

Output columns: Name, Title, Company, Persona Tier, LinkedIn URL, Email, Location, Market, Score

## Sales Navigator Search Specifications

Run these 4 searches separately in LinkedIn Sales Navigator and export each as CSV.

### Search 1: Economic Buyers
**Title filter (OR):**
- Head of Post Production
- Head of Production
- Managing Director
- Executive Producer
- Head of VFX
- COO OR Chief Operating Officer
- Operations Director
- Head of Operations
- Head of Innovation
- Head of Technology
- CTO OR Chief Technology Officer
- CEO
- President
- General Manager
- Studio Director
- Chief Creative Officer

**Company filter:** Add target VFX companies from your list
**Seniority:** Director, VP, CXO, Owner, Partner

### Search 2: Technical Champions
**Title filter (OR):**
- VFX Supervisor
- CG Supervisor
- Compositing Supervisor
- Head of 2D
- Head of Comp
- Pipeline TD
- Head of Pipeline
- Pipeline Supervisor
- Technical Director
- Head of R&D
- Head of CG
- Head of 3D
- DFX Supervisor
- Lighting Supervisor
- Animation Supervisor
- FX Supervisor
- Look Development Supervisor

**Company filter:** Add target VFX companies from your list
**Seniority:** Senior, Manager, Director, VP

### Search 3: Day-to-Day Users
**Title filter (OR):**
- Senior Compositor
- Lead Compositor
- Lead Roto Artist
- Lead Paint Artist
- Prep Supervisor
- Sequence Lead
- Senior Roto Artist
- Lead Matchmove Artist
- Rotoscope Supervisor
- Paint Supervisor
- 2D Lead

**Company filter:** Add target VFX companies from your list
**Seniority:** Senior, Manager

### Search 4: Procurement (Later Stage)
**Title filter (OR):**
- Procurement Manager
- Commercial Manager
- Vendor Manager
- Head of Procurement
- Commercial Director
- Head of Commercial
- Finance Director

**Company filter:** Add target VFX companies from your list
**Seniority:** Manager, Director, VP

## Scoring

| Factor | Weight | Description |
|--------|--------|-------------|
| Persona Tier | 40% | Economic Buyer (100), Technical Champion (85), User (55), Procurement (40) |
| Seniority | 25% | C-Suite (100), VP/Director (80-88), Supervisor (75), Lead (65) |
| Company Relevance | 20% | Blockbuster credits (100), Notable projects (70), Standard (55) |
| Market Priority | 15% | USA/UK (1.0x), Canada (0.95x), France (0.90x), India (0.85x) |

## Error Handling

### Common Issues

| Error | Fix |
|-------|-----|
| `APIFY_TOKEN not found` | Add to `.env` |
| `No target companies found` | Check company names match `data/companies.py` |
| `All leads rejected` | Sales Nav search not targeting right companies |
| `Low LinkedIn URL rate` | Check name/company spelling |
