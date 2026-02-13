"""
Database connection and models using SQLAlchemy
"""
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
from typing import Optional
import os

# SQLAlchemy base
Base = declarative_base()


class Player(Base):
    """Player model for database"""
    __tablename__ = 'players'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    runs = Column(Integer, nullable=False)
    wickets = Column(Integer, nullable=False)
    strike_rate = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    role = Column(String(10), nullable=False)
    
    def __repr__(self):
        return f"<Player(name='{self.name}', role='{self.role}', price={self.price})>"


# Database configuration
def get_database_url() -> str:
    """
    Get database URL from environment variables with sensible defaults.
    
    Environment variables:
        DATABASE_URL: Full database URL (preferred)
        DB_HOST: Database host (default: localhost)
        DB_PORT: Database port (default: 5432)
        DB_NAME: Database name (default: cricket_optimizer)
        DB_USER: Database user (default: postgres)
        DB_PASSWORD: Database password (default: postgres)
    
    Returns:
        Database connection URL
    """
    # Check for full DATABASE_URL first
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url
    
    # Build from individual components
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "cricket_optimizer")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "postgres")
    
    return f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


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
        database_url = get_database_url()
        
        # Create engine with connection pooling
        _engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=5,
            max_overflow=10,
            echo=False  # Set to True for SQL logging
        )
        
        # Test connection
        with _engine.connect() as conn:
            conn.execute("SELECT 1")
        
        # Create tables if they don't exist
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
