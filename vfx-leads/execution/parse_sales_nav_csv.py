#!/usr/bin/env python3
"""
Parse LinkedIn Sales Navigator CSV exports for VFX leads.

Handles the messy Sales Navigator export format and extracts:
- Name
- Title
- Company
- Location
- LinkedIn URL (if present in export)

Supports multiple CSV files (one per persona tier search).

Usage:
  # Single CSV
  python parse_sales_nav_csv.py "/path/to/export.csv"

  # Multiple CSVs (one per tier search)
  python parse_sales_nav_csv.py tier1_eb.csv tier2_tc.csv tier3_users.csv tier4_proc.csv

  # Append to existing JSON
  python parse_sales_nav_csv.py new_export.csv --append
"""
import re
import json
import csv
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from data.companies import is_target_company, normalize_company_name
from data.roles import classify_title


# VFX-specific title keywords for parsing the messy name block
VFX_TITLE_KEYWORDS = [
    # Economic Buyers
    'managing director', 'executive producer', 'head of post',
    'head of production', 'head of vfx', 'chief operating',
    'operations director', 'head of operations', 'head of innovation',
    'head of technology', 'chief technology', 'chief executive',
    'chief creative', 'president', 'general manager', 'studio director',
    'facility director', 'coo', 'cto', 'ceo',
    
    # Technical Champions
    'vfx supervisor', 'cg supervisor', 'compositing supervisor',
    'head of 2d', 'head of comp', 'pipeline td', 'head of pipeline',
    'pipeline supervisor', 'technical director', 'head of r&d',
    'head of cg', 'head of 3d', 'dfx supervisor', 'lighting supervisor',
    'animation supervisor', 'fx supervisor', 'effects supervisor',
    'look dev', 'asset supervisor',
    
    # Day-to-Day Users
    'senior compositor', 'lead compositor', 'compositor',
    'lead roto', 'lead paint', 'roto/paint', 'prep supervisor',
    'prep lead', 'sequence lead', 'shot lead', 'matchmove',
    'rotoscope', 'paint supervisor', 'cleanup lead', '2d lead',
    
    # Procurement
    'procurement', 'commercial manager', 'vendor',
    'purchasing', 'finance director',
    
    # General VFX keywords
    'supervisor', 'producer', 'director', 'head of', 'lead',
    'senior', 'manager', 'coordinator',
]

# Regex to find LinkedIn profile URLs in CSV data
LINKEDIN_URL_PATTERN = re.compile(r'https?://(?:www\.)?linkedin\.com/in/[A-Za-z0-9\-_%]+/?')


def parse_sales_nav_export(csv_path: str) -> list:
    """
    Parse Sales Navigator export CSV.
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        List of lead dicts
    """
    leads = []
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    for row in rows:
        if len(row) < 3:
            continue
        
        # Skip header rows
        if row[0] in ('NAME', 'Account', 'name'):
            continue
        
        name_block = row[0] if row[0] else ""
        company = row[1] if len(row) > 1 else ""
        location = row[2] if len(row) > 2 else ""
        
        if not name_block.strip():
            continue
        
        name = ""
        title = ""
        linkedin_url = ""
        
        # Check ALL columns for a LinkedIn URL
        full_row_text = ' '.join(str(col) for col in row)
        url_match = LINKEDIN_URL_PATTERN.search(full_row_text)
        if url_match:
            linkedin_url = url_match.group(0).rstrip('/')
        
        lines = name_block.split('\n')
        
        # Also check name block lines for LinkedIn URL
        if not linkedin_url:
            for line in lines:
                url_match = LINKEDIN_URL_PATTERN.search(line)
                if url_match:
                    linkedin_url = url_match.group(0).rstrip('/')
                    break
        
        # Extract name
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line in ['CRM', 'Saved Badge', '1 List']:
                continue
            if 'degree connection' in line.lower():
                continue
            if 'linkedin.com' in line.lower():
                continue
            
            if line.startswith('Select '):
                name = line.replace('Select ', '').strip()
                break
            
            if not name:
                title_indicators = [kw for kw in VFX_TITLE_KEYWORDS if len(kw) > 5]
                if not any(ind in line.lower() for ind in title_indicators):
                    clean_name = re.sub(r'(is online|was last active.*)', '', line, flags=re.IGNORECASE).strip()
                    if clean_name and len(clean_name) > 2:
                        name = clean_name
                        break
        
        # Extract title
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if any(kw in line.lower() for kw in VFX_TITLE_KEYWORDS):
                title = line.strip().rstrip('",')
                break
        
        # Clean up
        if name:
            name = name.split('\n')[0].strip()
            name = re.sub(r'[\u200b]', '', name).strip()
            if len(name) > 4:
                half_len = len(name) // 2
                if name[:half_len] == name[half_len:half_len*2]:
                    name = name[:half_len]
        
        company = company.strip().rstrip('",')
        company = re.sub(r'\(\+\d+\)', '', company).strip()
        location = location.strip().rstrip('",')
        
        if title:
            parts = title.split('",')
            if len(parts) > 1:
                title = parts[0].strip()
        
        if name and len(name) > 2:
            leads.append({
                'name': name,
                'title': title,
                'company': company,
                'location': location,
                'email': '',
                'linkedin_url': linkedin_url,
            })
    
    return leads


def deduplicate_leads(leads: list) -> list:
    """
    Deduplicate leads by (name, company) tuple.
    Keeps the first occurrence (which preserves richer data if present).
    """
    seen = set()
    unique_leads = []
    for lead in leads:
        key = (lead['name'].lower().strip(), lead.get('company', '').lower().strip())
        if key not in seen:
            seen.add(key)
            unique_leads.append(lead)
    return unique_leads


def parse_multiple_csvs(csv_paths: list) -> list:
    """
    Parse multiple Sales Navigator CSVs and merge into a single deduplicated list.
    Useful when running separate searches per persona tier.
    
    Args:
        csv_paths: List of CSV file paths
        
    Returns:
        Deduplicated list of lead dicts
    """
    all_leads = []
    for path in csv_paths:
        print(f"Parsing: {path}")
        leads = parse_sales_nav_export(path)
        print(f"  -> {len(leads)} leads extracted")
        all_leads.extend(leads)
    
    unique = deduplicate_leads(all_leads)
    print(f"\nTotal: {len(all_leads)} raw -> {len(unique)} after dedup")
    return unique


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_sales_nav_csv.py <csv_path> [csv_path2 ...] [--output <json_path>] [--append]")
        print("  Parses one or more LinkedIn Sales Navigator CSV exports into JSON.")
        print("  Use --append to merge into an existing output JSON file.")
        sys.exit(1)
    
    # Separate flags from CSV paths
    csv_paths = []
    output_path = None
    append_mode = False
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--output':
            if i + 1 < len(sys.argv):
                output_path = sys.argv[i + 1]
                i += 2
                continue
        elif arg == '--append':
            append_mode = True
            i += 1
            continue
        else:
            csv_paths.append(arg)
        i += 1
    
    if not csv_paths:
        print("Error: No CSV files provided.")
        sys.exit(1)
    
    if not output_path:
        output_path = str(Path(__file__).parent.parent / ".tmp" / "vfx_leads_raw.json")
    
    # Parse CSV(s)
    if len(csv_paths) == 1:
        print(f"Parsing: {csv_paths[0]}")
        leads = parse_sales_nav_export(csv_paths[0])
        leads = deduplicate_leads(leads)
    else:
        leads = parse_multiple_csvs(csv_paths)
    
    # Append mode: merge with existing JSON
    if append_mode:
        output_file = Path(output_path)
        if output_file.exists():
            with open(output_file, 'r') as f:
                existing = json.load(f)
            print(f"Appending to existing {len(existing)} leads in {output_path}")
            leads = deduplicate_leads(existing + leads)
            print(f"  -> {len(leads)} total after dedup")
    
    # Show results (same display as before)
    print(f"\n{'='*100}")
    print(f"Extracted {len(leads)} leads:")
    print(f"{'='*100}")
    print(f"{'Name':<30} | {'Title':<40} | {'Company':<20} | {'Tier'}")
    print("-" * 100)
    
    for lead in leads:
        name = lead['name'][:28]
        title = lead.get('title', '')[:38]
        company = lead.get('company', '')[:18]
        tier = classify_title(lead.get('title', ''))
        tier_label = {
            'economic_buyer': 'EB',
            'technical_champion': 'TC',
            'day_to_day_user': 'USER',
            'procurement': 'PROC',
            'unclassified': '?',
        }.get(tier, '?')
        print(f"  {name:<28} | {title:<38} | {company:<18} | {tier_label}")
    
    # Company filter preview
    target_leads = [l for l in leads if is_target_company(l.get('company', ''))]
    non_target = [l for l in leads if not is_target_company(l.get('company', ''))]
    
    print(f"\n{'='*100}")
    print(f"Target company filter:")
    print(f"  Accepted (target companies): {len(target_leads)}")
    print(f"  Rejected (non-target): {len(non_target)}")
    
    if non_target:
        print(f"\n  Non-target companies that will be rejected:")
        rejected_cos = set(l.get('company', '?') for l in non_target)
        for co in sorted(rejected_cos):
            print(f"    - {co}")
    
    # Summary by company
    print(f"\n{'='*100}")
    print("Summary by Company:")
    print("-" * 50)
    companies = {}
    for lead in leads:
        c = lead.get('company', 'Unknown') or 'Unknown'
        companies[c] = companies.get(c, 0) + 1
    for c, count in sorted(companies.items(), key=lambda x: -x[1]):
        target = "TARGET" if is_target_company(c) else "REJECTED"
        print(f"  [{target}] {c}: {count}")
    
    # Tier summary
    print(f"\nPersona Tier Breakdown:")
    print("-" * 50)
    tiers = {}
    for lead in leads:
        tier = classify_title(lead.get('title', ''))
        tiers[tier] = tiers.get(tier, 0) + 1
    for tier, count in sorted(tiers.items(), key=lambda x: -x[1]):
        label = {
            'economic_buyer': 'Economic Buyer',
            'technical_champion': 'Technical Champion',
            'day_to_day_user': 'Day-to-Day User',
            'procurement': 'Procurement',
            'unclassified': 'Unclassified',
        }.get(tier, tier)
        print(f"  {label}: {count}")
    
    # Save to JSON
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output, 'w') as f:
        json.dump(leads, f, indent=2)
    
    print(f"\nSaved to: {output}")
    return leads


if __name__ == "__main__":
    main()
