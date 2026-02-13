import pandas as pd
import pytest
from services.scoring import calculate_score

@pytest.fixture
def sample_player_df():
    """Create a sample DataFrame for testing."""
    data = {
        "name": ["Player1", "Player2"],
        "runs": [100, 50],
        "wickets": [2, 5],
        "strike_rate": [120.0, 100.0],
        "price": [10.0, 8.0],
        "role": ["BAT", "BOWL"]
    }
    return pd.DataFrame(data)

def test_calculate_score_logic(sample_player_df):
    """Test the score calculation formula."""
    # Calculate scores
    df_scored = calculate_score(sample_player_df)
    
    # Formula: (runs * 0.5) + (wickets * 20) + (strike_rate * 0.3)
    
    # Player 1: (100 * 0.5) + (2 * 20) + (120 * 0.3)
    #           = 50 + 40 + 36 = 126
    player1_score = df_scored.iloc[0]["score"]
    assert player1_score == 126.0
    
    # Player 2: (50 * 0.5) + (5 * 20) + (100 * 0.3)
    #           = 25 + 100 + 30 = 155
    player2_score = df_scored.iloc[1]["score"]
    assert player2_score == 155.0

def test_calculate_score_preserves_columns(sample_player_df):
    """Test that original columns are preserved and new one added."""
    df_scored = calculate_score(sample_player_df)
    
    assert "score" in df_scored.columns
    assert "name" in df_scored.columns
    assert "price" in df_scored.columns
    # Verify original data wasn't modified in place (copy check)
    assert id(df_scored) != id(sample_player_df)

def test_calculate_score_missing_columns():
    """Test validation for missing columns."""
    df_invalid = pd.DataFrame({"name": ["P1"], "runs": [10]})
    
    with pytest.raises(ValueError, match="Missing required columns"):
        calculate_score(df_invalid)
