import os

class Settings:
    """Application configuration settings."""
    
    # Server Configuration
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database Configuration
    # Defaults to SQLite if not provided
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cricket_optimizer.db")
    
    # Cache Configuration
    # Defaults to True, can be disabled for testing/debugging
    CACHE_ENABLED: bool = os.getenv("CACHE_ENABLED", "True").lower() in ("true", "1", "t")

settings = Settings()
