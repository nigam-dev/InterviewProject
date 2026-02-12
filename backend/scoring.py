import pandas as pd


def calculate_score(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate player scores based on performance metrics.
    
    Formula:
        score = (runs * 0.5) + (wickets * 20) + (strike_rate * 0.3)
    
    Args:
        df: DataFrame with columns: runs, wickets, strike_rate
        
    Returns:
        DataFrame with added 'score' column (original df is not modified)
        
    Raises:
        ValueError: If required columns are missing
    """
    # Create a copy to avoid modifying original
    df_copy = df.copy()
    
    # Validate required columns
    required_columns = ["runs", "wickets", "strike_rate"]
    missing_columns = set(required_columns) - set(df_copy.columns)
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    # Calculate score using the formula
    df_copy["score"] = (
        (df_copy["runs"] * 0.5) +
        (df_copy["wickets"] * 20) +
        (df_copy["strike_rate"] * 0.3)
    )
    
    return df_copy
