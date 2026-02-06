# VFX Lead Generation Pipeline

Lead generation and enrichment pipeline targeting 208 VFX houses globally. Classifies leads into the 4-tier buyer triangle (Economic Buyers, Technical Champions, Day-to-Day Users, Procurement) and scores them for outreach prioritization.

## Quick Start

```bash
# 1. Set up environment
cd vfx-leads
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Edit .env with your APIFY_TOKEN (and optionally DATABASE_URL)

# 3. Parse Sales Navigator exports (supports multiple CSVs per tier search)
python execution/parse_sales_nav_csv.py tier1_eb.csv tier2_tc.csv tier3_users.csv tier4_proc.csv
# Or parse incrementally with --append
python execution/parse_sales_nav_csv.py new_export.csv --append

# 4. Dry-run: validate classification + company filter (no API credits used)
python execution/enrich_pipeline.py --input .tmp/vfx_leads_raw.json --skip-enrich --skip-db

# 5. Full enrichment: LinkedIn URLs + emails via Apify
python execution/enrich_pipeline.py --input .tmp/vfx_leads_raw.json --skip-db --drop-unclassified

# 6. Output: output/vfx_leads_*.xlsx
```

## Architecture

```
INPUT: Sales Navigator CSV
    |
    v
STEP 1: Parse & Validate (multi-CSV, LinkedIn URL extraction)
    |
    v
STEP 2: Filter to 208 Target Companies (strict)
    |
    v
STEP 3: Classify Persona Tier (EB / TC / User / Procurement)
    |
    v
STEP 4: LinkedIn URL Discovery (batched Google search)
    |
    v
STEP 5: Email Enrichment (profile scrape + leads-finder)
    |
    v
STEP 6: Score Leads (tier + seniority + company + market)
    |
    v
STEP 7: Deal Qualification (company-level readiness)
    |
    v
OUTPUT: Excel with sheets:
  - Master Lead List
  - By Persona Tier
  - Deal Qualification (per company)
  - Scoring Methodology
```

## The Buyer Triangle

Every serious opportunity at a VFX house should have:

| Tier | Role | Example Titles | Purpose |
|------|------|---------------|---------|
| 1 | **Economic Buyer** | Head of Post, MD, EP, COO | Signs budget, approves vendors |
| 2 | **Technical Champion** | VFX Supe, CG Supe, Pipeline TD | Validates quality, workflow fit |
| 3 | **Day-to-Day User** | Senior Compositor, Lead Roto | Creates bottom-up demand |
| 4 | **Procurement** | Procurement Mgr, Commercial Mgr | Later-stage only |

If any of tiers 1-3 are missing, it's not a qualified deal.

## Target Companies

208 VFX houses across 5 markets. **Only leads from these companies are processed.**

| Market | Count | Key Companies |
|--------|-------|--------------|
| USA | ~51 | ILM, Digital Domain, Zoic, Crafty Apes, FuseFX |
| UK | ~22 | DNEG, Framestore, Cinesite, Union VFX, One of Us |
| Canada | ~30 | Rodeo FX, Image Engine, Sony Imageworks, Spin VFX |
| India | ~6 | redchillies.vfx, Basilic Fly, PhantomFX |
| France | ~2 | MPC, The Mill |
| Unknown | ~97 | Location to be enriched |

## Scoring

Leads are scored 1-100 based on:

| Factor | Weight | Description |
|--------|--------|-------------|
| Persona Tier | 40% | Economic Buyer (100) > Champion (85) > User (55) > Procurement (40) |
| Seniority | 25% | C-Suite > VP/Director > Supervisor > Lead > IC |
| Company Relevance | 20% | Blockbuster credits, company profile |
| Market Priority | 15% | USA/UK (1.0x) > Canada (0.95x) > France (0.90x) > India (0.85x) |

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `APIFY_TOKEN` | Yes | LinkedIn URL + email enrichment |
| `DATABASE_URL` | No | Neon Postgres persistence |

## Project Structure

```
vfx-leads/
├── AGENTS.md                    # Agent instructions
├── README.md                    # This file
├── config.yaml                  # Pipeline configuration
├── requirements.txt             # Python dependencies
│
├── directives/
│   ├── vfx_personas.md          # Buyer personas (4-tier triangle)
│   └── scrape_leads.md          # Lead scraping SOP
│
├── data/
│   ├── companies.py             # 208 target VFX companies (STRICT)
│   ├── roles.py                 # Persona tier definitions
│   └── markets.py               # Market detection
│
├── execution/
│   ├── enrich_pipeline.py       # Main pipeline
│   └── parse_sales_nav_csv.py   # Sales Navigator CSV parser
│
├── scrapers/
│   └── apify.py                 # Apify integration
│
├── db/
│   ├── connection.py            # Database connection
│   └── models.py                # SQLAlchemy models
│
├── utils.py                     # Logging, caching, retry, validation
├── scoring.py                   # Lead scoring engine
├── output.py                    # Excel/CSV generation
│
├── .cache/                      # API result cache
├── .tmp/                        # Intermediate files
└── output/                      # Generated files
```
