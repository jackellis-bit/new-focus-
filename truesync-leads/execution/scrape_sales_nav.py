#!/usr/bin/env python3
"""
Scrape LinkedIn Sales Navigator search results using Apify.
Uses the anchor/linkedin-sales-navigator-scraper actor.
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
from apify_client import ApifyClient

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

load_dotenv()


def scrape_sales_nav_search(
    search_url: str,
    max_leads: int = 100,
    output_file: str = None
) -> list:
    """
    Scrape leads from a LinkedIn Sales Navigator search URL.
    
    Args:
        search_url: The full Sales Navigator search URL
        max_leads: Maximum number of leads to scrape
        output_file: Optional path to save results
        
    Returns:
        List of lead dictionaries
    """
    token = os.getenv('APIFY_TOKEN')
    if not token:
        raise ValueError("APIFY_TOKEN not found in environment")
    
    client = ApifyClient(token)
    
    # Actor: anchor/linkedin-sales-navigator-scraper
    # This actor scrapes Sales Navigator search results
    actor_id = "anchor/linkedin-sales-navigator-scraper"
    
    print(f"Starting Sales Navigator scrape...")
    print(f"Search URL: {search_url[:100]}...")
    print(f"Max leads: {max_leads}")
    
    # Run the actor
    run_input = {
        "searchUrl": search_url,
        "maxLeads": max_leads,
        "proxy": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"]
        }
    }
    
    try:
        run = client.actor(actor_id).call(run_input=run_input)
    except Exception as e:
        print(f"Error calling actor: {e}")
        print("\nAlternative: Try 'code_crafter/leads-finder' or manual CSV export")
        return []
    
    # Fetch results
    leads = []
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        lead = {
            "name": item.get("fullName", item.get("name", "")),
            "title": item.get("title", item.get("jobTitle", "")),
            "company": item.get("company", item.get("companyName", "")),
            "linkedin_url": item.get("linkedinUrl", item.get("profileUrl", "")),
            "location": item.get("location", ""),
            "email": item.get("email", ""),
        }
        leads.append(lead)
    
    print(f"\nScraped {len(leads)} leads")
    
    # Save to file if requested
    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(leads, f, indent=2)
        print(f"Saved to: {output_path}")
    
    return leads


def main():
    parser = argparse.ArgumentParser(description="Scrape LinkedIn Sales Navigator search")
    parser.add_argument("--url", required=True, help="Sales Navigator search URL")
    parser.add_argument("--max_leads", type=int, default=100, help="Max leads to scrape")
    parser.add_argument("--output", default=".tmp/sales_nav_leads.json", help="Output file path")
    
    args = parser.parse_args()
    
    leads = scrape_sales_nav_search(
        search_url=args.url,
        max_leads=args.max_leads,
        output_file=args.output
    )
    
    if leads:
        print(f"\n=== Sample Leads ===")
        for lead in leads[:5]:
            print(f"  - {lead['name']} | {lead['title']} @ {lead['company']}")


if __name__ == "__main__":
    main()
