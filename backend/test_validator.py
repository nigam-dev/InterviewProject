"""
Test validation layer with various scenarios
"""
from data_loader import load_players
from scoring import calculate_score
from validator import (
    validate_optimization_inputs,
    validate_budget_range,
    validate_dataframe,
    ValidationError
)
import pandas as pd


def test_valid_inputs():
    """Test validation with valid inputs"""
    print("=" * 70)
    print("Test 1: Valid Inputs")
    print("=" * 70)
    
    df = load_players("players.csv")
    df_scored = calculate_score(df)
    
    # Test with sufficient budget
    budgets = [175, 200, 250]
    
    for budget in budgets:
        try:
            validate_optimization_inputs(budget, df_scored)
            print(f"✓ Budget ${budget}: Validation passed")
        except ValidationError as e:
            print(f"✗ Budget ${budget}: Unexpected validation error: {e}")


def test_negative_budget():
    """Test validation with negative budget"""
    print("\n" + "=" * 70)
    print("Test 2: Negative Budget")
    print("=" * 70)
    
    df = load_players("players.csv")
    df_scored = calculate_score(df)
    
    try:
        validate_optimization_inputs(-10, df_scored)
        print("✗ Should have raised ValidationError for negative budget")
    except ValidationError as e:
        print(f"✓ Correctly rejected negative budget: {e}")


def test_zero_budget():
    """Test validation with zero budget"""
    print("\n" + "=" * 70)
    print("Test 3: Zero Budget")
    print("=" * 70)
    
    df = load_players("players.csv")
    df_scored = calculate_score(df)
    
    try:
        validate_optimization_inputs(0, df_scored)
        print("✗ Should have raised ValidationError for zero budget")
    except ValidationError as e:
        print(f"✓ Correctly rejected zero budget: {e}")


def test_insufficient_budget():
    """Test validation with insufficient budget"""
    print("\n" + "=" * 70)
    print("Test 4: Insufficient Budget")
    print("=" * 70)
    
    df = load_players("players.csv")
    df_scored = calculate_score(df)
    
    # Try budgets that are too low
    low_budgets = [50, 100, 150]
    
    for budget in low_budgets:
        try:
            validate_optimization_inputs(budget, df_scored)
            print(f"✗ Budget ${budget}: Should have raised ValidationError")
        except ValidationError as e:
            print(f"✓ Budget ${budget}: Correctly rejected")
            print(f"  Reason: {e}")


def test_insufficient_players_per_role():
    """Test validation with insufficient players per role"""
    print("\n" + "=" * 70)
    print("Test 5: Insufficient Players Per Role")
    print("=" * 70)
    
    df = load_players("players.csv")
    df_scored = calculate_score(df)
    
    # Test with impossible role constraints
    impossible_constraints = [
        {"WK": 10, "BAT": 1, "BOWL": 0, "ALL": 0},  # Only 7 WK available
        {"WK": 1, "BAT": 20, "BOWL": 0, "ALL": 0},  # Only 8 BAT available
        {"WK": 0, "BAT": 0, "BOWL": 15, "ALL": 0},  # Only 8 BOWL available
    ]
    
    for constraints in impossible_constraints:
        try:
            validate_optimization_inputs(200, df_scored, constraints)
            print(f"✗ Should have raised ValidationError for {constraints}")
        except ValidationError as e:
            print(f"✓ Correctly rejected {constraints}")
            print(f"  Reason: {e}")


def test_custom_role_constraints():
    """Test validation with custom role constraints"""
    print("\n" + "=" * 70)
    print("Test 6: Custom Role Constraints - Valid")
    print("=" * 70)
    
    df = load_players("players.csv")
    df_scored = calculate_score(df)
    
    # Test with valid custom constraints
    valid_constraints = [
        {"WK": 1, "BAT": 5, "BOWL": 2, "ALL": 3},
        {"WK": 2, "BAT": 3, "BOWL": 3, "ALL": 3},
        {"WK": 1, "BAT": 3, "BOWL": 4, "ALL": 3},
    ]
    
    for constraints in valid_constraints:
        try:
            validate_optimization_inputs(200, df_scored, constraints)
            print(f"✓ Valid constraints {constraints}: Passed")
        except ValidationError as e:
            print(f"✗ Unexpected error for {constraints}: {e}")


def test_budget_range_validation():
    """Test budget range validation"""
    print("\n" + "=" * 70)
    print("Test 7: Budget Range Validation")
    print("=" * 70)
    
    # Test valid range
    try:
        validate_budget_range(200, min_budget=1, max_budget=1000)
        print("✓ Budget $200 within range [1, 1000]")
    except ValidationError as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test below minimum
    try:
        validate_budget_range(0, min_budget=1, max_budget=1000)
        print("✗ Should have rejected budget below minimum")
    except ValidationError as e:
        print(f"✓ Correctly rejected budget below minimum: {e}")
    
    # Test above maximum
    try:
        validate_budget_range(2000, min_budget=1, max_budget=1000)
        print("✗ Should have rejected budget above maximum")
    except ValidationError as e:
        print(f"✓ Correctly rejected budget above maximum: {e}")


def test_dataframe_validation():
    """Test DataFrame validation"""
    print("\n" + "=" * 70)
    print("Test 8: DataFrame Validation")
    print("=" * 70)
    
    df = load_players("players.csv")
    df_scored = calculate_score(df)
    
    # Test valid DataFrame
    try:
        validate_dataframe(df_scored)
        print("✓ Valid DataFrame passed validation")
    except ValidationError as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test empty DataFrame
    try:
        empty_df = pd.DataFrame()
        validate_dataframe(empty_df)
        print("✗ Should have rejected empty DataFrame")
    except ValidationError as e:
        print(f"✓ Correctly rejected empty DataFrame: {e}")
    
    # Test DataFrame with missing columns
    try:
        incomplete_df = df_scored[['name', 'price']].copy()  # Missing role and score
        validate_dataframe(incomplete_df)
        print("✗ Should have rejected DataFrame with missing columns")
    except ValidationError as e:
        print(f"✓ Correctly rejected incomplete DataFrame: {e}")


def test_minimum_cost_calculation():
    """Test minimum cost calculation with actual data"""
    print("\n" + "=" * 70)
    print("Test 9: Minimum Cost Calculation")
    print("=" * 70)
    
    df = load_players("players.csv")
    df_scored = calculate_score(df)
    
    # Calculate minimum cost manually for verification
    role_constraints = {"WK": 1, "BAT": 4, "BOWL": 3, "ALL": 3}
    
    min_costs = {}
    total_min_cost = 0
    
    for role, count in role_constraints.items():
        role_players = df_scored[df_scored['role'] == role]
        cheapest = role_players.nsmallest(count, 'price')
        role_min_cost = cheapest['price'].sum()
        min_costs[role] = role_min_cost
        total_min_cost += role_min_cost
        
        print(f"  {role}: {count} players, minimum cost: ${role_min_cost:.2f}")
        for _, player in cheapest.iterrows():
            print(f"    - {player['name']}: ${player['price']:.2f}")
    
    print(f"\n  Total minimum cost: ${total_min_cost:.2f}")
    
    # Test with budget just below minimum
    try:
        validate_optimization_inputs(int(total_min_cost) - 1, df_scored)
        print(f"✗ Should have rejected budget ${int(total_min_cost) - 1}")
    except ValidationError as e:
        print(f"✓ Correctly rejected insufficient budget: {e}")
    
    # Test with budget at minimum
    try:
        validate_optimization_inputs(int(total_min_cost), df_scored)
        print(f"✓ Accepted budget ${int(total_min_cost)} (at minimum)")
    except ValidationError as e:
        print(f"Note: Budget at exact minimum: {e}")


if __name__ == "__main__":
    print("\n" + "█" * 70)
    print("VALIDATION LAYER TEST SUITE")
    print("█" * 70)
    
    test_valid_inputs()
    test_negative_budget()
    test_zero_budget()
    test_insufficient_budget()
    test_insufficient_players_per_role()
    test_custom_role_constraints()
    test_budget_range_validation()
    test_dataframe_validation()
    test_minimum_cost_calculation()
    
    print("\n" + "█" * 70)
    print("✓ ALL VALIDATION TESTS COMPLETE")
    print("█" * 70)
