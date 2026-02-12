from typing import List, Set
import pulp
from models import Player, OptimizationConstraints, OptimizedTeam
from scoring import ScoringEngine


class TeamOptimizer:
    """Handles team optimization using linear programming."""
    
    def __init__(self):
        """Initialize the optimizer."""
        self.scoring_engine = ScoringEngine()
    
    def optimize(
        self,
        available_players: List[Player],
        constraints: OptimizationConstraints,
        excluded_player_ids: Set[int] | None = None,
        required_player_ids: Set[int] | None = None
    ) -> OptimizedTeam:
        """
        Optimize team selection based on constraints.
        
        Args:
            available_players: List of all available players
            constraints: Optimization constraints
            excluded_player_ids: Set of player IDs to exclude
            required_player_ids: Set of player IDs that must be included
        
        Returns:
            OptimizedTeam object with results
        """
        excluded_player_ids = excluded_player_ids or set()
        required_player_ids = required_player_ids or set()
        
        # Filter out excluded players
        players = [p for p in available_players if p.id not in excluded_player_ids]
        
        if not players:
            return OptimizedTeam(
                players=[],
                total_salary=0.0,
                total_projected_points=0.0,
                success=False,
                message="No players available after applying exclusions"
            )
        
        # Create the optimization problem
        prob = pulp.LpProblem("Team_Optimization", pulp.LpMaximize)
        
        # Decision variables: 1 if player is selected, 0 otherwise
        player_vars = {
            player.id: pulp.LpVariable(f"player_{player.id}", cat="Binary")
            for player in players
        }
        
        # Objective: Maximize total projected points
        prob += pulp.lpSum(
            player.projected_points * player_vars[player.id]
            for player in players
        ), "Total_Points"
        
        # Constraint: Salary cap
        prob += pulp.lpSum(
            player.salary * player_vars[player.id]
            for player in players
        ) <= constraints.salary_cap, "Salary_Cap"
        
        # Constraint: Minimum players
        prob += pulp.lpSum(
            player_vars[player.id]
            for player in players
        ) >= constraints.min_players, "Min_Players"
        
        # Constraint: Maximum players
        prob += pulp.lpSum(
            player_vars[player.id]
            for player in players
        ) <= constraints.max_players, "Max_Players"
        
        # Constraint: Required players must be selected
        for player_id in required_player_ids:
            if player_id in player_vars:
                prob += player_vars[player_id] == 1, f"Required_Player_{player_id}"
        
        # Constraint: Position requirements
        if constraints.positions:
            # Group players by position
            players_by_position: dict[str, List[Player]] = {}
            for player in players:
                if player.position not in players_by_position:
                    players_by_position[player.position] = []
                players_by_position[player.position].append(player)
            
            # Add position constraints
            for position, count in constraints.positions.items():
                if position in players_by_position:
                    prob += pulp.lpSum(
                        player_vars[player.id]
                        for player in players_by_position[position]
                    ) == count, f"Position_{position}"
        
        # Solve the optimization problem
        # Use PULP_CBC_CMD solver with msg=0 to suppress output
        solver = pulp.PULP_CBC_CMD(msg=0)
        prob.solve(solver)
        
        # Check if solution was found
        if prob.status != pulp.LpStatusOptimal:
            return OptimizedTeam(
                players=[],
                total_salary=0.0,
                total_projected_points=0.0,
                success=False,
                message=f"No optimal solution found. Status: {pulp.LpStatus[prob.status]}"
            )
        
        # Extract selected players
        selected_players = [
            player for player in players
            if player_vars[player.id].varValue == 1
        ]
        
        # Calculate totals
        total_salary = self.scoring_engine.calculate_team_salary(selected_players)
        total_points = self.scoring_engine.calculate_team_score(selected_players)
        
        return OptimizedTeam(
            players=selected_players,
            total_salary=total_salary,
            total_projected_points=total_points,
            success=True,
            message="Optimization successful"
        )
