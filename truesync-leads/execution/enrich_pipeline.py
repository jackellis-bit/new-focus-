#!/usr/bin/env python3
"""
Full lead enrichment pipeline:
1. Load parsed leads from Sales Navigator CSV
2. Filter to target companies
3. Score leads based on ICP
4. BULK enrich with emails via Apify code_crafter/leads-finder
5. Export to Google Sheet
6. Push to Neon Postgres database
"""
import os
import sys
import json
import time
import argparse
import uuid
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
load_dotenv()

# Target companies for UK market
TARGET_COMPANIES = [
    'bbc studios', 'sky', 'channel 4', 'all3media', 'itv studios'
]

# ICP role keywords (high value)
ICP_ROLES_HIGH = [
    'acquisitions', 'distribution', 'licensing', 'content sales',
    'content partnerships', 'programming', 'content strategy'
]

# ICP role keywords (medium value)
ICP_ROLES_MEDIUM = [
    'head of content', 'vp content', 'svp content', 'evp content',
    'director content', 'global head'
]

# Domain mapping for companies
COMPANY_DOMAINS = {
    'bbc studios': 'bbcstudios.com',
    'sky': 'sky.com', 
    'channel 4': 'channel4.com',
    'all3media': 'all3media.com',
    'itv studios': 'itvstudios.com',
}


def is_target_company(company: str) -> bool:
    """Check if company is in our target list."""
    if not company:
        return False
    company_lower = company.lower()
    return any(target in company_lower for target in TARGET_COMPANIES)


def get_company_key(company: str) -> str:
    """Get the normalized company key."""
    if not company:
        return None
    company_lower = company.lower()
    for key in COMPANY_DOMAINS.keys():
        if key in company_lower:
            return key
    return None


def score_lead(lead: dict) -> int:
    """Score a lead based on ICP match. Returns score 0-100."""
    score = 0
    title = (lead.get('title') or '').lower()
    company = (lead.get('company') or '').lower()
    
    # Company type score (0-25)
    if 'sky' in company or 'bbc studios' in company:
        score += 25
    elif 'channel 4' in company or 'itv' in company:
        score += 20
    elif 'all3media' in company:
        score += 15
    
    # Role relevance score (0-40)
    for keyword in ICP_ROLES_HIGH:
        if keyword in title:
            score += 40
            break
    else:
        for keyword in ICP_ROLES_MEDIUM:
            if keyword in title:
                score += 25
                break
    
    # Seniority score (0-20)
    if any(x in title for x in ['svp', 'evp', 'senior vice president', 'executive vice president']):
        score += 20
    elif any(x in title for x in ['vp', 'vice president', 'director']):
        score += 15
    elif any(x in title for x in ['head of', 'global head', 'group head']):
        score += 12
    elif 'manager' in title:
        score += 5
    
    # Decision authority bonus (0-15)
    if any(x in title for x in ['global', 'group', 'executive', 'chief']):
        score += 15
    
    return min(score, 100)


def name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity between two names."""
    if not name1 or not name2:
        return 0
    # Normalize names
    n1 = name1.lower().strip()
    n2 = name2.lower().strip()
    return SequenceMatcher(None, n1, n2).ratio()


def bulk_enrich_with_apify(leads: list, location: str = "united kingdom") -> list:
    """
    BULK enrich leads with emails using Apify code_crafter/leads-finder.
    Makes ONE bulk API call per company domain, then matches results to our leads.
    """
    token = os.getenv('APIFY_TOKEN')
    if not token:
        print("❌ APIFY_TOKEN not found - cannot enrich emails!")
        return leads
    
    from apify_client import ApifyClient
    client = ApifyClient(token)
    
    actor_id = "code_crafter/leads-finder"
    
    # Group leads by company
    leads_by_company = {}
    for lead in leads:
        company_key = get_company_key(lead.get('company', ''))
        if company_key:
            if company_key not in leads_by_company:
                leads_by_company[company_key] = []
            leads_by_company[company_key].append(lead)
    
    print(f"\n🔍 BULK Enriching leads via Apify...")
    print(f"   Actor: {actor_id}")
    print(f"   Companies: {list(leads_by_company.keys())}")
    
    # Track matches
    total_matched = 0
    apify_results_cache = {}
    
    # Make ONE bulk call per company
    for company_key, company_leads in leads_by_company.items():
        domain = COMPANY_DOMAINS.get(company_key)
        if not domain:
            continue
        
        print(f"\n   📧 Searching {company_key} ({len(company_leads)} leads to match)...")
        
        # Build job title filter from our leads' titles
        job_titles = set()
        for lead in company_leads:
            title = lead.get('title', '')
            if title:
                # Extract key parts of title
                title_lower = title.lower()
                if 'head of' in title_lower:
                    job_titles.add('Head of')
                if 'vp' in title_lower or 'vice president' in title_lower:
                    job_titles.add('VP')
                if 'director' in title_lower:
                    job_titles.add('Director')
                if 'svp' in title_lower:
                    job_titles.add('SVP')
                if 'content' in title_lower:
                    job_titles.add('Content')
                if 'licensing' in title_lower:
                    job_titles.add('Licensing')
                if 'acquisitions' in title_lower:
                    job_titles.add('Acquisitions')
        
        try:
            # BULK search for this company
            run_input = {
                "contact_location": [location],
                "contact_company_domain": [domain],
                "seniority_level": ["head", "director", "vp", "c_suite"],
                "fetch_count": min(len(company_leads) * 3, 100),  # Get more to increase match chance
            }
            
            print(f"      Calling Apify with domain={domain}, fetch_count={run_input['fetch_count']}...")
            
            run = client.actor(actor_id).call(
                run_input=run_input,
                timeout_secs=120,
                memory_mbytes=512
            )
            
            # Collect all results
            apify_leads = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            print(f"      ✅ Got {len(apify_leads)} leads from Apify")
            
            # Cache results for this company
            apify_results_cache[company_key] = apify_leads
            
            # Match Apify results to our leads by name
            for lead in company_leads:
                our_name = lead.get('name', '')
                best_match = None
                best_score = 0
                
                for apify_lead in apify_leads:
                    # Build full name from Apify result
                    apify_name = f"{apify_lead.get('first_name', '')} {apify_lead.get('last_name', '')}".strip()
                    if not apify_name:
                        apify_name = apify_lead.get('full_name', apify_lead.get('name', ''))
                    
                    similarity = name_similarity(our_name, apify_name)
                    
                    if similarity > best_score and similarity > 0.7:  # 70% threshold
                        best_score = similarity
                        best_match = apify_lead
                
                if best_match and best_match.get('email'):
                    lead['email'] = best_match['email']
                    lead['email_source'] = 'apify_verified'
                    lead['linkedin_url'] = best_match.get('linkedin_url', lead.get('linkedin_url', ''))
                    total_matched += 1
                    print(f"      ✓ Matched: {our_name} -> {best_match.get('email')}")
                else:
                    # Fallback to pattern-based email
                    name_parts = our_name.replace('.', ' ').split()
                    if len(name_parts) >= 2:
                        first = name_parts[0].lower()
                        last = name_parts[-1].lower()
                        lead['email'] = f"{first}.{last}@{domain}"
                        lead['email_source'] = 'pattern_guess'
                    
        except Exception as e:
            print(f"      ❌ Error: {e}")
            # Fallback to pattern for all leads in this company
            for lead in company_leads:
                name_parts = lead.get('name', '').replace('.', ' ').split()
                if len(name_parts) >= 2 and domain:
                    first = name_parts[0].lower()
                    last = name_parts[-1].lower()
                    lead['email'] = f"{first}.{last}@{domain}"
                    lead['email_source'] = 'pattern_guess'
    
    print(f"\n   ✅ Bulk enrichment complete!")
    print(f"      Verified matches: {total_matched}/{len(leads)}")
    
    return leads


def push_to_database(leads: list, market: str = 'UK') -> int:
    """Push leads to Neon Postgres database."""
    try:
        from db.connection import get_engine
        from db.models import Lead, Company
        from sqlalchemy.orm import Session
        from sqlalchemy import select
    except ImportError as e:
        print(f"⚠ Database modules not available: {e}")
        return 0
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("⚠ DATABASE_URL not found - skipping database push")
        return 0
    
    print(f"\n💾 Pushing {len(leads)} leads to database...")
    
    try:
        engine = get_engine()
        inserted = 0
        updated = 0
        
        with Session(engine) as session:
            # Get or create company mappings
            company_ids = {}
            
            for lead in leads:
                company_name = lead.get('company', 'Unknown')
                
                # Check if company exists
                if company_name not in company_ids:
                    stmt = select(Company).where(Company.name == company_name)
                    company = session.execute(stmt).scalar_one_or_none()
                    
                    if company:
                        company_ids[company_name] = company.id
                    else:
                        # Create company
                        new_company = Company(
                            id=str(uuid.uuid4()),
                            name=company_name,
                            type='platform' if 'sky' in company_name.lower() else 'producer',
                            market=market
                        )
                        session.add(new_company)
                        session.flush()
                        company_ids[company_name] = new_company.id
                
                # Check if lead already exists (by name + company)
                stmt = select(Lead).where(
                    Lead.name == lead.get('name'),
                    Lead.company_id == company_ids.get(company_name)
                )
                existing = session.execute(stmt).scalar_one_or_none()
                
                if existing:
                    # Update existing lead
                    if lead.get('email') and not existing.email:
                        existing.email = lead['email']
                        updated += 1
                    existing.title = lead.get('title') or existing.title
                    existing.priority_score = lead.get('score', 0)
                else:
                    # Create new lead
                    # Generate a unique placeholder if no LinkedIn URL
                    linkedin_url = lead.get('linkedin_url', '')
                    if not linkedin_url:
                        linkedin_url = None  # Use NULL instead of empty string
                    
                    new_lead = Lead(
                        id=str(uuid.uuid4()),
                        name=lead.get('name'),
                        title=lead.get('title'),
                        company_id=company_ids.get(company_name),
                        email=lead.get('email'),
                        market=market,
                        priority_score=lead.get('score', 0),
                        linkedin_url=linkedin_url,
                    )
                    session.add(new_lead)
                    inserted += 1
            
            session.commit()
        
        print(f"   ✅ Inserted {inserted} new leads, updated {updated} existing")
        return inserted
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return 0


def export_to_sheets(leads: list) -> str:
    """Export leads to Excel/CSV for Google Sheets import."""
    import pandas as pd
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"output/truesync_leads_enriched_{timestamp}.xlsx"
    
    df_data = []
    for lead in leads:
        df_data.append({
            'Name': lead.get('name', ''),
            'Title': lead.get('title', ''),
            'Company': lead.get('company', ''),
            'Location': lead.get('location', ''),
            'Email': lead.get('email', ''),
            'Email Source': lead.get('email_source', 'unknown'),
            'LinkedIn URL': lead.get('linkedin_url', ''),
            'ICP Score': lead.get('score', 0),
            'Market': 'UK',
        })
    
    df = pd.DataFrame(df_data)
    df = df.sort_values('ICP Score', ascending=False)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False, sheet_name='Enriched Leads')
    
    # Also CSV
    csv_path = output_path.replace('.xlsx', '.csv')
    df.to_csv(csv_path, index=False)
    
    print(f"\n📊 Exported to: {output_path}")
    print(f"   CSV: {csv_path}")
    
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Full lead enrichment pipeline with BULK Apify")
    parser.add_argument("--input", default=".tmp/uk_leads_raw.json", help="Input JSON file")
    parser.add_argument("--market", default="UK", help="Market name")
    parser.add_argument("--location", default="united kingdom", help="Location for Apify search")
    parser.add_argument("--skip-enrich", action="store_true", help="Skip Apify email enrichment")
    parser.add_argument("--skip-db", action="store_true", help="Skip database push")
    parser.add_argument("--min-score", type=int, default=0, help="Minimum ICP score")
    
    args = parser.parse_args()
    
    print("="*70)
    print("🚀 TRUESYNC LEAD ENRICHMENT PIPELINE (BULK MODE)")
    print("="*70)
    
    # Step 1: Load leads
    input_path = Path(__file__).parent.parent / args.input
    print(f"\n📂 Step 1: Loading leads from: {input_path}")
    
    with open(input_path, 'r') as f:
        leads = json.load(f)
    print(f"   Loaded {len(leads)} leads")
    
    # Step 2: Filter to target companies
    print(f"\n🎯 Step 2: Filtering to target companies...")
    filtered = [l for l in leads if is_target_company(l.get('company', ''))]
    print(f"   {len(filtered)} leads in target companies")
    
    # Step 3: Score leads
    print(f"\n📊 Step 3: Scoring leads by ICP match...")
    for lead in filtered:
        lead['score'] = score_lead(lead)
    
    # Filter by minimum score
    if args.min_score > 0:
        filtered = [l for l in filtered if l['score'] >= args.min_score]
        print(f"   {len(filtered)} leads with score >= {args.min_score}")
    
    # Sort by score
    filtered.sort(key=lambda x: x['score'], reverse=True)
    
    # Step 4: BULK Enrich with Apify
    if not args.skip_enrich:
        print(f"\n🔍 Step 4: BULK Enriching with Apify...")
        filtered = bulk_enrich_with_apify(filtered, args.location)
    else:
        print(f"\n⏭ Step 4: Skipping Apify enrichment")
        # Fallback to pattern emails
        for lead in filtered:
            company_key = get_company_key(lead.get('company', ''))
            domain = COMPANY_DOMAINS.get(company_key) if company_key else None
            if domain:
                name_parts = lead.get('name', '').replace('.', ' ').split()
                if len(name_parts) >= 2:
                    lead['email'] = f"{name_parts[0].lower()}.{name_parts[-1].lower()}@{domain}"
                    lead['email_source'] = 'pattern_guess'
    
    # Step 5: Export
    print(f"\n📤 Step 5: Exporting...")
    output_path = export_to_sheets(filtered)
    
    # Step 6: Push to database
    if not args.skip_db:
        print(f"\n💾 Step 6: Pushing to database...")
        push_to_database(filtered, args.market)
    else:
        print(f"\n⏭ Step 6: Skipping database push")
    
    # Summary
    verified = sum(1 for l in filtered if l.get('email_source') == 'apify_verified')
    pattern = sum(1 for l in filtered if l.get('email_source') == 'pattern_guess')
    
    print(f"\n{'='*70}")
    print(f"✅ PIPELINE COMPLETE")
    print(f"{'='*70}")
    print(f"   Total leads: {len(filtered)}")
    print(f"   ✅ Verified emails (Apify): {verified}")
    print(f"   📧 Pattern-based emails: {pattern}")
    print(f"   Average ICP score: {sum(l['score'] for l in filtered) / len(filtered):.1f}")
    print(f"\n   Output: {output_path}")
    
    # Top leads
    print(f"\n🏆 Top 10 Leads:")
    for lead in filtered[:10]:
        email = lead.get('email', 'N/A')[:35]
        icon = "✅" if lead.get('email_source') == 'apify_verified' else "📧"
        print(f"   {lead['score']:>3} | {lead['name']:<25} | {email:<35} {icon}")


if __name__ == "__main__":
    main()
