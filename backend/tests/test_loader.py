import pandas as pd
import pytest
from repositories.data_loader import load_players

def test_load_players_success(tmp_path):
    """Test loading valid player data from CSV."""
    # Create a temporary CSV file
    csv_content = """name,runs,wickets,strike_rate,price,role
Player1,100,2,120.5,10.0,BAT
Player2,50,5,110.0,8.5,BOWL
"""
    csv_file = tmp_path / "players.csv"
    csv_file.write_text(csv_content)
    
    # Load players
    df = load_players(str(csv_file))
    
    # Assertions
    assert len(df) == 2
    assert "name" in df.columns
    assert df.iloc[0]["name"] == "Player1"
    assert df.iloc[0]["role"] == "BAT"

def test_load_players_file_not_found():
    """Test loading from a non-existent file."""
    with pytest.raises(FileNotFoundError):
        load_players("non_existent_file.csv")

def test_load_players_missing_columns(tmp_path):
    """Test loading CSV with missing required columns."""
    # Create invalid CSV content (missing 'role')
    csv_content = """name,runs,wickets,strike_rate,price
Player1,100,2,120.5,10.0
"""
    csv_file = tmp_path / "invalid_players.csv"
    csv_file.write_text(csv_content)
    
    # Expect ValueError for missing columns
    with pytest.raises(ValueError, match="Missing required columns"):
        load_players(str(csv_file))

def test_load_players_empty_file(tmp_path):
    """Test loading an empty CSV file."""
    csv_file = tmp_path / "empty.csv"
    csv_file.write_text("")
    
    with pytest.raises(ValueError):
        load_players(str(csv_file))
