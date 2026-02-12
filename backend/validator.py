import pandas as pd
from typing import Dict, Optional


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


def validate_optimization_inputs(
    budget: int,
    df: pd.DataFrame,
    role_constraints: Optional[Dict[str, int]] = None
) -> None:
    """
    Validate inputs before team optimization.
    
    Validates:
        1. Budget is positive
        2. Budget is sufficient for minimum possible team cost
        3. Enough players available for each required role
    
    Args:
        budget: Maximum budget allowed
        df: DataFrame with columns: name, price, role
        role_constraints: Dict mapping role names to required counts
                         (default: {"WK": 1, "BAT": 4, "BOWL": 3, "ALL": 3})
    
    Raises:
        ValidationError: If any validation check fails
    """
    # Set default role constraints if not provided
    if role_constraints is None:
        role_constraints = {
            "WK": 1,
            "BAT": 4,
            "BOWL": 3,
            "ALL": 3
        }
    
    # Validation 1: Budget must be positive
    if budget <= 0:
        raise ValidationError(
            f"Budget must be positive. Provided budget: ${budget}"
        )
    
    # Validation 2: Check if DataFrame has required columns
    required_columns = ["name", "price", "role"]
    missing_columns = set(required_columns) - set(df.columns)
    if missing_columns:
        raise ValidationError(
            f"Missing required columns in player data: {missing_columns}"
        )
    
    # Validation 3: Check enough players available per role
    role_availability = df['role'].value_counts().to_dict()
    
    for role, required_count in role_constraints.items():
        available_count = role_availability.get(role, 0)
        
        if available_count < required_count:
            raise ValidationError(
                f"Insufficient players for role '{role}': "
                f"Required {required_count}, but only {available_count} available. "
                f"Available roles: {role_availability}"
            )
    
    # Validation 4: Calculate minimum possible team cost
    min_cost = 0
    cheapest_players_used = set()
    
    for role, required_count in role_constraints.items():
        # Get players of this role
        role_players = df[df['role'] == role].copy()
        
        if role_players.empty:
            raise ValidationError(
                f"No players available for role '{role}'. "
                f"Available roles: {list(role_availability.keys())}"
            )
        
        # Get cheapest players for this role
        cheapest_role_players = role_players.nsmallest(required_count, 'price')
        
        # Add to minimum cost
        min_cost += cheapest_role_players['price'].sum()
    
    # Check if budget is sufficient
    if budget < min_cost:
        raise ValidationError(
            f"Budget ${budget} is insufficient. "
            f"Minimum cost for required team composition is ${min_cost:.2f}. "
            f"Please increase budget by at least ${min_cost - budget:.2f}. "
            f"Required composition: {role_constraints}"
        )
    
    # All validations passed
    return None


def validate_budget_range(budget: int, min_budget: int = 1, max_budget: int = 1000) -> None:
    """
    Validate budget is within acceptable range.
    
    Args:
        budget: Budget to validate
        min_budget: Minimum acceptable budget (default: 1)
        max_budget: Maximum acceptable budget (default: 1000)
    
    Raises:
        ValidationError: If budget is out of range
    """
    if budget < min_budget:
        raise ValidationError(
            f"Budget ${budget} is below minimum allowed budget ${min_budget}"
        )
    
    if budget > max_budget:
        raise ValidationError(
            f"Budget ${budget} exceeds maximum allowed budget ${max_budget}"
        )


def validate_dataframe(df: pd.DataFrame) -> None:
    """
    Validate DataFrame structure and content.
    
    Args:
        df: DataFrame to validate
    
    Raises:
        ValidationError: If DataFrame is invalid
    """
    # Check if DataFrame is empty
    if df.empty:
        raise ValidationError("Player data is empty. No players available for selection.")
    
    # Check for required columns
    required_columns = ["name", "price", "role", "score"]
    missing_columns = set(required_columns) - set(df.columns)
    
    if missing_columns:
        raise ValidationError(
            f"Missing required columns: {missing_columns}. "
            f"Available columns: {list(df.columns)}"
        )
    
    # Check for null values in critical columns
    critical_columns = ["name", "price", "role"]
    for col in critical_columns:
        null_count = df[col].isnull().sum()
        if null_count > 0:
            raise ValidationError(
                f"Found {null_count} null values in column '{col}'. "
                f"All players must have valid {col} values."
            )
    
    # Check for invalid prices
    if (df['price'] <= 0).any():
        invalid_players = df[df['price'] <= 0]['name'].tolist()
        raise ValidationError(
            f"Found players with invalid prices (<=0): {invalid_players}"
        )
