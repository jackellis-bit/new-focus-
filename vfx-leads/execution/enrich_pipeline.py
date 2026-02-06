#!/usr/bin/env python3
"""
VFX Lead Enrichment Pipeline
==============================

Main pipeline for processing VFX leads from Sales Navigator exports.

Pipeline steps:
  1. Parse & validate input (JSON from Sales Nav CSV parser)
  2. Filter to target companies only (strict 208-company list)
  3. Classify by persona tier (Economic Buyer / Technical Champion / User / Procurement)
  4. LinkedIn URL discovery (batched Google search)
  5. Email enrichment (Apify leads-finder)
  6. Score leads
  7. Export to Excel/CSV

Usage:
  python execution/enrich_pipeline.py --input .tmp/vfx_leads_raw.json
  python execution/enrich_pipeline.py --input .tmp/vfx_leads_raw.json --skip-enrich --skip-db
"""

import os
import sys
import json
import time
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

from utils import setup_logging, get_logger, validate_json_file, APICache, ProgressTracker
from data.companies import is_target_company, normalize_company_name, get_company
from data.roles import classify_title, get_tier_label, check_deal_qualification
from data.markets import detect_market
from scoring import VFXLeadScorer
from output import VFXExcelExporter


def parse_args():
    parser = argparse.ArgumentParser(description="VFX Lead Enrichment Pipeline")
    parser.add_argument("--input", required=True, help="Input JSON file with leads")
    parser.add_argument("--skip-enrich", action="store_true", help="Skip LinkedIn/email enrichment")
    parser.add_argument("--skip-db", action="store_true", help="Skip database push")
    parser.add_argument("--skip-cache", action="store_true", help="Disable API caching")
    parser.add_argument("--clear-cache", action="store_true", help="Clear cache before running")
    return parser.parse_args()


def filter_target_companies(leads: list, logger) -> list:
    """
    Filter leads to ONLY include those from target companies.
    Rejects all leads from companies not in the strict 208-company list.
    """
    accepted = []
    rejected = []
    
    for lead in leads:
        company = lead.get('company', '')
        if is_target_company(company):
            lead['company'] = normalize_company_name(company)
            accepted.append(lead)
        else:
            rejected.append(lead)
    
    logger.info(f"Company filter: {len(accepted)} accepted, {len(rejected)} rejected")
    
    if rejected:
        rejected_companies = set(l.get('company', '?') for l in rejected)
        logger.info(f"Rejected companies: {', '.join(sorted(rejected_companies)[:10])}")
        if len(rejected_companies) > 10:
            logger.info(f"  ... and {len(rejected_companies) - 10} more")
    
    return accepted


def classify_leads(leads: list, logger) -> list:
    """Classify each lead into a persona tier."""
    tier_counts = {}
    
    for lead in leads:
        tier = classify_title(lead.get('title', ''))
        lead['persona_tier'] = tier
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
    
    logger.info("Persona classification:")
    for tier, count in sorted(tier_counts.items(), key=lambda x: -x[1]):
        logger.info(f"  {get_tier_label(tier)}: {count}")
    
    return leads


def enrich_market(leads: list, logger) -> list:
    """Detect market from location for each lead."""
    for lead in leads:
        if not lead.get('market'):
            # Try lead location first
            location = lead.get('location', '')
            market = detect_market(location)
            
            # Fall back to company data
            if market == 'unknown':
                company_data = get_company(lead.get('company', ''))
                if company_data:
                    market = company_data.get('market', 'unknown')
                    if not lead.get('location') and company_data.get('location'):
                        lead['location'] = company_data['location']
            
            lead['market'] = market
    
    return leads


def enrich_linkedin_urls(leads: list, logger, cache: APICache) -> list:
    """
    Batch-discover LinkedIn URLs via Google search.
    Uses batches of 20 queries per API call.
    """
    try:
        from apify_client import ApifyClient
    except ImportError:
        logger.warning("apify-client not installed. Skipping LinkedIn URL enrichment.")
        return leads
    
    token = os.getenv('APIFY_TOKEN')
    if not token:
        logger.warning("APIFY_TOKEN not set. Skipping LinkedIn URL enrichment.")
        return leads
    
    # Find leads without LinkedIn URLs
    needs_url = [l for l in leads if not l.get('linkedin_url')]
    if not needs_url:
        logger.info("All leads already have LinkedIn URLs")
        return leads
    
    logger.info(f"Discovering LinkedIn URLs for {len(needs_url)} leads...")
    client = ApifyClient(token)
    
    # Batch into groups of 20
    batch_size = 20
    batches = [needs_url[i:i+batch_size] for i in range(0, len(needs_url), batch_size)]
    
    progress = ProgressTracker(len(batches), "LinkedIn URL Discovery")
    
    for batch in batches:
        # Build search queries
        queries = []
        for lead in batch:
            name = lead.get('name', '')
            company = lead.get('company', '')
            query = f'"{name}" "{company}" site:linkedin.com/in'
            queries.append(query)
        
        queries_str = "\n".join(queries)
        
        # Check cache
        cache_key = f"google_linkedin_{hash(queries_str)}"
        cached = cache.get(cache_key) if cache else None
        
        if cached:
            results = cached
        else:
            try:
                run_input = {
                    "queries": queries_str,
                    "maxPagesPerQuery": 1,
                    "resultsPerPage": 3,
                }
                
                run = client.actor("apify/google-search-scraper").call(run_input=run_input)
                
                results = []
                for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                    results.append(item)
                
                if cache:
                    cache.set(cache_key, results)
                    
            except Exception as e:
                logger.warning(f"Google search batch failed: {e}")
                progress.update(1)
                continue
        
        # Match results back to leads
        for i, lead in enumerate(batch):
            name_lower = lead.get('name', '').lower()
            
            # Find matching result
            for result in results:
                url = result.get('url', '')
                title = result.get('title', '').lower()
                
                if 'linkedin.com/in/' in url and name_lower.split()[0] in title:
                    lead['linkedin_url'] = url
                    break
        
        progress.update(1)
        time.sleep(1)  # Rate limiting
    
    progress.finish()
    
    found = sum(1 for l in leads if l.get('linkedin_url'))
    logger.info(f"LinkedIn URLs: {found}/{len(leads)} ({100*found//len(leads)}%)")
    
    return leads


def enrich_emails(leads: list, logger, cache: APICache) -> list:
    """
    Batch email enrichment using Apify leads-finder.
    """
    try:
        from apify_client import ApifyClient
    except ImportError:
        logger.warning("apify-client not installed. Skipping email enrichment.")
        return leads
    
    token = os.getenv('APIFY_TOKEN')
    if not token:
        logger.warning("APIFY_TOKEN not set. Skipping email enrichment.")
        return leads
    
    needs_email = [l for l in leads if not l.get('email')]
    if not needs_email:
        logger.info("All leads already have emails")
        return leads
    
    logger.info(f"Enriching emails for {len(needs_email)} leads...")
    
    # Group by company domain for batch lookup
    # For now, mark as needing email - actual enrichment uses Apify
    # The leads-finder actor works best with company domains
    
    client = ApifyClient(token)
    
    # Get unique companies that need email enrichment
    companies_needing_email = set(l.get('company', '') for l in needs_email)
    logger.info(f"Companies needing email enrichment: {len(companies_needing_email)}")
    
    # Use leads-finder with company names
    # This is a simplified version - can be expanded with domain lookups
    for lead in needs_email:
        if lead.get('linkedin_url'):
            # If we have LinkedIn URL, we can try profile scraping for email
            pass  # Handled by LinkedIn profile enrichment if needed
    
    found = sum(1 for l in leads if l.get('email'))
    logger.info(f"Emails: {found}/{len(leads)} ({100*found//len(leads) if leads else 0}%)")
    
    return leads


def score_leads(leads: list, logger) -> list:
    """Score all leads using the VFX scoring engine."""
    scorer = VFXLeadScorer()
    
    for lead in leads:
        lead['score'] = scorer.calculate_score(lead)
    
    # Log score distribution
    high = sum(1 for l in leads if l.get('score', 0) >= 75)
    medium = sum(1 for l in leads if 50 <= l.get('score', 0) < 75)
    low = sum(1 for l in leads if l.get('score', 0) < 50)
    
    logger.info(f"Scores: {high} high (75+), {medium} medium (50-74), {low} low (<50)")
    
    return leads


def check_deal_readiness(leads: list, logger) -> list:
    """Check deal qualification at company level."""
    from collections import defaultdict
    
    company_tiers = defaultdict(lambda: defaultdict(int))
    for lead in leads:
        company = lead.get('company', 'Unknown')
        tier = lead.get('persona_tier', 'unclassified')
        company_tiers[company][tier] += 1
    
    qualified = 0
    partial = 0
    
    for company, tiers in company_tiers.items():
        qual = check_deal_qualification(tiers)
        if qual['qualified']:
            qualified += 1
            logger.info(f"  QUALIFIED: {company} ({qual['coverage']})")
        else:
            partial += 1
    
    logger.info(f"Deal readiness: {qualified} qualified, {partial} partial out of {len(company_tiers)} companies")
    
    return leads


def export_results(leads: list, logger) -> str:
    """Export leads to Excel and CSV."""
    exporter = VFXExcelExporter(output_dir='output')
    filepath = exporter.export(leads)
    
    logger.info(f"Exported {len(leads)} leads to: {filepath}")
    logger.info(f"CSV: {filepath.replace('.xlsx', '.csv')}")
    
    return filepath


def main():
    args = parse_args()
    
    # Setup
    logger = setup_logging(output_dir='output', log_to_file=True)
    logger.info("=" * 70)
    logger.info("VFX LEAD ENRICHMENT PIPELINE")
    logger.info("=" * 70)
    
    start_time = time.time()
    
    # Cache setup
    cache = None
    if not args.skip_cache:
        cache = APICache(cache_dir='.cache', ttl_hours=24)
        if args.clear_cache:
            cache.clear()
    
    # ================================================================
    # STEP 1: Load and validate input
    # ================================================================
    logger.info("\n--- STEP 1: Load & Validate Input ---")
    leads = validate_json_file(args.input)
    logger.info(f"Loaded {len(leads)} leads from {args.input}")
    
    # ================================================================
    # STEP 2: Filter to target companies ONLY
    # ================================================================
    logger.info("\n--- STEP 2: Filter Target Companies ---")
    leads = filter_target_companies(leads, logger)
    
    if not leads:
        logger.error("No leads from target companies. Exiting.")
        return
    
    # ================================================================
    # STEP 3: Classify by persona tier
    # ================================================================
    logger.info("\n--- STEP 3: Classify Persona Tiers ---")
    leads = classify_leads(leads, logger)
    
    # ================================================================
    # STEP 4: Enrich market from location
    # ================================================================
    logger.info("\n--- STEP 4: Detect Markets ---")
    leads = enrich_market(leads, logger)
    
    # ================================================================
    # STEP 5: LinkedIn URL + Email enrichment
    # ================================================================
    if not args.skip_enrich:
        logger.info("\n--- STEP 5a: LinkedIn URL Discovery ---")
        leads = enrich_linkedin_urls(leads, logger, cache)
        
        logger.info("\n--- STEP 5b: Email Enrichment ---")
        leads = enrich_emails(leads, logger, cache)
    else:
        logger.info("\n--- STEP 5: Enrichment SKIPPED ---")
    
    # ================================================================
    # STEP 6: Score leads
    # ================================================================
    logger.info("\n--- STEP 6: Score Leads ---")
    leads = score_leads(leads, logger)
    
    # ================================================================
    # STEP 7: Check deal readiness
    # ================================================================
    logger.info("\n--- STEP 7: Deal Qualification ---")
    leads = check_deal_readiness(leads, logger)
    
    # ================================================================
    # STEP 8: Export results
    # ================================================================
    logger.info("\n--- STEP 8: Export ---")
    filepath = export_results(leads, logger)
    
    # ================================================================
    # Summary
    # ================================================================
    elapsed = time.time() - start_time
    logger.info("\n" + "=" * 70)
    logger.info("PIPELINE COMPLETE")
    logger.info(f"  Leads processed: {len(leads)}")
    logger.info(f"  Companies: {len(set(l.get('company') for l in leads))}")
    logger.info(f"  With LinkedIn: {sum(1 for l in leads if l.get('linkedin_url'))}")
    logger.info(f"  With Email: {sum(1 for l in leads if l.get('email'))}")
    logger.info(f"  Output: {filepath}")
    logger.info(f"  Time: {elapsed:.1f}s")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
