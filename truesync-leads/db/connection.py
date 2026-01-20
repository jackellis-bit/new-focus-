"""
Database Connection Module
==========================

Handles connection to Neon Postgres with connection pooling.

Connection String (from .env.local):
    DATABASE_URL=postgresql://user:pass@host/db?sslmode=require

Usage:
    from db.connection import get_db_session
    session = get_db_session()
    leads = session.query(Lead).all()
    session.close()

Functions:
    - get_engine(): Create SQLAlchemy engine with pooling
    - get_session(engine): Create a new session
    - get_db_session(): Convenience function for quick access
    - init_db(engine): Initialize schema (create tables if needed)
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

from .models import Base


def get_database_url() -> str:
    """Get database URL from environment variable."""
    url = os.getenv('DATABASE_URL')
    if not url:
        raise ValueError(
            "DATABASE_URL environment variable not set. "
            "Set it to your Neon Postgres connection string."
        )
    return url


def get_engine():
    """
    Create and return SQLAlchemy engine with connection pooling.
    
    Neon Postgres uses connection pooling, so we configure
    the engine to work well with it.
    """
    database_url = get_database_url()
    
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,  # Verify connections before use
        echo=False  # Set to True for SQL debugging
    )
    
    return engine


def init_db(engine):
    """
    Initialize database schema.
    
    Creates all tables if they don't exist.
    """
    Base.metadata.create_all(engine)
    print("Database schema initialized.")


def get_session(engine):
    """Create a new database session."""
    Session = sessionmaker(bind=engine)
    return Session()


# Convenience function for quick access
def get_db_session():
    """Get a ready-to-use database session."""
    engine = get_engine()
    init_db(engine)
    return get_session(engine)
