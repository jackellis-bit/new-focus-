#!/usr/bin/env python3
"""
TrueSync Lead Generation System
===============================

Main orchestration script for lead discovery, enrichment, and scoring.

Usage:
    python main.py --market spain     # Run for Spain only
    python main.py --market all       # Run for all markets
    python main.py --export           # Export current DB to Excel
    python main.py --seed             # Seed companies only
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from db.connection import get_engine, init_db
from db.models import Company, Lead
from scrapers.apify import ApifyClient
from scrapers.catalog import TMDbClient
from enrichers.email import EmailEnricher
from enrichers.context import CatalogContextEnricher
from scoring import LeadScorer
from output import ExcelExporter


def seed_companies(session):
    """Seed the companies table with target companies."""
    from data.companies import COMPANIES
    
    print("Seeding companies...")
    for company_data in COMPANIES:
        existing = session.query(Company).filter_by(name=company_data['name']).first()
        if not existing:
            company = Company(**company_data)
            session.add(company)
            print(f"  Added: {company_data['name']}")
        else:
            print(f"  Exists: {company_data['name']}")
    
    session.commit()
    print(f"Companies seeded: {session.query(Company).count()} total")


def discover_leads(session, market: str = None):
    """Run lead discovery for specified market(s)."""
    apify = ApifyClient()
    catalog_enricher = CatalogContextEnricher()
    
    query = session.query(Company)
    
    # Handle tier-based and individual market filtering
    if market == 'tier1':
        query = query.filter(Company.market.in_(['uk', 'usa', 'spain']))
    elif market == 'tier2':
        query = query.filter(Company.market.in_(['germany', 'france', 'korea']))
    elif market and market != 'all':
        query = query.filter_by(market=market)
    
    companies = query.all()
    print(f"\nDiscovering leads for {len(companies)} companies...")
    
    for company in companies:
        print(f"\n  Processing: {company.name} ({company.market})")
        
        # Check if we've recently scraped this company
        existing_leads = session.query(Lead).filter_by(company_id=company.id).count()
        if existing_leads > 0:
            print(f"    Found {existing_leads} existing leads, skipping discovery")
            continue
        
        # Get catalog context for this company (used for all leads)
        catalog_context = catalog_enricher.get_context_for_lead(
            company.name, company.market
        )
        
        # Discover new leads
        leads = apify.discover_company_employees(
            company_name=company.name,
            company_linkedin_url=company.linkedin_url,
            target_roles=None  # Will use config defaults
        )
        
        for lead_data in leads:
            # Check for duplicates by LinkedIn URL
            existing = session.query(Lead).filter_by(
                linkedin_url=lead_data.get('linkedin_url')
            ).first()
            
            if not existing:
                lead = Lead(
                    linkedin_url=lead_data.get('linkedin_url'),
                    name=lead_data.get('name'),
                    title=lead_data.get('title'),
                    company_id=company.id,
                    market=company.market,
                    catalog_context=catalog_context,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                session.add(lead)
        
        session.commit()
        new_count = session.query(Lead).filter_by(company_id=company.id).count()
        print(f"    Added {new_count} leads")


def enrich_leads(session, market: str = None):
    """Enrich leads with email and catalog context."""
    email_enricher = EmailEnricher()
    catalog_enricher = CatalogContextEnricher()
    
    query = session.query(Lead).filter(Lead.email.is_(None))
    
    # Handle tier-based and individual market filtering
    if market == 'tier1':
        query = query.filter(Lead.market.in_(['uk', 'usa', 'spain']))
    elif market == 'tier2':
        query = query.filter(Lead.market.in_(['germany', 'france', 'korea']))
    elif market and market != 'all':
        query = query.filter_by(market=market)
    
    leads_to_enrich = query.all()
    print(f"\nEnriching {len(leads_to_enrich)} leads...")
    
    for lead in leads_to_enrich:
        print(f"  Enriching: {lead.name}")
        
        # Email enrichment
        email = email_enricher.find_email(
            name=lead.name,
            company=lead.company.name if lead.company else None,
            linkedin_url=lead.linkedin_url
        )
        if email:
            lead.email = email
        
        # Catalog context enrichment
        if lead.company and not lead.catalog_context:
            catalog_context = catalog_enricher.get_context_for_lead(
                lead.company.name, lead.market
            )
            if catalog_context:
                lead.catalog_context = catalog_context
        
        lead.updated_at = datetime.utcnow()
        session.commit()
    
    print("Enrichment complete")


def score_leads(session, market: str = None):
    """Apply scoring algorithm to all leads."""
    scorer = LeadScorer()
    
    query = session.query(Lead)
    
    # Handle tier-based and individual market filtering
    if market == 'tier1':
        query = query.filter(Lead.market.in_(['uk', 'usa', 'spain']))
    elif market == 'tier2':
        query = query.filter(Lead.market.in_(['germany', 'france', 'korea']))
    elif market and market != 'all':
        query = query.filter_by(market=market)
    
    leads = query.all()
    print(f"\nScoring {len(leads)} leads...")
    
    for lead in leads:
        score = scorer.calculate_score(lead)
        lead.priority_score = score
        lead.updated_at = datetime.utcnow()
    
    session.commit()
    print("Scoring complete")


def export_to_excel(session):
    """Export all leads from DB to Excel."""
    exporter = ExcelExporter()
    
    leads = session.query(Lead).order_by(Lead.priority_score.desc()).all()
    companies = session.query(Company).all()
    
    print(f"\nExporting {len(leads)} leads to Excel...")
    
    filepath = exporter.export(leads, companies)
    print(f"Exported to: {filepath}")
    
    return filepath


def main():
    parser = argparse.ArgumentParser(description='TrueSync Lead Generation System')
    parser.add_argument('--market', choices=['uk', 'usa', 'spain', 'germany', 'france', 'korea', 'tier1', 'tier2', 'all'],
                        default='all', help='Target market(s) - tier1=UK,USA,Spain; tier2=Germany,France,Korea')
    parser.add_argument('--seed', action='store_true', help='Seed companies only')
    parser.add_argument('--discover', action='store_true', help='Run lead discovery')
    parser.add_argument('--enrich', action='store_true', help='Run enrichment')
    parser.add_argument('--score', action='store_true', help='Run scoring')
    parser.add_argument('--export', action='store_true', help='Export to Excel')
    parser.add_argument('--full', action='store_true', help='Run full pipeline')
    
    args = parser.parse_args()
    
    # Initialize database
    print("Initializing database connection...")
    engine = get_engine()
    init_db(engine)
    
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        if args.seed or args.full:
            seed_companies(session)
        
        if args.discover or args.full:
            discover_leads(session, args.market)
        
        if args.enrich or args.full:
            enrich_leads(session, args.market)
        
        if args.score or args.full:
            score_leads(session, args.market)
        
        if args.export or args.full:
            export_to_excel(session)
        
        if not any([args.seed, args.discover, args.enrich, args.score, args.export, args.full]):
            print("No action specified. Use --help to see options.")
            print("\nQuick start:")
            print("  python main.py --full --market spain")
            
    finally:
        session.close()
    
    print("\nDone!")


if __name__ == '__main__':
    main()
