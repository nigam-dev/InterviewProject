from typing import List, Set
import pulp
from models import Player, OptimizationConstraints, OptimizedTeam
from scoring import ScoringEngine


class TeamOptimizer:
    """Handles cricket team optimization using linear programming."""
    
    def __init__(self):
        """Initialize the optimizer."""
        self.scoring_engine = ScoringEngine()
    
    def optimize(
        self,
        available_players: List[Player],
        constraints: OptimizationConstraints,
        excluded_player_names: Set[str] | None = None,
        required_player_names: Set[str] | None = None
    ) -> OptimizedTeam:
        """
        Optimize cricket team selection based on constraints.
        
        Args:
            available_players: List of all available players
            constraints: Optimization constraints (budget, team_size)
            excluded_player_names: Set of player names to exclude
            required_player_names: Set of player names that must be included
        
        Returns:
            OptimizedTeam object with results
        """
        excluded_player_names = excluded_player_names or set()
        required_player_names = required_player_names or set()
        
        # Filter out excluded players
        players = [p for p in available_players if p.name not in excluded_player_names]
        
        if not players:
            return OptimizedTeam(
                players=[],
                total_price=0.0,
                total_runs=0.0,
                total_wickets=0.0,
                avg_strike_rate=0.0,
                success=False,
                message="No players available after applying exclusions"
            )
        
        # Create the optimization problem
        prob = pulp.LpProblem("Cricket_Team_Optimization", pulp.LpMaximize)
        
        # Decision variables: 1 if player is selected, 0 otherwise
        player_vars = {
            player.name: pulp.LpVariable(f"player_{i}", cat="Binary")
            for i, player in enumerate(players)
        }
        
        # Objective: Maximize team score (runs + weighted wickets)
        prob += pulp.lpSum(
            (player.runs + player.wickets * 20) * player_vars[player.name]
            for player in players
        ), "Total_Score"
        
        # Constraint: Budget
        prob += pulp.lpSum(
            player.price * player_vars[player.name]
            for player in players
        ) <= constraints.budget, "Budget_Constraint"
        
        # Constraint: Team size (exactly team_size players)
        prob += pulp.lpSum(
            player_vars[player.name]
            for player in players
        ) == constraints.team_size, "Team_Size"
        
        # Constraint: Required players must be selected
        for player_name in required_player_names:
            if player_name in player_vars:
                prob += player_vars[player_name] == 1, f"Required_Player_{player_name}"
        
        # Solve the optimization problem
        solver = pulp.PULP_CBC_CMD(msg=0)
        prob.solve(solver)
        
        # Check if solution was found
        if prob.status != pulp.LpStatusOptimal:
            return OptimizedTeam(
                players=[],
                total_price=0.0,
                total_runs=0.0,
                total_wickets=0.0,
                avg_strike_rate=0.0,
                success=False,
                message=f"No optimal solution found. Status: {pulp.LpStatus[prob.status]}"
            )
        
        # Extract selected players
        selected_players = [
            player for player in players
            if player_vars[player.name].varValue == 1
        ]
        
        # Calculate totals
        total_price = self.scoring_engine.calculate_total_price(selected_players)
        total_runs = self.scoring_engine.calculate_total_runs(selected_players)
        total_wickets = self.scoring_engine.calculate_total_wickets(selected_players)
        avg_sr = self.scoring_engine.calculate_avg_strike_rate(selected_players)
        
        return OptimizedTeam(
            players=selected_players,
            total_price=total_price,
            total_runs=total_runs,
            total_wickets=total_wickets,
            avg_strike_rate=avg_sr,
            success=True,
            message="Optimization successful"
        )
