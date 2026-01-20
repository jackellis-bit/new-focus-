"""
Database Models
===============

SQLAlchemy models for the TrueSync lead generation system.
Connected to Neon Postgres (PostgreSQL 17.7).

Tables:
    - companies: 30 target companies across 6 markets
    - leads: 506 leads with catalog context and scoring
    - accounts: Enriched company data with title counts and contact counts
    - enrichment_history: Track enrichment attempts
    - scrape_runs: Track scraping sessions

Lead.to_dict() output matches sample sheet columns:
    Name, Title, Company, Company Type, LinkedIn URL, Email,
    Market, Priority Score, Catalog Context, Created, Updated
    
Account.to_dict() output matches accounts pipeline schema:
    Accounts, Region, No. of titles, Type of company, No. of contacts
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Text, Integer, DateTime, ForeignKey, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


def generate_uuid():
    """Generate a new UUID."""
    return str(uuid.uuid4())


class Company(Base):
    """
    Target companies for lead generation.
    
    Stores information about studios, distributors, and platforms
    across Spain, Korea, and France markets.
    """
    __tablename__ = 'companies'
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, unique=True)
    type = Column(String(50), nullable=False)  # Producer/Distributor/Platform
    market = Column(String(50), nullable=False)  # spain/korea/france
    linkedin_url = Column(Text)
    catalog_size = Column(Text)
    catalog_notes = Column(Text)  # Additional context about their catalog
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    leads = relationship('Lead', back_populates='company')
    scrape_runs = relationship('ScrapeRun', back_populates='company')
    
    def __repr__(self):
        return f"<Company(name='{self.name}', market='{self.market}')>"


class Account(Base):
    """
    Enriched company/account data with title counts and contact statistics.
    
    Populated by the accounts_pipeline.py which:
    - Fetches title counts from TMDb (with Google Search fallback)
    - Counts contacts from the leads table
    - Stores top shows and popularity data
    
    Output schema: Accounts, Region, No. of titles, Type of company, No. of contacts
    """
    __tablename__ = 'accounts'
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name = Column(String(255), nullable=False, unique=True)
    region = Column(String(50), nullable=False)  # uk/usa/spain/germany/france/korea
    num_titles = Column(Integer, default=0)  # From TMDb or Google Search
    company_type = Column(String(50), nullable=False)  # Producer/Distributor/Platform/AVOD Platform
    num_contacts = Column(Integer, default=0)  # Count from leads table
    
    # Additional enrichment data
    top_shows = Column(Text)  # Comma-separated top 5 show titles
    tmdb_id = Column(Integer)  # TMDb company ID for reference
    popularity_score = Column(Integer, default=0)  # TMDb aggregate popularity
    data_source = Column(String(50))  # tmdb/google_search/manual
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Account(name='{self.name}', region='{self.region}', num_titles={self.num_titles})>"
    
    def to_dict(self):
        """Convert account to dictionary for export."""
        return {
            'Accounts': self.name,
            'Region': self.region.upper() if self.region else '',
            'No. of titles': self.num_titles,
            'Type of company': self.company_type,
            'No. of contacts': self.num_contacts,
            'Top Shows': self.top_shows,
            'Popularity Score': self.popularity_score,
            'Data Source': self.data_source,
            'Updated': self.updated_at.isoformat() if self.updated_at else None
        }


class Lead(Base):
    """
    Individual leads (people) at target companies.
    
    Each lead represents a potential contact for TrueSync sales.
    """
    __tablename__ = 'leads'
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    linkedin_url = Column(Text, unique=True)  # Primary deduplication key
    name = Column(String(255), nullable=False)
    title = Column(String(255))
    company_id = Column(UUID(as_uuid=False), ForeignKey('companies.id'))
    email = Column(String(255))
    market = Column(String(50))  # spain/korea/france
    priority_score = Column(Integer, default=0)  # 1-100
    
    # Additional profile data
    profile_summary = Column(Text)
    experience_years = Column(Integer)
    catalog_context = Column(Text)  # Show titles, performance data from TMDb
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    company = relationship('Company', back_populates='leads')
    enrichment_history = relationship('EnrichmentHistory', back_populates='lead')
    
    def __repr__(self):
        return f"<Lead(name='{self.name}', title='{self.title}')>"
    
    def to_dict(self):
        """Convert lead to dictionary for export."""
        return {
            'name': self.name,
            'title': self.title,
            'company': self.company.name if self.company else None,
            'company_type': self.company.type if self.company else None,
            'linkedin_url': self.linkedin_url,
            'email': self.email,
            'market': self.market,
            'priority_score': self.priority_score,
            'catalog_context': self.catalog_context,
            'created': self.created_at.isoformat() if self.created_at else None,
            'updated': self.updated_at.isoformat() if self.updated_at else None
        }


class EnrichmentHistory(Base):
    """
    Track enrichment attempts and results.
    
    Stores what data we've collected and from where,
    allowing for incremental enrichment.
    """
    __tablename__ = 'enrichment_history'
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    lead_id = Column(UUID(as_uuid=False), ForeignKey('leads.id'), nullable=False)
    enrichment_type = Column(String(50), nullable=False)  # email/profile/catalog
    source = Column(String(100))  # Apify actor, Hunter, etc.
    data = Column(JSON)  # Raw enrichment data
    success = Column(Integer, default=1)  # 1=success, 0=failed
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    lead = relationship('Lead', back_populates='enrichment_history')
    
    def __repr__(self):
        return f"<EnrichmentHistory(type='{self.enrichment_type}', source='{self.source}')>"


class ScrapeRun(Base):
    """
    Track scraping sessions.
    
    Logs each scraping run for audit and to prevent
    unnecessary re-scraping.
    """
    __tablename__ = 'scrape_runs'
    
    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    company_id = Column(UUID(as_uuid=False), ForeignKey('companies.id'), nullable=False)
    actor_id = Column(String(255))  # Apify actor used
    leads_found = Column(Integer, default=0)
    status = Column(String(50), default='completed')  # pending/running/completed/failed
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    company = relationship('Company', back_populates='scrape_runs')
    
    def __repr__(self):
        return f"<ScrapeRun(company_id='{self.company_id}', leads_found={self.leads_found})>"
