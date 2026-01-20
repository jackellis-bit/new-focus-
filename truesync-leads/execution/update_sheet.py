#!/usr/bin/env python3
"""
Google Sheets Updater
=====================

Exports leads from database or JSON to Google Sheets.
This is the DELIVERABLE - the actual output the user receives.

Usage:
    # Export from database to new sheet
    python execution/update_sheet.py
    
    # Export from JSON file
    python execution/update_sheet.py --json .tmp/leads_20260115_120000.json
    
    # Update existing sheet
    python execution/update_sheet.py --sheet_url "https://docs.google.com/spreadsheets/d/..."

Environment Variables:
    DATABASE_URL - For database queries
    GOOGLE_APPLICATION_CREDENTIALS - Path to service account JSON

Output:
    Google Sheet URL (DELIVERABLE)
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


def load_leads_from_json(json_path: str) -> List[Dict]:
    """Load leads from a JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def load_leads_from_database(market: Optional[str] = None, limit: int = 1000) -> List[Dict]:
    """Load leads from the database."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not set")
        sys.exit(1)
    
    try:
        from db.connection import get_db_session
        from db.models import Lead
        
        session = get_db_session()
        
        query = session.query(Lead).order_by(Lead.priority_score.desc())
        
        if market:
            query = query.filter_by(market=market)
        
        leads = query.limit(limit).all()
        
        # Convert to dictionaries
        result = [lead.to_dict() for lead in leads]
        
        session.close()
        return result
        
    except Exception as e:
        print(f"Error loading from database: {e}")
        return []


def format_leads_for_sheet(leads: List[Dict]) -> List[List]:
    """
    Format leads for Google Sheets.
    
    Returns a 2D array where first row is headers.
    """
    headers = [
        "Name",
        "Title", 
        "Company",
        "Company Type",
        "LinkedIn URL",
        "Email",
        "Market",
        "Priority Score",
        "Catalog Context",
        "Created",
        "Updated"
    ]
    
    rows = [headers]
    
    for lead in leads:
        # Handle both Apify format and database format
        if "full_name" in lead:
            # Apify format
            row = [
                lead.get("full_name") or f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip(),
                lead.get("job_title") or lead.get("headline", ""),
                lead.get("company_name", ""),
                "",  # Company type not in Apify output
                lead.get("linkedin", ""),
                lead.get("email", ""),
                "",  # Market needs to be set
                "",  # Priority score calculated separately
                "",  # Catalog context from our database
                "",  # Created
                "",  # Updated
            ]
        else:
            # Database format (from Lead.to_dict())
            row = [
                lead.get("name", ""),
                lead.get("title", ""),
                lead.get("company", ""),
                lead.get("company_type", ""),
                lead.get("linkedin_url", ""),
                lead.get("email", ""),
                lead.get("market", ""),
                lead.get("priority_score", ""),
                lead.get("catalog_context", ""),
                lead.get("created", ""),
                lead.get("updated", ""),
            ]
        
        rows.append(row)
    
    return rows


def export_to_csv(leads: List[Dict], output_path: Optional[str] = None) -> Path:
    """
    Export leads to CSV file (fallback if Google Sheets not available).
    """
    import csv
    
    if not output_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"leads_export_{timestamp}.csv"
    else:
        output_path = Path(output_path)
    
    rows = format_leads_for_sheet(leads)
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
    
    print(f"✓ Exported {len(leads)} leads to {output_path}")
    return output_path


def export_to_google_sheets(leads: List[Dict], sheet_url: Optional[str] = None) -> str:
    """
    Export leads to Google Sheets.
    
    Returns the Google Sheet URL (DELIVERABLE).
    """
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("Warning: gspread not installed. Falling back to CSV export.")
        print("Install with: pip install gspread google-auth")
        csv_path = export_to_csv(leads)
        return str(csv_path)
    
    # Get credentials
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path or not Path(creds_path).exists():
        # Try default locations
        for default_path in ["credentials.json", "service_account.json"]:
            if Path(default_path).exists():
                creds_path = default_path
                break
    
    if not creds_path or not Path(creds_path).exists():
        print("Warning: Google credentials not found. Falling back to CSV export.")
        csv_path = export_to_csv(leads)
        return str(csv_path)
    
    try:
        # Authenticate
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        gc = gspread.authorize(creds)
        
        # Format data
        rows = format_leads_for_sheet(leads)
        
        if sheet_url:
            # Update existing sheet
            sh = gc.open_by_url(sheet_url)
            worksheet = sh.sheet1
            worksheet.clear()
            worksheet.update('A1', rows)
            print(f"✓ Updated existing sheet: {sheet_url}")
            return sheet_url
        else:
            # Create new sheet
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
            title = f"TrueSync Leads - {timestamp}"
            sh = gc.create(title)
            worksheet = sh.sheet1
            worksheet.update('A1', rows)
            
            # Make it accessible
            sh.share(None, perm_type='anyone', role='reader')
            
            sheet_url = sh.url
            print(f"✓ Created new sheet: {sheet_url}")
            return sheet_url
            
    except Exception as e:
        print(f"Error with Google Sheets: {e}")
        print("Falling back to CSV export.")
        csv_path = export_to_csv(leads)
        return str(csv_path)


def main():
    parser = argparse.ArgumentParser(description="Export leads to Google Sheets")
    
    parser.add_argument("--json", type=str, help="Path to JSON file with leads")
    parser.add_argument("--market", type=str, help="Filter by market (uk/usa/spain/etc)")
    parser.add_argument("--limit", type=int, default=1000, help="Max leads to export")
    parser.add_argument("--sheet_url", type=str, help="Existing Google Sheet URL to update")
    parser.add_argument("--csv", action="store_true", help="Force CSV output instead of Google Sheets")
    
    args = parser.parse_args()
    
    # Load leads
    if args.json:
        print(f"Loading leads from {args.json}...")
        leads = load_leads_from_json(args.json)
    else:
        print("Loading leads from database...")
        leads = load_leads_from_database(market=args.market, limit=args.limit)
    
    if not leads:
        print("No leads found to export.")
        sys.exit(0)
    
    print(f"Found {len(leads)} leads")
    
    # Export
    if args.csv:
        output_path = export_to_csv(leads)
        print(f"\n✓ DELIVERABLE: {output_path}")
    else:
        sheet_url = export_to_google_sheets(leads, sheet_url=args.sheet_url)
        print(f"\n✓ DELIVERABLE: {sheet_url}")


if __name__ == "__main__":
    main()
