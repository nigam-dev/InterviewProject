"""
Database connection and models using SQLAlchemy
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import Optional
import os
from .config import settings

# SQLAlchemy base
Base = declarative_base()


# Database configuration
# Global engine and session
_engine: Optional[object] = None
_SessionLocal: Optional[sessionmaker] = None


def init_database() -> bool:
    """
    Initialize database connection and create tables.
    
    Returns:
        True if successful, False if database is unavailable
    """
    global _engine, _SessionLocal
    
    try:
        database_url = settings.DATABASE_URL
        
        # Configure engine arguments based on database type
        connect_args = {}
        engine_args = {
            "pool_pre_ping": True,
            "echo": False
        }
        
        if database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        else:
            # PostgreSQL/others support pooling options
            engine_args["pool_size"] = 5
            engine_args["max_overflow"] = 10
            
        # Create engine with connection pooling
        _engine = create_engine(
            database_url,
            connect_args=connect_args,
            **engine_args
        )
        
        # Test connection (using text() for SQLAlchemy 2.0 compatibility)
        from sqlalchemy import text
        with _engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Create tables if they don't exist
        # Import models so they are registered with Base
        import models.db  # noqa
        Base.metadata.create_all(bind=_engine)
        
        # Create session factory
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        
        return True
        
    except Exception as e:
        print(f"Database initialization failed: {e}")
        print("Will fall back to CSV data source")
        _engine = None
        _SessionLocal = None
        return False


def get_session():
    """
    Get database session.
    
    Yields:
        SQLAlchemy session
    
    Raises:
        RuntimeError: If database is not initialized
    """
    if _SessionLocal is None:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    session = _SessionLocal()
    try:
        yield session
    finally:
        session.close()


def is_database_available() -> bool:
    """
    Check if database is available and initialized.
    
    Returns:
        True if database is available, False otherwise
    """
    return _engine is not None and _SessionLocal is not None


def close_database():
    """Close database connections"""
    global _engine, _SessionLocal
    
    if _engine is not None:
        _engine.dispose()
        _engine = None
        _SessionLocal = None
