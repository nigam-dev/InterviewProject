import pandas as pd
import pulp
from typing import Dict, List, Any, Optional
from logger import get_logger
from models import OptimizationStrategy

logger = get_logger(__name__)


def optimize_team(
    df: pd.DataFrame,
    budget: int,
    team_size: int = 11,
    role_constraints: Optional[Dict[str, int]] = None,
    strategy: OptimizationStrategy = OptimizationStrategy.MAX_SCORE
) -> Dict[str, Any]:
    """
    Optimize cricket team selection using Linear Programming.
    
    Objective:
        Maximize total score or efficiency based on strategy.
    
    Constraints:
        - sum(price) <= budget
        - select exactly team_size players
        - Role-based constraints (customizable via role_constraints parameter)
    
    Args:
        df: DataFrame with columns: name, price, score, role
        budget: Maximum budget allowed
        team_size: Number of players to select (default: 11)
        role_constraints: Dict mapping role names to required counts
        strategy: Optimization strategy (MAX_SCORE or MAX_SCORE_PER_COST)
    
    Returns:
        Dict containing:
            - players: List of selected player records (as dicts)
            - total_cost: Total price of selected team
            - total_score: Total score of selected team
    
    Raises:
        ValueError: If required columns are missing or no feasible solution exists
    """
    # Set default role constraints if not provided
    if role_constraints is None:
        role_constraints = {
            "WK": 1,
            "BAT": 4,
            "BOWL": 3,
            "ALL": 3
        }
    # Validate required columns
    required_columns = ["name", "price", "score", "role"]
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
    
    # Extract numpy arrays for faster access (avoids repeated .loc[] calls)
    indices = df.index.tolist()
    scores = df["score"].values
    prices = df["price"].values
    roles = df["role"].values
    
    # Create optimization problem
    prob = pulp.LpProblem("Cricket_Team_Optimization", pulp.LpMaximize)
    
    # Create binary decision variables for each player
    player_vars = {
        idx: pulp.LpVariable(f"player_{idx}", cat="Binary")
        for idx in indices
    }
    
    # Objective: Maximize based on strategy
    if strategy == OptimizationStrategy.MAX_SCORE_PER_COST:
        # Strategy: Maximize sum of (score/cost) for each player (Efficiency)
        # Note: If price is 0, we handle it to avoid division by zero
        efficiencies = []
        for i in range(len(prices)):
            price = prices[i]
            score = scores[i]
            if price > 0:
                efficiencies.append(score / price)
            else:
                # If price is 0, assign high efficiency if score > 0
                efficiencies.append(score * 1000 if score > 0 else 0)
                
        prob += pulp.lpSum(
            efficiencies[i] * player_vars[idx]
            for i, idx in enumerate(indices)
        ), "Total_Efficiency"
    else:
        # Default Strategy: Maximize Total Score
        prob += pulp.lpSum(
            scores[i] * player_vars[idx]
            for i, idx in enumerate(indices)
        ), "Total_Score"
    
    # Constraint 1: Total price <= budget (using pre-extracted arrays)
    prob += pulp.lpSum(
        prices[i] * player_vars[idx]
        for i, idx in enumerate(indices)
    ) <= budget, "Budget_Constraint"
    
    # Constraint 2: Select exactly team_size players
    prob += pulp.lpSum(
        player_vars[idx]
        for idx in indices
    ) == team_size, "Team_Size_Constraint"
    
    # Constraint 3: Role-based constraints (dynamic)
    for role, required_count in role_constraints.items():
        prob += pulp.lpSum(
            player_vars[idx]
            for i, idx in enumerate(indices)
            if roles[i] == role
        ) == required_count, f"{role}_Constraint"
    
    # Solve the problem using CBC solver (deterministic and stable)
    solver = pulp.PULP_CBC_CMD(msg=0)
    prob.solve(solver)
    
    # Check if solution was found
    if prob.status != pulp.LpStatusOptimal:
        status_msg = pulp.LpStatus[prob.status]
        logger.warning(f"Optimization failed. Status: {status_msg}")
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
