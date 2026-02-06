"""
VFX Leads Database Models
==========================

SQLAlchemy ORM models for VFX lead data.
"""

from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Boolean,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class VFXCompany(Base):
    __tablename__ = 'vfx_companies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    parent_company = Column(String(255))
    market = Column(String(50))
    location = Column(String(255))
    notable_projects = Column(Text)
    
    # Deal qualification
    has_economic_buyer = Column(Boolean, default=False)
    has_technical_champion = Column(Boolean, default=False)
    has_day_to_day_user = Column(Boolean, default=False)
    deal_qualified = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    leads = relationship('VFXLead', back_populates='company_rel')


class VFXLead(Base):
    __tablename__ = 'vfx_leads'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    title = Column(String(255))
    company = Column(String(255))
    company_id = Column(Integer, ForeignKey('vfx_companies.id'))
    linkedin_url = Column(String(500))
    email = Column(String(255))
    location = Column(String(255))
    market = Column(String(50))
    
    # Classification
    persona_tier = Column(String(50))  # economic_buyer, technical_champion, etc.
    score = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    company_rel = relationship('VFXCompany', back_populates='leads')
    
    __table_args__ = (
        UniqueConstraint('name', 'company', name='uq_vfx_lead_name_company'),
    )
