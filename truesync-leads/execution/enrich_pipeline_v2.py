#!/usr/bin/env python3
"""
Enhanced Lead Enrichment Pipeline v2:

PART 1: Email Enrichment for Known Leads
  - Use snipercoder/bulk-linkedin-email-finder to find emails for our Sales Nav leads
  
PART 2: Lead Discovery  
  - Use code_crafter/leads-finder to discover additional leads at target companies
  
PART 3: Export & Database
  - Merge all leads, export to Excel/CSV, push to database
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

# Target companies
TARGET_COMPANIES = {
    'bbc studios': 'bbcstudios.com',
    'sky': 'sky.com', 
    'channel 4': 'channel4.com',
    'all3media': 'all3media.com',
    'itv studios': 'itvstudios.com',
}

# ICP role keywords
ICP_ROLES_HIGH = [
    'acquisitions', 'distribution', 'licensing', 'content sales',
    'content partnerships', 'programming', 'content strategy'
]

ICP_ROLES_MEDIUM = [
    'head of content', 'vp content', 'svp content', 'evp content',
    'director content', 'global head'
]

# Job titles for lead discovery
DISCOVERY_JOB_TITLES = [
    "Head of Acquisitions",
    "VP Acquisitions", 
    "Director of Acquisitions",
    "Head of Distribution",
    "VP Distribution",
    "Head of Licensing",
    "Head of Content Sales",
    "VP Content Partnerships",
    "Head of Programming",
]


def get_company_key(company: str) -> str:
    """Get normalized company key."""
    if not company:
        return None
    company_lower = company.lower()
    for key in TARGET_COMPANIES.keys():
        if key in company_lower:
            return key
    return None


def score_lead(lead: dict) -> int:
    """Score a lead based on ICP match."""
    score = 0
    title = (lead.get('title') or '').lower()
    company = (lead.get('company') or '').lower()
    
    if 'sky' in company or 'bbc studios' in company:
        score += 25
    elif 'channel 4' in company or 'itv' in company:
        score += 20
    elif 'all3media' in company:
        score += 15
    
    for keyword in ICP_ROLES_HIGH:
        if keyword in title:
            score += 40
            break
    else:
        for keyword in ICP_ROLES_MEDIUM:
            if keyword in title:
                score += 25
                break
    
    if any(x in title for x in ['svp', 'evp', 'senior vice president']):
        score += 20
    elif any(x in title for x in ['vp', 'vice president', 'director']):
        score += 15
    elif any(x in title for x in ['head of', 'global head', 'group head']):
        score += 12
    
    if any(x in title for x in ['global', 'group', 'executive', 'chief']):
        score += 15
    
    return min(score, 100)


def name_similarity(name1: str, name2: str) -> float:
    """Calculate name similarity."""
    if not name1 or not name2:
        return 0
    return SequenceMatcher(None, name1.lower().strip(), name2.lower().strip()).ratio()


# ============================================================================
# PART 1: Email Enrichment using snipercoder/bulk-linkedin-email-finder
# ============================================================================

def enrich_emails_bulk(leads: list) -> list:
    """
    PART 1: Find emails for known leads using bulk email finder.
    Uses snipercoder/bulk-linkedin-email-finder or similar.
    """
    token = os.getenv('APIFY_TOKEN')
    if not token:
        print("❌ APIFY_TOKEN not found")
        return leads
    
    from apify_client import ApifyClient
    client = ApifyClient(token)
    
    # Try snipercoder/bulk-linkedin-email-finder first
    actor_id = "snipercoder/bulk-linkedin-email-finder"
    
    print(f"\n{'='*60}")
    print(f"📧 PART 1: Email Enrichment for Known Leads")
    print(f"{'='*60}")
    print(f"   Actor: {actor_id}")
    print(f"   Leads to enrich: {len(leads)}")
    
    # Prepare input for bulk email finder
    # Format: list of {firstName, lastName, companyDomain}
    enrichment_input = []
    for lead in leads:
        name_parts = lead.get('name', '').replace('.', ' ').split()
        if len(name_parts) < 2:
            continue
            
        company_key = get_company_key(lead.get('company', ''))
        domain = TARGET_COMPANIES.get(company_key) if company_key else None
        
        if domain:
            enrichment_input.append({
                "firstName": name_parts[0],
                "lastName": name_parts[-1],
                "companyDomain": domain,
                "fullName": lead.get('name'),  # For matching back
            })
    
    if not enrichment_input:
        print("   ⚠ No valid leads to enrich")
        return leads
    
    print(f"   Prepared {len(enrichment_input)} leads for enrichment")
    
    try:
        # Call bulk email finder
        run_input = {
            "leads": enrichment_input,
        }
        
        print(f"   🔍 Calling Apify bulk email finder...")
        
        run = client.actor(actor_id).call(
            run_input=run_input,
            timeout_secs=300,
            memory_mbytes=1024
        )
        
        # Get results
        results = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        print(f"   ✅ Got {len(results)} email results")
        
        # Match results back to leads
        emails_found = 0
        for result in results:
            result_name = f"{result.get('firstName', '')} {result.get('lastName', '')}".strip()
            result_email = result.get('email', '')
            
            if not result_email:
                continue
            
            # Find matching lead
            for lead in leads:
                if name_similarity(lead.get('name', ''), result_name) > 0.8:
                    lead['email'] = result_email
                    lead['email_source'] = 'apify_verified'
                    lead['linkedin_url'] = result.get('linkedinUrl', lead.get('linkedin_url', ''))
                    emails_found += 1
                    print(f"      ✓ {lead['name']}: {result_email}")
                    break
        
        print(f"\n   ✅ Verified emails found: {emails_found}/{len(leads)}")
        
    except Exception as e:
        error_msg = str(e)
        print(f"   ⚠ Actor error: {error_msg[:100]}")
        print(f"   Falling back to alternative method...")
        
        # Fallback: Try a different email finder approach
        leads = enrich_emails_fallback(leads, client)
    
    # Apply pattern-based emails for remaining leads without email
    pattern_count = 0
    for lead in leads:
        if not lead.get('email'):
            company_key = get_company_key(lead.get('company', ''))
            domain = TARGET_COMPANIES.get(company_key) if company_key else None
            if domain:
                name_parts = lead.get('name', '').replace('.', ' ').split()
                if len(name_parts) >= 2:
                    lead['email'] = f"{name_parts[0].lower()}.{name_parts[-1].lower()}@{domain}"
                    lead['email_source'] = 'pattern_guess'
                    pattern_count += 1
    
    if pattern_count > 0:
        print(f"   📧 Pattern-based emails added: {pattern_count}")
    
    return leads


def enrich_emails_fallback(leads: list, client) -> list:
    """
    Fallback email enrichment using global_api/email-search-actor
    or individual lookups.
    """
    print(f"\n   🔄 Trying fallback email enrichment...")
    
    # Group by company domain
    by_domain = {}
    for lead in leads:
        company_key = get_company_key(lead.get('company', ''))
        domain = TARGET_COMPANIES.get(company_key) if company_key else None
        if domain:
            if domain not in by_domain:
                by_domain[domain] = []
            by_domain[domain].append(lead)
    
    # Try global_api/email-search-actor per domain
    actor_id = "global_api/email-search-actor"
    
    for domain, domain_leads in by_domain.items():
        try:
            print(f"      Searching {domain}...")
            
            run = client.actor(actor_id).call(
                run_input={
                    "domain": domain,
                    "maxEmails": len(domain_leads) * 2,
                },
                timeout_secs=120
            )
            
            results = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            
            # Try to match emails to leads by name
            for result in results:
                email = result.get('email', '')
                if not email:
                    continue
                
                # Extract name from email (e.g., john.smith@domain.com -> John Smith)
                email_name = email.split('@')[0].replace('.', ' ').replace('_', ' ')
                
                for lead in domain_leads:
                    if not lead.get('email') and name_similarity(lead.get('name', ''), email_name) > 0.6:
                        lead['email'] = email
                        lead['email_source'] = 'apify_verified'
                        print(f"         ✓ {lead['name']}: {email}")
                        break
                        
        except Exception as e:
            print(f"         ⚠ {domain}: {str(e)[:50]}")
            continue
    
    return leads


# ============================================================================
# PART 2: Lead Discovery using code_crafter/leads-finder
# ============================================================================

def discover_additional_leads(existing_leads: list, location: str = "united kingdom") -> list:
    """
    PART 2: Discover additional leads at target companies that weren't
    in the Sales Navigator export.
    """
    token = os.getenv('APIFY_TOKEN')
    if not token:
        print("❌ APIFY_TOKEN not found")
        return []
    
    from apify_client import ApifyClient
    client = ApifyClient(token)
    
    actor_id = "code_crafter/leads-finder"
    
    print(f"\n{'='*60}")
    print(f"🔍 PART 2: Discover Additional Leads")
    print(f"{'='*60}")
    print(f"   Actor: {actor_id}")
    print(f"   Location: {location}")
    
    # Create set of existing names for deduplication
    existing_names = {lead.get('name', '').lower().strip() for lead in existing_leads}
    
    new_leads = []
    
    for company_key, domain in TARGET_COMPANIES.items():
        print(f"\n   📧 Searching {company_key} for additional roles...")
        
        try:
            run_input = {
                "contact_location": [location],
                "contact_company_domain": [domain],
                "contact_job_title": DISCOVERY_JOB_TITLES,
                "seniority_level": ["head", "director", "vp", "c_suite"],
                "fetch_count": 50,
            }
            
            run = client.actor(actor_id).call(
                run_input=run_input,
                timeout_secs=120,
                memory_mbytes=512
            )
            
            results = list(client.dataset(run["defaultDatasetId"]).iterate_items())
            print(f"      Found {len(results)} leads from Apify")
            
            # Filter to NEW leads only
            for result in results:
                name = f"{result.get('first_name', '')} {result.get('last_name', '')}".strip()
                if not name:
                    name = result.get('full_name', result.get('name', ''))
                
                # Skip if already exists
                if name.lower().strip() in existing_names:
                    continue
                
                # Create new lead
                new_lead = {
                    'name': name,
                    'title': result.get('job_title', result.get('title', '')),
                    'company': result.get('company_name', company_key.title()),
                    'email': result.get('email', ''),
                    'email_source': 'apify_verified' if result.get('email') else '',
                    'linkedin_url': result.get('linkedin_url', ''),
                    'location': result.get('location', location),
                    'source': 'apify_discovery',
                }
                new_lead['score'] = score_lead(new_lead)
                
                new_leads.append(new_lead)
                existing_names.add(name.lower().strip())
                
                if result.get('email'):
                    print(f"      ✓ NEW: {name} | {result.get('email')}")
            
        except Exception as e:
            print(f"      ⚠ Error: {str(e)[:50]}")
            continue
    
    print(f"\n   ✅ Discovered {len(new_leads)} NEW leads")
    verified = sum(1 for l in new_leads if l.get('email_source') == 'apify_verified')
    print(f"      With verified emails: {verified}")
    
    return new_leads


# ============================================================================
# PART 3: Export & Database
# ============================================================================

def export_to_sheets(leads: list) -> str:
    """Export leads to Excel/CSV."""
    import pandas as pd
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_path = f"output/truesync_leads_v2_{timestamp}.xlsx"
    
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
            'Source': lead.get('source', 'sales_nav'),
            'Market': 'UK',
        })
    
    df = pd.DataFrame(df_data)
    df = df.sort_values('ICP Score', ascending=False)
    
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(output_path, index=False, sheet_name='All Leads')
    
    csv_path = output_path.replace('.xlsx', '.csv')
    df.to_csv(csv_path, index=False)
    
    print(f"\n📊 Exported to: {output_path}")
    print(f"   CSV: {csv_path}")
    
    return output_path


def push_to_database(leads: list, market: str = 'UK') -> int:
    """Push leads to database."""
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
        print("⚠ DATABASE_URL not found")
        return 0
    
    print(f"\n💾 Pushing {len(leads)} leads to database...")
    
    try:
        engine = get_engine()
        inserted = 0
        updated = 0
        
        with Session(engine) as session:
            company_ids = {}
            
            for lead in leads:
                company_name = lead.get('company', 'Unknown')
                
                if company_name not in company_ids:
                    stmt = select(Company).where(Company.name == company_name)
                    company = session.execute(stmt).scalar_one_or_none()
                    
                    if company:
                        company_ids[company_name] = company.id
                    else:
                        new_company = Company(
                            id=str(uuid.uuid4()),
                            name=company_name,
                            type='platform' if 'sky' in company_name.lower() else 'producer',
                            market=market
                        )
                        session.add(new_company)
                        session.flush()
                        company_ids[company_name] = new_company.id
                
                # Check for existing lead by name
                stmt = select(Lead).where(Lead.name == lead.get('name'))
                existing = session.execute(stmt).scalar_one_or_none()
                
                if existing:
                    # Update if we have better data
                    if lead.get('email') and not existing.email:
                        existing.email = lead['email']
                        updated += 1
                    if lead.get('linkedin_url') and not existing.linkedin_url:
                        existing.linkedin_url = lead['linkedin_url']
                else:
                    linkedin_url = lead.get('linkedin_url') or None
                    
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
        
        print(f"   ✅ Inserted: {inserted}, Updated: {updated}")
        return inserted
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return 0


# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Enhanced Lead Pipeline v2")
    parser.add_argument("--input", default=".tmp/uk_leads_raw.json", help="Input JSON")
    parser.add_argument("--market", default="UK", help="Market name")
    parser.add_argument("--location", default="united kingdom", help="Location filter")
    parser.add_argument("--skip-enrich", action="store_true", help="Skip email enrichment")
    parser.add_argument("--skip-discovery", action="store_true", help="Skip lead discovery")
    parser.add_argument("--skip-db", action="store_true", help="Skip database push")
    
    args = parser.parse_args()
    
    print("="*70)
    print("🚀 TRUESYNC LEAD PIPELINE v2")
    print("="*70)
    
    # Load existing leads
    input_path = Path(__file__).parent.parent / args.input
    print(f"\n📂 Loading leads from: {input_path}")
    
    with open(input_path, 'r') as f:
        leads = json.load(f)
    
    # Filter to target companies
    leads = [l for l in leads if get_company_key(l.get('company', ''))]
    print(f"   Loaded {len(leads)} leads in target companies")
    
    # Score leads
    for lead in leads:
        lead['score'] = score_lead(lead)
        lead['source'] = 'sales_nav'
    
    # PART 1: Email Enrichment
    if not args.skip_enrich:
        leads = enrich_emails_bulk(leads)
    else:
        print(f"\n⏭ Skipping email enrichment")
        # Add pattern emails
        for lead in leads:
            if not lead.get('email'):
                company_key = get_company_key(lead.get('company', ''))
                domain = TARGET_COMPANIES.get(company_key)
                if domain:
                    name_parts = lead.get('name', '').replace('.', ' ').split()
                    if len(name_parts) >= 2:
                        lead['email'] = f"{name_parts[0].lower()}.{name_parts[-1].lower()}@{domain}"
                        lead['email_source'] = 'pattern_guess'
    
    # PART 2: Lead Discovery
    new_leads = []
    if not args.skip_discovery:
        new_leads = discover_additional_leads(leads, args.location)
        leads.extend(new_leads)
    else:
        print(f"\n⏭ Skipping lead discovery")
    
    # Sort all leads by score
    leads.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    # PART 3: Export
    print(f"\n{'='*60}")
    print(f"📤 PART 3: Export & Database")
    print(f"{'='*60}")
    
    output_path = export_to_sheets(leads)
    
    if not args.skip_db:
        push_to_database(leads, args.market)
    else:
        print(f"\n⏭ Skipping database push")
    
    # Summary
    verified = sum(1 for l in leads if l.get('email_source') == 'apify_verified')
    pattern = sum(1 for l in leads if l.get('email_source') == 'pattern_guess')
    from_sales_nav = sum(1 for l in leads if l.get('source') == 'sales_nav')
    from_discovery = sum(1 for l in leads if l.get('source') == 'apify_discovery')
    
    print(f"\n{'='*70}")
    print(f"✅ PIPELINE COMPLETE")
    print(f"{'='*70}")
    print(f"\n   📊 Lead Summary:")
    print(f"      Total leads: {len(leads)}")
    print(f"      From Sales Navigator: {from_sales_nav}")
    print(f"      From Apify Discovery: {from_discovery}")
    print(f"\n   📧 Email Summary:")
    print(f"      Verified (Apify): {verified}")
    print(f"      Pattern-based: {pattern}")
    print(f"\n   Average ICP score: {sum(l.get('score', 0) for l in leads) / len(leads):.1f}")
    print(f"\n   Output: {output_path}")
    
    # Top leads
    print(f"\n🏆 Top 15 Leads:")
    for lead in leads[:15]:
        email = lead.get('email', 'N/A')[:30]
        icon = "✅" if lead.get('email_source') == 'apify_verified' else "📧"
        src = "🔍" if lead.get('source') == 'apify_discovery' else "📋"
        print(f"   {lead.get('score', 0):>3} | {lead['name']:<25} | {email:<30} {icon} {src}")


if __name__ == "__main__":
    main()
