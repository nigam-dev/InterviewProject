from typing import Optional
import pandas as pd
from repositories.player_repository import load_players
from services.scoring import calculate_score
from core.logger import get_logger

logger = get_logger(__name__)

# Global cache for scored players
_cached_players_df: Optional[pd.DataFrame] = None

def get_scored_players(force_refresh: bool = False) -> pd.DataFrame:
    """
    Get players DataFrame with calculated scores.
    Uses in-memory caching to avoid reloading/recalculating on every request.
    
    Args:
        force_refresh: If True, reload from repository even if cached
    
    Returns:
        DataFrame with player data and 'score' column
    """
    global _cached_players_df
    
    if _cached_players_df is None or force_refresh:
        logger.info("Loading and scoring players data...")
        # Load raw data
        df = load_players()
        # Calculate scores
        _cached_players_df = calculate_score(df)
        logger.info(f"✓ Cached {_cached_players_df.shape[0]} scored players")
        
    return _cached_players_df
