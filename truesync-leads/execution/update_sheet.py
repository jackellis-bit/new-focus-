#!/usr/bin/env python3
"""
Google Sheets Updater
=====================

Exports leads and accounts from database or JSON to Google Sheets.
This is the DELIVERABLE - the actual output the user receives.

Usage:
    # Export from database to default sheet
    python execution/update_sheet.py
    
    # Export from JSON file
    python execution/update_sheet.py --json .tmp/leads_20260115_120000.json
    
    # Update specific worksheet tab
    python execution/update_sheet.py --worksheet "Exec Summary"
    
    # Export accounts data
    python execution/update_sheet.py --accounts
    
    # Export leads data
    python execution/update_sheet.py --leads

Environment Variables:
    DATABASE_URL - For database queries
    GOOGLE_APPLICATION_CREDENTIALS - Path to service account JSON
    GOOGLE_SHEET_ID - Default spreadsheet ID (from URL)

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

# Default Google Sheet ID (from GOOGLE_SHEET_ID env var or hardcoded fallback)
DEFAULT_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "1jJ4UQaTuPlJh6m1iDVGep09juryjQqX1kLm9BqIeSXU")


def get_default_sheet_url() -> str:
    """Get the default Google Sheet URL."""
    return f"https://docs.google.com/spreadsheets/d/{DEFAULT_SHEET_ID}/edit"


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


def load_accounts_from_database() -> List[Dict]:
    """Load accounts/companies from the database with aggregated data."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("Error: DATABASE_URL not set")
        sys.exit(1)
    
    try:
        from db.connection import get_db_session
        from db.models import Company, Lead
        from sqlalchemy import func
        
        session = get_db_session()
        
        # Get companies with lead counts
        results = session.query(
            Company,
            func.count(Lead.id).label('contact_count')
        ).outerjoin(Lead).group_by(Company.id).all()
        
        accounts = []
        for company, contact_count in results:
            account = company.to_dict() if hasattr(company, 'to_dict') else {
                'name': company.name,
                'type': company.type,
                'market': company.market,
                'catalog_size': getattr(company, 'catalog_size', ''),
                'catalog_notes': getattr(company, 'catalog_notes', ''),
            }
            account['contact_count'] = contact_count
            accounts.append(account)
        
        session.close()
        return accounts
        
    except Exception as e:
        print(f"Error loading accounts from database: {e}")
        return []


def format_accounts_for_sheet(accounts: List[Dict]) -> List[List]:
    """
    Format accounts for Google Sheets (Exec Summary tab).
    Combines account info with show details.
    """
    headers = [
        "Account",
        "Region",
        "Company Type",
        "No. of Titles",
        "No. of Contacts",
        "Catalog Notes",
        "Top Shows",
        "Priority Tier",
    ]
    
    rows = [headers]
    
    for account in accounts:
        # Determine priority tier based on market
        market = (account.get('market') or '').lower()
        if market in ['uk', 'usa', 'spain']:
            tier = 'Tier 1'
        elif market in ['germany', 'france', 'korea']:
            tier = 'Tier 2'
        else:
            tier = 'Tier 3'
        
        # Parse catalog size for title count
        catalog_size = account.get('catalog_size', '')
        title_count = catalog_size if catalog_size else 'Unknown'
        
        row = [
            account.get('name', ''),
            account.get('market', '').upper(),
            account.get('type', ''),
            title_count,
            account.get('contact_count', 0),
            account.get('catalog_notes', ''),
            account.get('top_shows', ''),
            tier,
        ]
        rows.append(row)
    
    return rows


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


def get_gspread_client():
    """Get authenticated gspread client."""
    try:
        import gspread
        from google.oauth2.service_account import Credentials
    except ImportError:
        print("Warning: gspread not installed.")
        print("Install with: pip install gspread google-auth")
        return None
    
    # Get credentials
    creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path or not Path(creds_path).exists():
        # Try default locations
        for default_path in ["credentials.json", "service_account.json"]:
            if Path(default_path).exists():
                creds_path = default_path
                break
    
    if not creds_path or not Path(creds_path).exists():
        print("Warning: Google credentials not found.")
        return None
    
    try:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        creds = Credentials.from_service_account_file(creds_path, scopes=scopes)
        return gspread.authorize(creds)
    except Exception as e:
        print(f"Error authenticating: {e}")
        return None


def update_worksheet(
    data: List[List],
    worksheet_name: str,
    sheet_url: Optional[str] = None,
    sheet_id: Optional[str] = None
) -> str:
    """
    Update a specific worksheet tab in a Google Sheet.
    
    Args:
        data: 2D array of data (first row = headers)
        worksheet_name: Name of the worksheet tab to update
        sheet_url: Full Google Sheet URL (optional)
        sheet_id: Google Sheet ID (optional, uses default if not provided)
    
    Returns:
        Google Sheet URL
    """
    gc = get_gspread_client()
    if not gc:
        print("Falling back to CSV export.")
        return ""
    
    try:
        # Open the spreadsheet
        if sheet_url:
            sh = gc.open_by_url(sheet_url)
        else:
            sid = sheet_id or DEFAULT_SHEET_ID
            sh = gc.open_by_key(sid)
        
        # Get or create the worksheet
        try:
            worksheet = sh.worksheet(worksheet_name)
        except Exception:
            # Create worksheet if it doesn't exist
            worksheet = sh.add_worksheet(title=worksheet_name, rows=1000, cols=20)
        
        # Clear and update
        worksheet.clear()
        worksheet.update('A1', data, value_input_option='USER_ENTERED')
        
        print(f"✓ Updated worksheet '{worksheet_name}' in {sh.url}")
        return sh.url
        
    except Exception as e:
        print(f"Error updating worksheet: {e}")
        return ""


def export_to_google_sheets(leads: List[Dict], sheet_url: Optional[str] = None, worksheet_name: str = "Leads") -> str:
    """
    Export leads to Google Sheets.
    
    Returns the Google Sheet URL (DELIVERABLE).
    """
    gc = get_gspread_client()
    if not gc:
        print("Falling back to CSV export.")
        csv_path = export_to_csv(leads)
        return str(csv_path)
    
    # Format data
    rows = format_leads_for_sheet(leads)
    
    try:
        if sheet_url:
            # Update existing sheet
            result_url = update_worksheet(rows, worksheet_name, sheet_url=sheet_url)
            if result_url:
                return result_url
        else:
            # Use default sheet
            result_url = update_worksheet(rows, worksheet_name)
            if result_url:
                return result_url
        
        # Fallback to creating new sheet
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        title = f"TrueSync Leads - {timestamp}"
        sh = gc.create(title)
        worksheet = sh.sheet1
        worksheet.update('A1', rows, value_input_option='USER_ENTERED')
        
        # Make it accessible
        sh.share(None, perm_type='anyone', role='reader')
        
        print(f"✓ Created new sheet: {sh.url}")
        return sh.url
            
    except Exception as e:
        print(f"Error with Google Sheets: {e}")
        print("Falling back to CSV export.")
        csv_path = export_to_csv(leads)
        return str(csv_path)


def export_accounts_to_google_sheets(accounts: List[Dict], worksheet_name: str = "Exec Summary") -> str:
    """
    Export accounts to Google Sheets (Exec Summary tab).
    
    Returns the Google Sheet URL (DELIVERABLE).
    """
    rows = format_accounts_for_sheet(accounts)
    result_url = update_worksheet(rows, worksheet_name)
    
    if not result_url:
        # Fallback to CSV
        import csv
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path(__file__).parent.parent / "output"
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / f"accounts_export_{timestamp}.csv"
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(rows)
        
        print(f"✓ Exported {len(accounts)} accounts to {output_path}")
        return str(output_path)
    
    return result_url


def main():
    parser = argparse.ArgumentParser(description="Export leads and accounts to Google Sheets")
    
    parser.add_argument("--json", type=str, help="Path to JSON file with leads")
    parser.add_argument("--market", type=str, help="Filter by market (uk/usa/spain/etc)")
    parser.add_argument("--limit", type=int, default=1000, help="Max leads to export")
    parser.add_argument("--sheet_url", type=str, help="Existing Google Sheet URL to update")
    parser.add_argument("--worksheet", type=str, default="Leads", help="Worksheet tab name")
    parser.add_argument("--csv", action="store_true", help="Force CSV output instead of Google Sheets")
    parser.add_argument("--accounts", action="store_true", help="Export accounts to Exec Summary tab")
    parser.add_argument("--leads", action="store_true", help="Export leads to Leads tab")
    parser.add_argument("--all", action="store_true", help="Export both accounts and leads")
    
    args = parser.parse_args()
    
    print(f"Default Sheet: {get_default_sheet_url()}")
    print()
    
    # Export accounts if requested
    if args.accounts or args.all:
        print("Loading accounts from database...")
        accounts = load_accounts_from_database()
        
        if accounts:
            print(f"Found {len(accounts)} accounts")
            if args.csv:
                rows = format_accounts_for_sheet(accounts)
                import csv
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = Path(__file__).parent.parent / "output"
                output_dir.mkdir(exist_ok=True)
                output_path = output_dir / f"accounts_export_{timestamp}.csv"
                with open(output_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(rows)
                print(f"✓ DELIVERABLE (Accounts): {output_path}")
            else:
                sheet_url = export_accounts_to_google_sheets(accounts)
                print(f"✓ DELIVERABLE (Accounts): {sheet_url}")
        else:
            print("No accounts found to export.")
        print()
    
    # Export leads if requested (or if no specific export requested)
    if args.leads or args.all or (not args.accounts and not args.all):
        # Load leads
        if args.json:
            print(f"Loading leads from {args.json}...")
            leads = load_leads_from_json(args.json)
        else:
            print("Loading leads from database...")
            leads = load_leads_from_database(market=args.market, limit=args.limit)
        
        if not leads:
            print("No leads found to export.")
            if not args.accounts and not args.all:
                sys.exit(0)
        else:
            print(f"Found {len(leads)} leads")
            
            # Export
            if args.csv:
                output_path = export_to_csv(leads)
                print(f"\n✓ DELIVERABLE (Leads): {output_path}")
            else:
                sheet_url = export_to_google_sheets(
                    leads, 
                    sheet_url=args.sheet_url,
                    worksheet_name=args.worksheet
                )
                print(f"\n✓ DELIVERABLE (Leads): {sheet_url}")


if __name__ == "__main__":
    main()
