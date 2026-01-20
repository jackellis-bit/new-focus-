#!/usr/bin/env python3
"""
Parse messy LinkedIn Sales Navigator CSV export.
"""
import re
import json
import csv
import sys
from pathlib import Path

def parse_sales_nav_export(csv_path: str) -> list:
    """
    Parse the messy Sales Navigator export format.
    Each row contains: [messy_name_block, company, location, ...]
    Handles multiple formats:
    - "Select Name\nName\nName\n..." (most common)
    - "Name\nThird-degree..." (without Select)
    - "Name\nNameName is online\n..." (with status)
    """
    leads = []
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        rows = list(reader)
    
    for row in rows:
        if len(row) < 3:
            continue
        
        # Skip header rows
        if row[0] == 'NAME' or row[0] == 'Account':
            continue
            
        # First column contains name block with lots of noise
        name_block = row[0] if row[0] else ""
        company = row[1] if len(row) > 1 else ""
        location = row[2] if len(row) > 2 else ""
        
        # Skip if no name block or no company
        if not name_block.strip():
            continue
        
        name = ""
        title = ""
        
        lines = name_block.split('\n')
        
        # Find name - it's usually the first real line (after "Select " if present)
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Skip noise lines
            if line in ['CRM', 'Saved Badge', '1 List']:
                continue
            if 'degree connection' in line.lower():
                continue
            
            # Handle "Select Name" format
            if line.startswith('Select '):
                name = line.replace('Select ', '').strip()
                break
            
            # Handle plain name (first entry format) - must be a real name
            # Names typically: start with capital, have 2+ parts, no special keywords
            if not name and not any(kw in line.lower() for kw in ['degree', 'badge', 'list', 'crm']):
                # Check if this looks like a name (not a title)
                title_indicators = ['head of', 'director', 'vp,', 'vp ', 'svp', 'evp', 
                                   'manager', 'president', 'chief', 'executive', 
                                   'assistant', 'senior', 'junior', 'lead ']
                if not any(ind in line.lower() for ind in title_indicators):
                    # Clean up status suffixes like "Name is online" or "Namewas last active"
                    clean_name = re.sub(r'(.+?)(\1.*(?:is online|was last active|ago).*)?$', r'\1', line, flags=re.IGNORECASE)
                    clean_name = re.sub(r'(is online|was last active.*)', '', clean_name, flags=re.IGNORECASE).strip()
                    if clean_name and len(clean_name) > 2:
                        name = clean_name
                        break
        
        # Find title - look for job title keywords in remaining lines
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            title_keywords = ['head of', 'director', 'vp,', 'vp ', 'svp', 'evp', 
                            'manager', 'president', 'chief', 'executive', 
                            'controller', 'analyst', 'lead ', 'global head',
                            'group head', 'content', 'licensing', 'acquisitions',
                            'programming', 'strategy', 'distribution', 'sales',
                            'marketing', 'legal', 'business affairs', 'finance']
            
            if any(kw in line.lower() for kw in title_keywords):
                title = line.strip().rstrip('",')
                break
        
        # Clean up name
        if name:
            name = name.split('\n')[0].strip()
            name = re.sub(r'[📺🎬🎥\u200b]', '', name).strip()
            # Remove duplicate name patterns like "NameName"
            if len(name) > 4:
                half_len = len(name) // 2
                if name[:half_len] == name[half_len:half_len*2]:
                    name = name[:half_len]
            
        # Clean up company
        company = company.strip().rstrip('",')
        company = re.sub(r'\(\+\d+\)', '', company).strip()
        
        # Clean up location  
        location = location.strip().rstrip('",')
        
        # Clean up title
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
                'linkedin_url': ''
            })
    
    # Deduplicate by name (case-insensitive)
    seen = set()
    unique_leads = []
    for lead in leads:
        name_key = lead['name'].lower().strip()
        if name_key not in seen:
            seen.add(name_key)
            unique_leads.append(lead)
    
    return unique_leads


def main():
    if len(sys.argv) < 2:
        csv_path = "/Users/jack.ellis/Desktop/UK LEads - Sheet1.csv"
    else:
        csv_path = sys.argv[1]
    
    print(f"Parsing: {csv_path}")
    leads = parse_sales_nav_export(csv_path)
    
    print(f"\n{'='*100}")
    print(f"Extracted {len(leads)} leads:")
    print(f"{'='*100}")
    print(f"{'Name':<30} | {'Title':<45} | {'Company':<20}")
    print("-" * 100)
    
    for lead in leads:
        name = lead['name'][:28]
        title = lead.get('title', '')[:43]
        company = lead.get('company', '')[:18]
        print(f"  {name:<28} | {title:<43} | {company}")
    
    # Summary by company
    print(f"\n{'='*100}")
    print("Summary by Company:")
    print("-" * 50)
    companies = {}
    for lead in leads:
        c = lead.get('company', 'Unknown') or 'Unknown'
        companies[c] = companies.get(c, 0) + 1
    for c, count in sorted(companies.items(), key=lambda x: -x[1]):
        print(f"  {c}: {count}")
    
    # Save to JSON
    output_path = Path(__file__).parent.parent / ".tmp" / "uk_leads_raw.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(leads, f, indent=2)
    
    print(f"\n✓ Saved to: {output_path}")
    return leads


if __name__ == "__main__":
    main()
