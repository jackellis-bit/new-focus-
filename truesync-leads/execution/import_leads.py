#!/usr/bin/env python3
"""
Import leads from various sources:
- LinkedIn Sales Navigator CSV export
- Manual JSON input
- Copy-pasted text

Then enrich with emails via Apify.
"""
import os
import sys
import json
import csv
import argparse
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent))
load_dotenv()


def parse_csv(csv_path: str) -> list:
    """Parse LinkedIn Sales Navigator CSV export."""
    leads = []
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            lead = {
                "name": row.get("First Name", "") + " " + row.get("Last Name", ""),
                "first_name": row.get("First Name", ""),
                "last_name": row.get("Last Name", ""),
                "title": row.get("Title", row.get("Job Title", "")),
                "company": row.get("Company", row.get("Company Name", "")),
                "linkedin_url": row.get("LinkedIn URL", row.get("Profile URL", "")),
                "location": row.get("Location", row.get("Geography", "")),
                "email": row.get("Email", ""),
            }
            lead["name"] = lead["name"].strip()
            if lead["name"]:
                leads.append(lead)
    return leads


def parse_json(json_path: str) -> list:
    """Parse JSON file with leads."""
    with open(json_path, 'r') as f:
        return json.load(f)


def parse_text(text: str) -> list:
    """
    Parse copy-pasted text from Sales Navigator.
    Expects format like:
    Name | Title | Company
    or
    Name, Title, Company
    """
    leads = []
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Try different delimiters
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
        elif '\t' in line:
            parts = [p.strip() for p in line.split('\t')]
        elif ',' in line:
            parts = [p.strip() for p in line.split(',')]
        else:
            parts = [line]
        
        if len(parts) >= 1:
            lead = {
                "name": parts[0],
                "title": parts[1] if len(parts) > 1 else "",
                "company": parts[2] if len(parts) > 2 else "",
                "linkedin_url": "",
                "email": "",
            }
            leads.append(lead)
    
    return leads


def enrich_with_emails(leads: list) -> list:
    """
    Use Apify code_crafter/leads-finder to find emails.
    """
    from apify_client import ApifyClient
    
    token = os.getenv('APIFY_TOKEN')
    if not token:
        print("Warning: APIFY_TOKEN not found, skipping email enrichment")
        return leads
    
    client = ApifyClient(token)
    enriched = []
    
    for lead in leads:
        if lead.get('email'):
            enriched.append(lead)
            continue
            
        # Try to find email by name + company
        name = lead.get('name', '')
        company = lead.get('company', '')
        
        if not name or not company:
            enriched.append(lead)
            continue
        
        print(f"  Finding email for: {name} @ {company}")
        
        # Use leads-finder with specific person search
        try:
            run = client.actor("code_crafter/leads-finder").call(
                run_input={
                    "contact_name": name,
                    "contact_company": company,
                    "fetch_count": 1,
                },
                timeout_secs=60
            )
            
            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                if item.get('email'):
                    lead['email'] = item['email']
                    print(f"    Found: {lead['email']}")
                    break
        except Exception as e:
            print(f"    Error: {e}")
        
        enriched.append(lead)
    
    return enriched


def save_leads(leads: list, output_path: str):
    """Save leads to JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w') as f:
        json.dump(leads, f, indent=2)
    print(f"\nSaved {len(leads)} leads to: {path}")


def main():
    parser = argparse.ArgumentParser(description="Import leads from various sources")
    parser.add_argument("--csv", help="Path to CSV file from Sales Navigator export")
    parser.add_argument("--json", help="Path to JSON file with leads")
    parser.add_argument("--text", help="Path to text file with copy-pasted leads")
    parser.add_argument("--enrich", action="store_true", help="Enrich leads with emails")
    parser.add_argument("--output", default=".tmp/imported_leads.json", help="Output file path")
    
    args = parser.parse_args()
    
    leads = []
    
    if args.csv:
        print(f"Parsing CSV: {args.csv}")
        leads = parse_csv(args.csv)
    elif args.json:
        print(f"Parsing JSON: {args.json}")
        leads = parse_json(args.json)
    elif args.text:
        print(f"Parsing text file: {args.text}")
        with open(args.text, 'r') as f:
            leads = parse_text(f.read())
    else:
        print("No input file specified. Use --csv, --json, or --text")
        print("\nExample usage:")
        print("  python import_leads.py --csv sales_nav_export.csv --enrich --output leads.json")
        return
    
    print(f"Parsed {len(leads)} leads")
    
    if args.enrich:
        print("\nEnriching with emails...")
        leads = enrich_with_emails(leads)
    
    save_leads(leads, args.output)
    
    # Print summary
    with_email = sum(1 for l in leads if l.get('email'))
    print(f"\nSummary:")
    print(f"  Total leads: {len(leads)}")
    print(f"  With emails: {with_email}")
    
    print(f"\n=== Sample Leads ===")
    for lead in leads[:5]:
        email_str = f" | {lead['email']}" if lead.get('email') else ""
        print(f"  - {lead['name']} | {lead.get('title', 'N/A')} @ {lead.get('company', 'N/A')}{email_str}")


if __name__ == "__main__":
    main()
