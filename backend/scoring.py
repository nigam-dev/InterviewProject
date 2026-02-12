from typing import List
from models import Player


class ScoringEngine:
    """Handles scoring calculations for players and teams."""
    
    @staticmethod
    def calculate_team_score(players: List[Player]) -> float:
        """Calculate total projected points for a team."""
        return sum(player.projected_points for player in players)
    
    @staticmethod
    def calculate_team_salary(players: List[Player]) -> float:
        """Calculate total salary for a team."""
        return sum(player.salary for player in players)
    
    @staticmethod
    def calculate_value_score(player: Player) -> float:
        """Calculate value score (points per dollar) for a player."""
        if player.salary == 0:
            return 0.0
        return player.projected_points / player.salary
    
    @staticmethod
    def get_position_breakdown(players: List[Player]) -> dict[str, int]:
        """Get count of players by position."""
        breakdown: dict[str, int] = {}
        for player in players:
            breakdown[player.position] = breakdown.get(player.position, 0) + 1
        return breakdown
    
    @staticmethod
    def validate_team_constraints(
        players: List[Player],
        salary_cap: float,
        min_players: int,
        max_players: int
    ) -> tuple[bool, str]:
        """
        Validate if a team meets the constraints.
        
        Returns:
            tuple: (is_valid, message)
        """
        team_size = len(players)
        team_salary = ScoringEngine.calculate_team_salary(players)
        
        if team_size < min_players:
            return False, f"Team has {team_size} players, minimum is {min_players}"
        
        if team_size > max_players:
            return False, f"Team has {team_size} players, maximum is {max_players}"
        
        if team_salary > salary_cap:
            return False, f"Team salary ${team_salary:,.2f} exceeds cap ${salary_cap:,.2f}"
        
        return True, "Team meets all constraints"
