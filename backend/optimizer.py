import pandas as pd
import pulp
from typing import Dict, List, Any


def optimize_team(
    df: pd.DataFrame,
    budget: int,
    team_size: int = 11
) -> Dict[str, Any]:
    """
    Optimize cricket team selection using Linear Programming.
    
    Objective:
        Maximize total score
    
    Constraints:
        - sum(price) <= budget
        - select exactly team_size players
    
    Args:
        df: DataFrame with columns: name, price, score
        budget: Maximum budget allowed
        team_size: Number of players to select (default: 11)
    
    Returns:
        Dict containing:
            - players: List of selected player records (as dicts)
            - total_cost: Total price of selected team
            - total_score: Total score of selected team
    
    Raises:
        ValueError: If required columns are missing or no feasible solution exists
    """
    # Validate required columns
    required_columns = ["name", "price", "score"]
    missing_columns = set(required_columns) - set(df.columns)
    
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    if team_size <= 0:
        raise ValueError(f"team_size must be positive, got {team_size}")
    
    if team_size > len(df):
        raise ValueError(f"team_size ({team_size}) exceeds available players ({len(df)})")
    
    if budget <= 0:
        raise ValueError(f"budget must be positive, got {budget}")
    
    # Create optimization problem
    prob = pulp.LpProblem("Cricket_Team_Optimization", pulp.LpMaximize)
    
    # Create binary decision variables for each player
    # Use player index to ensure deterministic behavior
    player_vars = {}
    for idx in df.index:
        player_vars[idx] = pulp.LpVariable(f"player_{idx}", cat="Binary")
    
    # Objective: Maximize total score
    prob += pulp.lpSum(
        df.loc[idx, "score"] * player_vars[idx]
        for idx in df.index
    ), "Total_Score"
    
    # Constraint 1: Total price <= budget
    prob += pulp.lpSum(
        df.loc[idx, "price"] * player_vars[idx]
        for idx in df.index
    ) <= budget, "Budget_Constraint"
    
    # Constraint 2: Select exactly team_size players
    prob += pulp.lpSum(
        player_vars[idx]
        for idx in df.index
    ) == team_size, "Team_Size_Constraint"
    
    # Solve the problem using CBC solver (deterministic and stable)
    solver = pulp.PULP_CBC_CMD(msg=0)
    prob.solve(solver)
    
    # Check if solution was found
    if prob.status != pulp.LpStatusOptimal:
        status_msg = pulp.LpStatus[prob.status]
        raise ValueError(f"No optimal solution found. Status: {status_msg}")
    
    # Extract selected players
    selected_indices = [
        idx for idx in df.index
        if player_vars[idx].varValue == 1
    ]
    
    # Get selected players as list of dicts
    selected_df = df.loc[selected_indices]
    players_list = selected_df.to_dict('records')
    
    # Calculate totals
    total_cost = float(selected_df["price"].sum())
    total_score = float(selected_df["score"].sum())
    
    return {
        "players": players_list,
        "total_cost": total_cost,
        "total_score": total_score
    }
