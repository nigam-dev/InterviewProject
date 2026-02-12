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
    
    # Load CSV
    try:
        df = pd.read_csv(csv_file)
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {str(e)}")
    
    # Validate required columns
    required_columns = ["name", "runs", "wickets", "strike_rate", "price"]
    missing_columns = set(required_columns) - set(df.columns)
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Check for empty dataframe
    if df.empty:
        raise ValueError("CSV file is empty")
    
    # Ensure numeric types for numeric columns
    numeric_columns = ["runs", "wickets", "strike_rate", "price"]
    
    for col in numeric_columns:
        try:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        except Exception as e:
            raise ValueError(f"Error converting column '{col}' to numeric: {str(e)}")
    
    # Check for missing values after conversion
    if df[numeric_columns].isnull().any().any():
        null_counts = df[numeric_columns].isnull().sum()
        null_cols = null_counts[null_counts > 0].to_dict()
        raise ValueError(f"Invalid numeric values found in columns: {null_cols}")
    
    # Ensure name is string type
    df["name"] = df["name"].astype(str)
    
    # Validate data ranges
    if (df["runs"] < 0).any() or (df["runs"] > 1000).any():
        raise ValueError("Runs must be between 0 and 1000")
    
    if (df["wickets"] < 0).any() or (df["wickets"] > 50).any():
        raise ValueError("Wickets must be between 0 and 50")
    
    if (df["strike_rate"] < 0).any() or (df["strike_rate"] > 250).any():
        raise ValueError("Strike rate must be between 0 and 250")
    
    if (df["price"] <= 0).any() or (df["price"] > 100).any():
        raise ValueError("Price must be greater than 0 and at most 100")
    
    # Check for duplicate player names
    if df["name"].duplicated().any():
        duplicates = df[df["name"].duplicated()]["name"].tolist()
        raise ValueError(f"Duplicate player names found: {duplicates}")
    
    return df
