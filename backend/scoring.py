from typing import List
from models import Player


class ScoringEngine:
    """Handles scoring calculations for cricket players and teams."""
    
    @staticmethod
    def calculate_total_runs(players: List[Player]) -> float:
        """Calculate total runs for a team."""
        return sum(player.runs for player in players)
    
    @staticmethod
    def calculate_total_wickets(players: List[Player]) -> float:
        """Calculate total wickets for a team."""
        return sum(player.wickets for player in players)
    
    @staticmethod
    def calculate_total_price(players: List[Player]) -> float:
        """Calculate total price for a team."""
        return sum(player.price for player in players)
    
    @staticmethod
    def calculate_avg_strike_rate(players: List[Player]) -> float:
        """Calculate average strike rate for a team."""
        if not players:
            return 0.0
        total_strike_rate = sum(player.strike_rate for player in players)
        return total_strike_rate / len(players)
    
    @staticmethod
    def calculate_team_score(players: List[Player]) -> float:
        """
        Calculate overall team score (weighted combination of runs and wickets).
        Higher is better.
        """
        total_runs = ScoringEngine.calculate_total_runs(players)
        total_wickets = ScoringEngine.calculate_total_wickets(players)
        # Weight runs and wickets equally for simplicity
        return total_runs + (total_wickets * 20)
    
    @staticmethod
    def validate_team_constraints(
        players: List[Player],
        budget: float,
        team_size: int
    ) -> tuple[bool, str]:
        """
        Validate if a team meets the constraints.
        
        Returns:
            tuple: (is_valid, message)
        """
        actual_size = len(players)
        total_price = ScoringEngine.calculate_total_price(players)
        
        if actual_size != team_size:
            return False, f"Team has {actual_size} players, required {team_size}"
        
        if total_price > budget:
            return False, f"Team price {total_price:.2f} exceeds budget {budget:.2f}"
        
        return True, "Team meets all constraints"
