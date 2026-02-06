# Agent Instructions

> VFX Lead Generation Pipeline - Agent operating instructions.

You operate within a 3-layer architecture (DOE: Directive-Orchestration-Execution).

## The 3-Layer Architecture

**Layer 1: Directive (What to do)**
- SOPs in `directives/`
- `directives/vfx_personas.md` - Buyer personas (4-tier triangle)
- `directives/scrape_leads.md` - Lead scraping SOP

**Layer 2: Orchestration (Decision making)**
- This is you. Read directives, call execution tools, handle errors.

**Layer 3: Execution (Doing the work)**
- Deterministic Python scripts in `execution/`
- Environment variables in `.env`

## Key Constraint: STRICT COMPANY TARGETING

This pipeline ONLY processes leads from the 208 target VFX companies defined in `data/companies.py`. No exceptions. No company discovery. Any leads from non-target companies must be rejected.

## Operating Principles

1. **Check for tools first** - Before writing a script, check `execution/`.
2. **Self-anneal when things break** - Fix, test, update directive.
3. **Update directives as you learn** - Directives are living documents.

## File Organization

- `.tmp/` - Intermediate files (Sales Nav JSON, temp exports)
- `.cache/` - API result cache (24h TTL)
- `execution/` - Python scripts
- `directives/` - SOPs
- `data/` - Company list, role definitions, market detection
- `output/` - Generated Excel/CSV files

## Available Scripts

| Script | Purpose |
|--------|---------|
| `execution/enrich_pipeline.py` | Main enrichment pipeline |
| `execution/parse_sales_nav_csv.py` | Parse Sales Navigator CSV exports |

## Workflow

```bash
# 1. Parse Sales Navigator export(s) - supports multiple CSVs and --append
python execution/parse_sales_nav_csv.py tier1_eb.csv tier2_tc.csv tier3_users.csv tier4_proc.csv

# Or parse one at a time and append
python execution/parse_sales_nav_csv.py tier1_eb.csv
python execution/parse_sales_nav_csv.py tier2_tc.csv --append

# 2. Dry-run: validate classification + company filtering (no API credits used)
python execution/enrich_pipeline.py --input .tmp/vfx_leads_raw.json --skip-enrich --skip-db

# 3. Full enrichment (LinkedIn URLs + emails via Apify)
python execution/enrich_pipeline.py --input .tmp/vfx_leads_raw.json --skip-db --drop-unclassified

# 4. Output in output/vfx_leads_*.xlsx
```

## Data Architecture

| Module | Purpose |
|--------|---------|
| `data/companies.py` | 208 target VFX companies (STRICT filter) |
| `data/roles.py` | 4-tier persona definitions + title classification |
| `data/markets.py` | USA, UK, Canada, India, France market detection |
| `scoring.py` | Lead scoring engine |
| `output.py` | Excel/CSV generation |
| `utils.py` | Logging, caching, retry, validation |

## Persona Tiers

| Tier | Label | Score | Purpose |
|------|-------|-------|---------|
| 1 | Economic Buyer | 100 | Signs budget, approves vendors |
| 2 | Technical Champion | 85 | Validates quality, workflow fit |
| 3 | Day-to-Day User | 55 | Creates bottom-up demand |
| 4 | Procurement | 40 | Later-stage, contract terms |

**Deal qualification**: Company needs all 3 of tiers 1, 2, and 3 to be qualified.
