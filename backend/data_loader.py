import pandas as pd
from pathlib import Path
from typing import List
from models import Player


class DataLoader:
    """Handles loading and processing player data."""
    
    def __init__(self, csv_path: str = "players.csv"):
        """Initialize data loader with CSV path."""
        self.csv_path = Path(csv_path)
        self._data: pd.DataFrame | None = None
    
    def load_data(self) -> pd.DataFrame:
        """Load player data from CSV file."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Player data file not found: {self.csv_path}")
        
        self._data = pd.read_csv(self.csv_path)
        
        # Validate required columns
        required_columns = ["id", "name", "position", "salary", "projected_points", "team"]
        missing_columns = set(required_columns) - set(self._data.columns)
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        return self._data
    
    def get_all_players(self) -> List[Player]:
        """Get all players as list of Player models."""
        if self._data is None:
            self.load_data()
        
        players = []
        for _, row in self._data.iterrows():
            player = Player(
                id=int(row["id"]),
                name=str(row["name"]),
                position=str(row["position"]),
                salary=float(row["salary"]),
                projected_points=float(row["projected_points"]),
                team=str(row["team"])
            )
            players.append(player)
        
        return players
    
    def get_player_by_id(self, player_id: int) -> Player | None:
        """Get a specific player by ID."""
        if self._data is None:
            self.load_data()
        
        player_row = self._data[self._data["id"] == player_id]
        
        if player_row.empty:
            return None
        
        row = player_row.iloc[0]
        return Player(
            id=int(row["id"]),
            name=str(row["name"]),
            position=str(row["position"]),
            salary=float(row["salary"]),
            projected_points=float(row["projected_points"]),
            team=str(row["team"])
        )
    
    def filter_players(self, position: str | None = None, max_salary: float | None = None) -> List[Player]:
        """Filter players by position and/or salary."""
        if self._data is None:
            self.load_data()
        
        filtered = self._data.copy()
        
        if position:
            filtered = filtered[filtered["position"] == position]
        
        if max_salary is not None:
            filtered = filtered[filtered["salary"] <= max_salary]
        
        players = []
        for _, row in filtered.iterrows():
            player = Player(
                id=int(row["id"]),
                name=str(row["name"]),
                position=str(row["position"]),
                salary=float(row["salary"]),
                projected_points=float(row["projected_points"]),
                team=str(row["team"])
            )
            players.append(player)
        
        return players
