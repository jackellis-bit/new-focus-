#!/usr/bin/env python3
"""
Apify Lead Scraper
==================

Scrapes leads using the code_crafter/leads-finder Apify actor.
This single actor provides verified emails, LinkedIn URLs, and company data.

Usage:
    # Test scrape (25 leads)
    python execution/scrape_apify.py --test
    
    # Scrape specific company domain
    python execution/scrape_apify.py --company_domain bbcstudios.com --location "United Kingdom" --fetch_count 50
    
    # Scrape by job titles only
    python execution/scrape_apify.py --location "United States" --fetch_count 100

Environment Variables:
    APIFY_TOKEN - Required for API access
    DATABASE_URL - Optional, for database insertion

Output:
    .tmp/leads_[timestamp].json - Scraped leads data
    LEADS table - If DATABASE_URL is set
    SCRAPE_RUNS table - Logs the run
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

try:
    from apify_client import ApifyClient
except ImportError:
    print("Error: apify-client not installed. Run: pip install apify-client")
    sys.exit(1)


# Default ICP roles from config.yaml
DEFAULT_JOB_TITLES = [
    # Primary ICP #1: Acquisitions
    "Head of International Acquisitions",
    "VP International Acquisitions", 
    "Director of Acquisitions",
    "Head of Content Acquisitions",
    "VP Content Acquisitions",
    "SVP Acquisitions",
    # Primary ICP #2: Partnerships
    "Head of International Content Partnerships",
    "VP Content Partnerships",
    "Head of International Content",
    "Director Content Partnerships",
    # Primary ICP #3: Distribution
    "EVP Global Distribution",
    "SVP Global Licensing",
    "Head of International Sales",
    "VP International Distribution",
    "Head of Global Licensing",
    # Secondary ICP #4: Strategy
    "Head of International Strategy",
    "VP Content Strategy",
    # Secondary ICP #5: AVOD Programming
    "Head of Programming",
    "VP Programming",
]

DEFAULT_SENIORITY = ["c_suite", "vp", "director", "head", "owner", "founder"]

ACTOR_ID = "code_crafter/leads-finder"


def ensure_tmp_dir():
    """Ensure .tmp directory exists."""
    tmp_dir = Path(__file__).parent.parent / ".tmp"
    tmp_dir.mkdir(exist_ok=True)
    return tmp_dir


def scrape_leads(
    company_domain: Optional[str] = None,
    location: str = "United States",
    job_titles: Optional[List[str]] = None,
    seniority_levels: Optional[List[str]] = None,
    fetch_count: int = 50,
    email_status: str = "validated"
) -> List[Dict]:
    """
    Scrape leads using Apify leads-finder actor.
    
    Args:
        company_domain: Target company domain (e.g., "bbcstudios.com")
        location: Target location/region (e.g., "United Kingdom", "United States")
        job_titles: List of job titles to filter for
        seniority_levels: List of seniority levels (C-Level, VP, etc.)
        fetch_count: Maximum number of leads to fetch
        email_status: Email validation status ("validated", "unknown", "not_validated")
    
    Returns:
        List of lead dictionaries from Apify
    """
    api_token = os.getenv("APIFY_TOKEN")
    if not api_token:
        print("Error: APIFY_TOKEN environment variable not set")
        sys.exit(1)
    
    client = ApifyClient(api_token)
    
    # Build input for the actor
    actor_input = {
        "fetch_count": fetch_count,
        "email_status": [email_status],
    }
    
    # Add location filter
    if location:
        actor_input["contact_location"] = [location]
    
    # Add job title filter
    titles = job_titles or DEFAULT_JOB_TITLES
    if titles:
        actor_input["contact_job_title"] = titles
    
    # Add seniority filter
    seniority = seniority_levels or DEFAULT_SENIORITY
    if seniority:
        actor_input["seniority_level"] = seniority
    
    # Add company domain filter if specified
    if company_domain:
        actor_input["company_domain"] = [company_domain]
    
    print(f"\n{'='*60}")
    print(f"Apify Lead Scraper - {ACTOR_ID}")
    print(f"{'='*60}")
    print(f"Location: {location}")
    print(f"Company Domain: {company_domain or 'Any'}")
    print(f"Job Titles: {len(titles)} roles")
    print(f"Seniority: {seniority}")
    print(f"Fetch Count: {fetch_count}")
    print(f"Email Status: {email_status}")
    print(f"{'='*60}\n")
    
    print("Starting Apify actor run...")
    
    try:
        # Run the actor and wait for it to finish
        run = client.actor(ACTOR_ID).call(run_input=actor_input)
        
        # Fetch results from the dataset
        results = []
        dataset_id = run["defaultDatasetId"]
        
        for item in client.dataset(dataset_id).iterate_items():
            results.append(item)
        
        print(f"✓ Scraped {len(results)} leads")
        return results
        
    except Exception as e:
        print(f"✗ Error running Apify actor: {e}")
        raise


def save_to_json(leads: List[Dict], test_mode: bool = False) -> Path:
    """Save leads to JSON file in .tmp directory."""
    tmp_dir = ensure_tmp_dir()
    
    if test_mode:
        filename = "test_leads.json"
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"leads_{timestamp}.json"
    
    filepath = tmp_dir / filename
    
    with open(filepath, 'w') as f:
        json.dump(leads, f, indent=2, default=str)
    
    print(f"✓ Saved to {filepath}")
    return filepath


def insert_to_database(leads: List[Dict], company_id: Optional[str] = None, market: str = "usa"):
    """Insert leads into Neon Postgres database."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("⚠ DATABASE_URL not set, skipping database insertion")
        return 0
    
    try:
        from db.connection import get_db_session
        from db.models import Lead, ScrapeRun, Company
        
        session = get_db_session()
        inserted_count = 0
        
        # Create scrape run record
        scrape_run = ScrapeRun(
            company_id=company_id,
            actor_id=ACTOR_ID,
            status="running",
            created_at=datetime.utcnow()
        )
        session.add(scrape_run)
        session.flush()  # Get the ID
        
        for lead_data in leads:
            # Check for duplicate by LinkedIn URL or email
            linkedin_url = lead_data.get("linkedin")
            email = lead_data.get("email")
            
            if linkedin_url:
                existing = session.query(Lead).filter_by(linkedin_url=linkedin_url).first()
                if existing:
                    continue
            
            # Try to match company by domain
            matched_company_id = company_id
            if not matched_company_id and lead_data.get("company_domain"):
                company = session.query(Company).filter(
                    Company.linkedin_url.ilike(f"%{lead_data.get('company_name', '')}%")
                ).first()
                if company:
                    matched_company_id = company.id
            
            # Create lead record
            lead = Lead(
                name=lead_data.get("full_name") or f"{lead_data.get('first_name', '')} {lead_data.get('last_name', '')}".strip(),
                title=lead_data.get("job_title") or lead_data.get("headline"),
                linkedin_url=linkedin_url,
                email=email,
                market=market,
                company_id=matched_company_id,
                priority_score=calculate_priority_score(lead_data),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            session.add(lead)
            inserted_count += 1
        
        # Update scrape run
        scrape_run.leads_found = inserted_count
        scrape_run.status = "completed"
        scrape_run.completed_at = datetime.utcnow()
        
        session.commit()
        session.close()
        
        print(f"✓ Inserted {inserted_count} leads into database")
        return inserted_count
        
    except Exception as e:
        print(f"✗ Database error: {e}")
        return 0


def calculate_priority_score(lead_data: Dict) -> int:
    """
    Calculate priority score (1-100) based on ICP criteria.
    
    Scoring:
    - Base score: 40
    - ICP Category: +15 to +30
    - Seniority: +10 to +15
    - Email available: +15
    """
    score = 40  # Base score
    
    title = (lead_data.get("job_title") or "").lower()
    seniority = (lead_data.get("seniority_level") or "").lower()
    
    # ICP Category scoring
    if any(kw in title for kw in ["acquisition", "acquisitions"]):
        score += 30  # Primary ICP #1
    elif any(kw in title for kw in ["distribution", "licensing", "sales"]):
        score += 25  # Primary ICP #3
    elif any(kw in title for kw in ["partnership", "content"]):
        score += 25  # Primary ICP #2
    elif any(kw in title for kw in ["programming", "strategy"]):
        score += 15  # Secondary ICPs
    
    # Seniority scoring
    if any(kw in seniority for kw in ["c-level", "chief", "evp", "svp"]):
        score += 15
    elif any(kw in seniority for kw in ["vp", "director", "head"]):
        score += 10
    elif any(kw in title for kw in ["head of", "evp", "svp", "chief"]):
        score += 15
    elif any(kw in title for kw in ["vp ", "director"]):
        score += 10
    
    # Email available bonus
    if lead_data.get("email"):
        score += 15
    
    return min(score, 100)  # Cap at 100


def main():
    parser = argparse.ArgumentParser(description="Scrape leads using Apify leads-finder actor")
    
    parser.add_argument("--company_domain", type=str, help="Target company domain (e.g., bbcstudios.com)")
    parser.add_argument("--location", type=str, default="United States", help="Target location/region")
    parser.add_argument("--fetch_count", type=int, default=50, help="Max leads to fetch")
    parser.add_argument("--test", action="store_true", help="Test mode: fetch only 25 leads")
    parser.add_argument("--market", type=str, default="usa", help="Market code for database (uk/usa/spain/etc)")
    parser.add_argument("--no-db", action="store_true", help="Skip database insertion")
    
    args = parser.parse_args()
    
    # Test mode overrides
    if args.test:
        args.fetch_count = 25
        print("\n🧪 TEST MODE: Fetching 25 leads only\n")
    
    # Run the scrape
    leads = scrape_leads(
        company_domain=args.company_domain,
        location=args.location,
        fetch_count=args.fetch_count
    )
    
    if not leads:
        print("\n⚠ No leads found. Try broadening your filters.")
        sys.exit(0)
    
    # Save to JSON
    json_path = save_to_json(leads, test_mode=args.test)
    
    # Insert to database (unless --no-db)
    if not args.no_db:
        insert_to_database(leads, market=args.market)
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    print(f"Total leads scraped: {len(leads)}")
    print(f"Leads with email: {sum(1 for l in leads if l.get('email'))}")
    print(f"Output file: {json_path}")
    print(f"{'='*60}\n")
    
    # Show sample leads
    print("Sample leads (first 5):")
    for lead in leads[:5]:
        name = lead.get("full_name") or f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip()
        title = lead.get("job_title", "")
        company = lead.get("company_name", "")
        email = lead.get("email", "No email")
        print(f"  • {name} - {title} @ {company}")
        print(f"    Email: {email}")


if __name__ == "__main__":
    main()
