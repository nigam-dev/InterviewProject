"""
Player repository for loading data from database or CSV
"""
import pandas as pd
from typing import Optional
from database import Player, get_session, is_database_available, init_database
from data_loader import load_players as load_players_from_csv
from logger import get_logger

logger = get_logger(__name__)


def sync_csv_to_database(csv_path: str = "players.csv") -> int:
    """
    Sync players from CSV to database.
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        Number of players synced
    
    Raises:
        RuntimeError: If database is not available
    """
    if not is_database_available():
        error_msg = "Database not available. Cannot sync CSV data."
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    
    # Load players from CSV
    logger.info(f"Loading players from CSV for sync: {csv_path}")
    df = load_players_from_csv(csv_path)
    
    # Get database session
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Clear existing data (optional - comment out to preserve existing data)
        session.query(Player).delete()
        
        # Insert players from CSV
        players_added = 0
        for _, row in df.iterrows():
            player = Player(
                name=row['name'],
                runs=int(row['runs']),
                wickets=int(row['wickets']),
                strike_rate=float(row['strike_rate']),
                price=float(row['price']),
                role=row['role']
            )
            session.add(player)
            players_added += 1
        
        logger.info(f"✓ Synced {players_added} players from CSV to database")
        return players_added
        
    except Exception as e:
        session.rollback()
        logger.error
    except Exception as e:
        session.rollback()
        print(f"Error syncing CSV to database: {e}")
        raise
    finally:
        session.close()


def load_players_from_database() -> Optional[pd.DataFrame]:
    """
    Load players from database.
    
    Returns:
        DataFrame with player data, or None if database is unavailable
    """
    if not is_database_available():
        return None
    
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Query all players
        players = session.query(Player).all()
        
        if not players:
            logger.warning("Database is empty. Consider syncing CSV data.")
            return None
        
        # Convert to DataFrame
        data = []
        for player in players:
            data.append({
                'name': player.name,
                'runs': player.runs,
                'wickets': player.wickets,
                'strike_rate': player.strike_rate,
                'price': player.price,
                'role': player.role
            })
        
        df = pd.DataFrame(data)
        
        # Set proper dtypes (same as CSV loader)
        df = df.astype({
            'name': str,
            'runs': 'Int64',
            'wickets': 'Int64',
            'strike_rate': float,
            'price': float,
            'role': str
        })
        
        logger.info(f"✓ Loaded {len(df)} players from database")
        return df
        
    except Exception as e:
        logger.error(f"Error loading from database: {e}")
        return None
    finally:
        session.close()


def load_players(
    csv_path: str = "players.csv",
    auto_sync: bool = True
) -> pd.DataFrame:
    """
    Load players with smart fallback: database first, then CSV.
    
    Strategy:
        1. Try to load from database
        2. If database unavailable or empty, load from CSV
        3. If auto_sync=True and database is available but empty, sync CSV to DB
    
    Args:
        csv_path: Path to CSV file (fallback)
        auto_sync: Automatically sync CSV to database if DB is empty
    
    Returns:
        DataFrame with player data
    
    Raises:
        FileNotFoundError: If CSV file doesn't exist (when database is unavailable)
        ValueError: If data validation fails
    """
    # Try database first
    if is_database_available():
        df = load_players_from_database()
        
        if df is not None and not df.empty:
            logger.info("✓ Using database as data source")
            return df
        
        # Database is empty - try to sync from CSV
        if auto_sync:
            logger.info("Database is empty. Syncing from CSV...")
            try:
                sync_csv_to_database(csv_path)
                df = load_players_from_database()
                if df is not None:
                    logger.info("✓ Using database as data source (after sync)")
                    return df
            except Exception as e:
                logger.warning(f"Auto-sync failed: {e}. Falling back to CSV.")
    
    # Fallback to CSV
    logger.info("✓ Using CSV as data source")
    return load_players_from_csv(csv_path)


def get_data_source() -> str:
    """
    Get current data source.
    
    Returns:
        'database' if database is available, 'csv' otherwise
    """
    if is_database_available():
        # Check if database has data
        session_gen = get_session()
        session = next(session_gen)
        try:
            count = session.query(Player).count()
            if count > 0:
                return 'database'
        except:
            pass
        finally:
            session.close()
    
    return 'csv'
