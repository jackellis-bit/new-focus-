#!/usr/bin/env python3
"""
Parse LinkedIn Sales Navigator CSV exports for VFX leads.

Handles the messy Sales Navigator export format and extracts:
- Name
- Title
- Company
- Location

Then filters to VFX-relevant titles only.
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
        
        lines = name_block.split('\n')
        
        # Extract name
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line in ['CRM', 'Saved Badge', '1 List']:
                continue
            if 'degree connection' in line.lower():
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
                'linkedin_url': '',
            })
    
    # Deduplicate
    seen = set()
    unique_leads = []
    for lead in leads:
        key = lead['name'].lower().strip()
        if key not in seen:
            seen.add(key)
            unique_leads.append(lead)
    
    return unique_leads


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_sales_nav_csv.py <csv_path> [--output <json_path>]")
        print("  Parses a LinkedIn Sales Navigator CSV export into JSON for the VFX pipeline.")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    
    # Optional output path
    output_path = None
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_path = sys.argv[idx + 1]
    
    if not output_path:
        output_path = str(Path(__file__).parent.parent / ".tmp" / "vfx_leads_raw.json")
    
    print(f"Parsing: {csv_path}")
    leads = parse_sales_nav_export(csv_path)
    
    # Show results
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
