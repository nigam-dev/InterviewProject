import pandas as pd
from pathlib import Path


def load_players(csv_path: str = "players.csv") -> pd.DataFrame:
    """
    Load player data from CSV file.
    
    Args:
        csv_path: Path to the CSV file containing player data
        
    Returns:
        pd.DataFrame: Validated player data with proper types
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If required columns are missing or data is invalid
    """
    csv_file = Path(csv_path)
    
    # Check if file exists
    if not csv_file.exists():
        raise FileNotFoundError(f"Player data file not found: {csv_path}")
    
    # Load CSV with explicit dtypes for performance (avoids type inference)
    try:
        df = pd.read_csv(
            csv_file,
            dtype={
                "name": str,
                "runs": "Int64",
                "wickets": "Int64",
                "strike_rate": float,
                "price": float,
                "role": str
            }
        )
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {str(e)}")
    
    # Validate required columns
    required_columns = ["name", "runs", "wickets", "strike_rate", "price", "role"]
    missing_columns = set(required_columns) - set(df.columns)
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Check for empty dataframe
    if df.empty:
        raise ValueError("CSV file is empty")
    
    # Check for missing values (vectorized, single pass)
    numeric_columns = ["runs", "wickets", "strike_rate", "price"]
    null_mask = df[numeric_columns].isnull()
    if null_mask.values.any():
        null_counts = null_mask.sum()
        null_cols = null_counts[null_counts > 0].to_dict()
        raise ValueError(f"Invalid numeric values found in columns: {null_cols}")
    
    # Validate data ranges (vectorized, combined checks for efficiency)
    runs = df["runs"].values
    wickets = df["wickets"].values
    strike_rate = df["strike_rate"].values
    price = df["price"].values
    
    if (runs < 0).any() or (runs > 1000).any():
        raise ValueError("Runs must be between 0 and 1000")
    
    if (wickets < 0).any() or (wickets > 50).any():
        raise ValueError("Wickets must be between 0 and 50")
    
    if (strike_rate < 0).any() or (strike_rate > 250).any():
        raise ValueError("Strike rate must be between 0 and 250")
    
    if (price <= 0).any() or (price > 100).any():
        raise ValueError("Price must be greater than 0 and at most 100")
    
    # Check for duplicate player names
    if df["name"].duplicated().any():
        duplicates = df[df["name"].duplicated()]["name"].tolist()
        raise ValueError(f"Duplicate player names found: {duplicates}")
    
    # Validate role values
    allowed_roles = {"BAT", "BOWL", "ALL", "WK"}
    invalid_roles = set(df["role"].unique()) - allowed_roles
    if invalid_roles:
        raise ValueError(f"Invalid role values found: {invalid_roles}. Allowed roles: {allowed_roles}")
    
    return df
